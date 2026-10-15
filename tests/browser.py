"""Minimal Marionette client for testing in disposable Firefox profiles."""

import json
from pathlib import Path
import socket
import shutil
import subprocess
import tempfile
import time


class Firefox:
    def __init__(self, theme, patcher=None, binary='firefox'):
        self.temp = tempfile.TemporaryDirectory(prefix='browser-probe-')
        self.profile = Path(self.temp.name)
        self.theme = self.profile / 'chrome' / 'firefox-gnome-theme'
        shutil.copytree(theme, self.theme, ignore=shutil.ignore_patterns('.git'))
        if patcher:
            subprocess.run([str(patcher), str(self.theme)], check=True)
        for kind in ('Chrome', 'Content'):
            (self.profile / 'chrome' / f'user{kind}.css').write_text(f'@import "firefox-gnome-theme/user{kind}.css";\n')
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
        prefs = {'toolkit.legacyUserProfileCustomizations.stylesheets': True,
                 'marionette.port': port, 'marionette.enabled': True,
                 'browser.shell.checkDefaultBrowser': False,
                 'browser.startup.homepage_override.mstone': 'ignore',
                 'browser.startup.page': 0, 'browser.startup.homepage': 'about:blank',
                 'datareporting.policy.dataSubmissionEnabled': False,
                 'browser.newtabpage.activity-stream.feeds.telemetry': False,
                 'browser.newtabpage.activity-stream.feeds.snippets': False}
        (self.profile / 'user.js').write_text(''.join(f'user_pref({json.dumps(k)}, {json.dumps(v)});\n' for k,v in prefs.items()))
        self.log = open(self.profile / 'firefox.log', 'w+')
        self.proc = subprocess.Popen([binary, '--headless', '--no-remote', '--marionette', '--remote-allow-system-access', '--profile', str(self.profile), 'about:blank'], stdout=self.log, stderr=self.log)
        for _ in range(150):
            try:
                self.sock = socket.create_connection(('127.0.0.1', port), timeout=1)
                self.sock.settimeout(20)
                break
            except OSError:
                if self.proc.poll() is not None:
                    self.log.seek(0)
                    message = self.log.read()
                    self.close()
                    raise RuntimeError(message)
                time.sleep(.1)
        else:
            self.close()
            raise TimeoutError('Firefox did not start Marionette')
        self.seq = 0
        try:
            self.receive()
            self.command('WebDriver:NewSession', {'capabilities': {'alwaysMatch': {'acceptInsecureCerts': True}}})
            self.command('Marionette:SetContext', {'value': 'chrome'})
        except Exception:
            self.close()
            raise

    def receive(self):
        n = b''
        while True:
            c = self.sock.recv(1)
            if not c:
                raise ConnectionError('Firefox disconnected')
            if c == b':':
                break
            n += c
        data = b''
        length = int(n)
        while len(data) < length:
            chunk = self.sock.recv(length - len(data))
            if not chunk:
                raise ConnectionError('Firefox disconnected during a response')
            data += chunk
        return json.loads(data)

    def command(self, name, args):
        self.seq += 1
        payload = json.dumps([0, self.seq, name, args]).encode()
        self.sock.sendall(str(len(payload)).encode() + b':' + payload)
        response = self.receive()
        if response[2]:
            raise RuntimeError(response[2])
        return response[3]

    def js(self, script, args=None):
        return self.command('WebDriver:ExecuteScript', {'script': script, 'args': args or [], 'newSandbox': True, 'sandbox': 'system'})['value']

    def close(self):
        if hasattr(self, 'sock'):
            self.sock.close()
        if hasattr(self, 'proc'):
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        self.log.close()
        self.temp.cleanup()
