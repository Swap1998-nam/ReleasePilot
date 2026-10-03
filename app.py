import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def assess(d):
    required = {'tests_passed': bool, 'coverage': int, 'critical_vulnerabilities': int,
                'high_vulnerabilities': int, 'image_signed': bool, 'rollback_ready': bool, 'replicas': int}
    if not isinstance(d, dict) or set(d) != set(required):
        raise ValueError('Provide all seven release signals and no other fields')
    for key, kind in required.items():
        if type(d[key]) is not kind:
            raise ValueError(f'{key} must be {kind.__name__}')
    if not 0 <= d['coverage'] <= 100 or any(d[k] < 0 for k in ('critical_vulnerabilities', 'high_vulnerabilities', 'replicas')):
        raise ValueError('Coverage must be 0–100; counts must be nonnegative')
    checks = [(not d['tests_passed'], 35, 'Tests failed'),
              (d['coverage'] < 80, 15, 'Coverage below 80%'),
              (d['critical_vulnerabilities'] > 0, 45, 'Critical vulnerabilities'),
              (d['high_vulnerabilities'] > 0, 15, 'High vulnerabilities'),
              (not d['image_signed'], 10, 'Unsigned image'),
              (not d['rollback_ready'], 15, 'No rollback plan'),
              (d['replicas'] < 2, 10, 'Fewer than two replicas')]
    score = max(0, 100 - sum(p for failed, p, _ in checks if failed))
    blocked = not d['tests_passed'] or d['critical_vulnerabilities'] > 0
    return {'score': score, 'verdict': 'BLOCKED' if blocked else 'READY' if score >= 80 else 'REVIEW',
            'findings': [label for failed, _, label in checks if failed]}


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, payload, mime='application/json'):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/':
            return self.reply(200, Path(__file__).with_name('index.html').read_bytes(), 'text/html; charset=utf-8')
        if self.path in ('/health/live', '/health/ready'):
            return self.reply(200, {'status': 'ok'})
        if self.path == '/metrics':
            return self.reply(200, b'releasepilot_up 1\n', 'text/plain; version=0.0.4')
        self.reply(404, {'error': 'Not found'})

    def do_POST(self):
        if self.path != '/api/assess':
            return self.reply(404, {'error': 'Not found'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 8192:
                return self.reply(413, {'error': 'Invalid request size'})
            return self.reply(200, assess(json.loads(self.rfile.read(size))))
        except (ValueError, UnicodeDecodeError) as exc:
            self.reply(400, {'error': str(exc)})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', int(os.getenv('PORT', '8081'))), Handler).serve_forever()
