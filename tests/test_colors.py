"""Run with: python tests/test_colors.py --theme-dir /path/to/firefox-gnome-theme."""

import argparse
import base64
from pathlib import Path
import time
import unittest

from browser import Firefox


ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--theme-dir', type=Path, required=True)
parser.add_argument('--firefox', default='firefox')
parser.add_argument('--screenshot', type=Path)
options, remaining = parser.parse_known_args()

PALETTE = {
    '--lwt-accent-color': '#131313', '--lwt-text-color': '#e2e2e2',
    '--toolbar-background-color': '#242424', '--toolbar-text-color': '#f1f1f1',
    '--toolbar-field-background-color': '#333333', '--toolbar-field-text-color': '#c2c2c2',
    '--panel-background-color': '#1f1f1f', '--panel-text-color': '#dadada',
    '--newtab-background-color-secondary': '#303030',
    '--tab-background-color-selected': '#424242', '--lwt-tab-line-color': '#ab2233',
    '--lwt-toolbar-field-highlight': '#55d6f4', '--tab-loading-fill': '#55d6f4',
    '--sidebar-background-color': '#292929', '--sidebar-text-color': '#eeeeee',
}


class ColorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser = Firefox(options.theme_dir.resolve(), ROOT / 'patch-gnome-firefox-theme', options.firefox)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()

    def setUp(self):
        self.browser.command('Marionette:SetContext', {'value': 'chrome'})
        self.browser.js('''
            const root = document.documentElement;
            root.removeAttribute('privatebrowsingmode');
            root.removeAttribute('lwtheme');
            root.removeAttribute('style');
        ''')

    def palette(self, colors=None):
        self.browser.js('''
            const root = document.documentElement;
            root.setAttribute('lwtheme', 'true');
            for (const [k,v] of Object.entries(arguments[0])) root.style.setProperty(k,v);
        ''', [PALETTE if colors is None else colors])
        # Let the theme's background/color transitions finish before sampling pixels.
        time.sleep(.3)

    def token(self, name, selector=':root'):
        return self.browser.js('return getComputedStyle(document.querySelector(arguments[1])).getPropertyValue(arguments[0]).trim();', [name, selector])

    def color(self, selector, prop):
        return self.browser.js('return getComputedStyle(document.querySelector(arguments[0]))[arguments[1]];', [selector, prop])

    def test_current_firefox_roles_and_cycles(self):
        self.palette()
        expected = {
            '--gnome-accent-bg': '#55d6f4',
            '--gnome-entry-color': '#c2c2c2',
            '--gnome-entry-background': '#333333',
            '--gnome-menu-background': '#1f1f1f',
            '--gnome-menu-color': '#dadada',
            '--gnome-card-background': '#303030',
            '--gnome-tabbar-tab-active-background': '#ab2233',
            '--gnome-tabbar-tab-needs-attetion': '#55d6f4',
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(self.token(name), value)
        self.assertTrue(self.token('--gnome-selection-bg'))
        self.assertTrue(self.token('--lwt-toolbar-field-highlight'))
        self.assertEqual(self.token('--panel-background-color', '#appMenu-popup'), '#1f1f1f')
        self.assertEqual(self.color('#urlbar-input', 'color'), 'rgb(194, 194, 194)')
        self.assertEqual(self.color('#TabsToolbar', 'backgroundColor'), 'rgb(19, 19, 19)')

    def test_legacy_firefox_names(self):
        self.palette({
            '--lwt-accent-color': '#121212', '--lwt-text-color': '#eeeeee',
            '--toolbar-bgcolor': '#303030', '--toolbar-field-color': '#dddddd',
            '--arrowpanel-background': '#404040', '--arrowpanel-color': '#cccccc',
            '--lwt-tab-loading-fill': '#ddaa33',
        })
        self.assertEqual(self.token('--gnome-entry-color'), '#dddddd')
        self.browser.js('document.documentElement.style.setProperty("--tab-loading-fill", "initial", "important");')
        self.assertEqual(self.token('--gnome-accent-bg'), '#ddaa33')
        # Current Firefox defines default modern panel tokens. Remove those
        # explicitly to exercise the legacy fallback path.
        self.browser.js('document.documentElement.style.setProperty("--panel-background-color", "initial", "important"); document.documentElement.style.setProperty("--panel-text-color", "initial", "important");')
        self.assertEqual(self.token('--gnome-menu-background'), '#404040')
        self.assertEqual(self.token('--gnome-menu-color'), '#cccccc')

    def test_palette_updates_without_restart(self):
        self.palette()
        self.palette({**PALETTE, '--panel-background-color': '#293b4d', '--toolbar-field-text-color': '#fafafa', '--tab-loading-fill': '#ff8844'})
        self.assertEqual(self.token('--gnome-menu-background'), '#293b4d')
        self.assertEqual(self.token('--gnome-entry-color'), '#fafafa')
        self.assertEqual(self.token('--gnome-accent-bg'), '#ff8844')

    def test_private_window_tokens(self):
        self.palette()
        self.browser.js('document.documentElement.setAttribute("privatebrowsingmode", "temporary");')
        self.assertEqual(self.token('--gnome-headerbar-background'), '#131313')
        self.assertEqual(self.token('--gnome-menu-background'), '#1f1f1f')
        self.assertEqual(self.token('--gnome-entry-color'), '#c2c2c2')

    def test_no_extension_leaves_gnome_colors_valid(self):
        for name in ['--gnome-headerbar-background', '--gnome-entry-color', '--gnome-accent-bg', '--gnome-menu-background', '--gnome-card-background']:
            with self.subTest(name=name):
                self.assertTrue(self.token(name))

    def test_newtab_colors_and_ordinary_pages(self):
        self.browser.command('Marionette:SetContext', {'value': 'content'})
        try:
            self.browser.command('WebDriver:Navigate', {'url': 'about:newtab'})
            self.browser.js('''
                const root = document.documentElement;
                root.setAttribute('lwt-newtab', 'true');
                for (const [k,v] of Object.entries(arguments[0])) root.style.setProperty(k,v);
            ''', [{'--newtab-background-color': '#131313', '--newtab-background-color-secondary': '#1f1f1f', '--newtab-text-primary-color': '#e2e2e2'}])
            self.assertEqual(self.token('--gnome-window-background'), '#131313')
            self.assertEqual(self.token('--gnome-card-background'), '#1f1f1f')
            self.assertEqual(self.color('body', 'backgroundColor'), 'rgb(19, 19, 19)')
            self.assertEqual(self.token('--newtab-background-color-secondary', 'body'), '#1f1f1f')
            self.browser.command('WebDriver:Navigate', {'url': 'data:text/html,<body style="background:rgb(1,2,3);color:rgb(4,5,6)">Ordinary page</body>'})
            self.assertEqual(self.color('body', 'backgroundColor'), 'rgb(1, 2, 3)')
            self.assertEqual(self.color('body', 'color'), 'rgb(4, 5, 6)')
            self.assertEqual(self.token('--pywalfox-menu-color'), '')
        finally:
            self.browser.command('Marionette:SetContext', {'value': 'chrome'})

    def test_screenshot(self):
        if not options.screenshot:
            self.skipTest('No screenshot requested')
        self.palette()
        result = self.browser.command('WebDriver:TakeScreenshot', {'id': None, 'full': False, 'scroll': False})
        options.screenshot.write_bytes(base64.b64decode(result['value']))


if __name__ == '__main__':
    unittest.main(argv=[__file__, *remaining])
