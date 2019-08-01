from http.server import BaseHTTPRequestHandler, HTTPServer
from config import settings
import json, logging, time
from db import db, Event
from pony.orm import *


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        with db_session:
            events = Event.select()
            response = ""
            for event in events:
                response = response + "{} {} {} {}".format(event.event, event.repo, event.branch, event.time)
            self._set_response()
            self.wfile.write(bytes(response, "utf-8"))

    def do_POST(self):
        if self.path.startswith('/handler'):
            event = self.headers.get('X-GitHub-Event')
            ts = time.time()
            content_len = int(self.headers.get('Content-Length'))
            data = json.loads(self.rfile.read(content_len))
            with db_session:
                Event(event=event, repo=data['repository']['full_name'], branch=data['ref'])
            self._set_response()
            self.wfile.write(bytes("ok", "utf-8"))


def run_http_server(server_class=HTTPServer, handler_class=S, port=settings['http_server_port']):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    db.bind(**settings['db'])
    db.generate_mapping(create_tables=True)
    run_http_server()
