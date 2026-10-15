"""Offline patch/install/remove regression tests; no browser or root needed."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
IMPORT = '@import "theme/colors/pywalfox.css";\n'


class PatcherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gnome-pywalfox-')
        self.theme = Path(self.temp.name) / 'theme with spaces'
        (self.theme / 'theme/colors').mkdir(parents=True)
        (self.theme / 'userChrome.css').write_text('@import "customChrome.css"; /**/\n')
        (self.theme / 'userContent.css').write_text('@import "customContent.css"; /**/\n')
        (self.theme / 'theme/gnome-theme.css').write_text('/* Theme */\n')

    def tearDown(self):
        self.temp.cleanup()

    def run_patch(self, *args, source=None):
        env = dict(os.environ)
        env.pop('GNOME_PYWALFOX_CSS_SOURCE', None)
        if source:
            env['GNOME_PYWALFOX_CSS_SOURCE'] = str(source)
        return subprocess.run([str(ROOT / 'patch-gnome-firefox-theme'), *args, str(self.theme)], env=env, capture_output=True, text=True)

    def snapshot(self):
        return {str(p.relative_to(self.theme)): p.read_bytes() for p in self.theme.rglob('*') if p.is_file()}

    def test_install_and_repeat_are_identical(self):
        custom = self.theme / 'customChrome.css'
        custom.write_text('@charset "UTF-8";\n/* Keep my settings */\n:root { --mine: blue; }\n')
        self.assertEqual(self.run_patch().returncode, 0)
        before = self.snapshot()
        for _ in range(3):
            self.assertEqual(self.run_patch().returncode, 0)
            self.assertEqual(self.snapshot(), before)
        self.assertTrue(custom.read_text().startswith('@charset "UTF-8";\n' + IMPORT))
        self.assertEqual((self.theme / 'theme/colors/pywalfox.css').read_bytes(), (ROOT / 'pywalfox-colors.css').read_bytes())

    def test_remove_restores_existing_custom_files(self):
        original = '@charset "UTF-8";\n/* Custom */\n:root { color: red; }\n'
        for name in ['customChrome.css', 'customContent.css']:
            (self.theme / name).write_text(original)
        before = self.snapshot()
        self.assertEqual(self.run_patch().returncode, 0)
        self.assertEqual(self.run_patch('--remove').returncode, 0)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.run_patch('--remove').returncode, 0)

    def test_legacy_imports(self):
        (self.theme / 'userChrome.css').write_text('/* Legacy */\n')
        (self.theme / 'theme/gnome-theme.css').write_text('@import "extensions/adaptive-tab-bar-colour.css" screen and -moz-pref("gnomeTheme.extensions.adaptiveTabBarColour");\n')
        (self.theme / 'userContent.css').write_text('@import "theme/pages/privatebrowsing.css";\n')
        before = self.snapshot()
        self.assertEqual(self.run_patch().returncode, 0)
        self.assertIn('@import "colors/pywalfox.css";', (self.theme / 'theme/gnome-theme.css').read_text())
        self.assertEqual(self.run_patch('--remove').returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_missing_source_does_not_change_theme(self):
        before = self.snapshot()
        result = self.run_patch(source=self.theme / 'missing.css')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_unknown_layout_does_not_change_theme(self):
        (self.theme / 'userChrome.css').write_text('/* No supported import */\n')
        before = self.snapshot()
        self.assertEqual(self.run_patch().returncode, 42)
        self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
