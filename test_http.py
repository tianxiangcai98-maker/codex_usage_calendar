import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
import server

class LocalHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.port = cls.http.server_port
        cls.port_patch = patch.object(server, 'PORT', cls.port)
        cls.port_patch.start()
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()
        cls.port_patch.stop()

    def request(self, path, method='GET', headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        try:
            connection.request(method, path, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_public_assets_and_response_headers(self):
        for path in ('/', '/i18n.js', '/quota-model.js', '/assets/bell.svg', '/assets/info.circle.svg'):
            status, headers, body = self.request(path)
            self.assertEqual(status, 200)
            self.assertTrue(body)
            self.assertEqual(headers['Cache-Control'], 'no-store')
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
            self.assertEqual(headers['X-Frame-Options'], 'DENY')
            self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])

    def test_private_paths_are_not_served(self):
        for path in ('/data/usage.sqlite3', '/data/codex-home/auth.json', '/.git/config', '/preview-deploy.local.json', '/../README.md'):
            self.assertEqual(self.request(path)[0], 404)

    def test_cross_site_or_untrusted_host_is_rejected(self):
        self.assertEqual(self.request('/api/usage', headers={'Sec-Fetch-Site': 'cross-site'})[0], 403)
        self.assertEqual(self.request('/', headers={'Host': 'attacker.example'})[0], 403)

    def test_mutation_requires_matching_origin(self):
        with patch.object(server, 'login_cancel', return_value={'ok': True}) as cancel:
            self.assertEqual(self.request('/api/auth/cancel', 'POST')[0], 403)
            self.assertEqual(self.request('/api/auth/cancel', 'POST', {'Origin': 'https://attacker.example'})[0], 403)
            cancel.assert_not_called()
            self.assertEqual(self.request('/api/auth/cancel', 'POST', {'Origin': f'http://127.0.0.1:{self.port}'})[0], 200)
            cancel.assert_called_once()

    def test_account_identifiers_do_not_reach_browser(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(server, 'DB', Path(tmp)/'test.sqlite3'), patch.object(server, 'STATE', {**server.STATE, 'signedIn': False, 'account': 'fixture', 'loginId': 'fixture-id', 'loginUrl': 'https://auth.openai.com/authorize?state=fixture'}):
            status, _, raw = self.request('/api/usage')
            self.assertEqual(status, 200)
            body = json.loads(raw)
            for key in ('account', 'loginId', 'loginUrl'):
                self.assertNotIn(key, body)
            self.assertEqual(body['history'], [])

if __name__ == '__main__':
    unittest.main()
