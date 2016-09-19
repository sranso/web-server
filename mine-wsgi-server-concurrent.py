# Concurrent WSGI server
import socket
import signal
import sys
import os
import errno
import StringIO
from time import gmtime, strftime


class WSGIServer(object):

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1024

    def __init__(self, server_address):
        # create listening server socket
        self.listening_socket = listening_socket = socket.socket(
            self.address_family,
            self.socket_type
        )
        # allow address to be reused
        listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind to host and port
        listening_socket.bind(server_address)
        # start listening
        listening_socket.listen(self.request_queue_size)
        # get server host name & port
        host, port = listening_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # hold list of headers set by client
        self.headers_set = ()

    def set_app(self, app):
        self.application = app

    def grim_reaper(self, signum, frame):
        while True:
            try:
                pid, status = os.waitpid(
                    -1, # wait for any child ps
                    os.WNOHANG # do not block
                )
                print(
                    'Child {pid} terminated with status {status}'
                    '\n'.format(pid=pid, status=status)
                )
            except OSError:
                return

            if pid == 0: # zombies gone
                return

    def serve_forever(self):
        listening_socket = self.listening_socket

        signal.signal(signal.SIGCHLD, self.grim_reaper)

        while True:
            # create new client connection
            try:
                self.client_connection, client_address = listening_socket.accept()
            except IOError as e:
                code, msg = e.args
                # restart accept if interrupted
                if code == errno.EINTR:
                    continue
                else:
                    raise

            pid = os.fork()
            if pid == 0: # child
                # child doesn't need to listen, so close 
                listening_socket.close()
                # handle req then close client cnxn
                self.handle_one_request()
                os._exit(0)
            else: # parent
                # parent doesn't need this cnxn, so close
                self.client_connection.close()

    def handle_one_request(self):
        # grab req data
        self.request_data = request_data = self.client_connection.recv(1024)
        # print formatted req data
        print 'REQUEST:\n'
        print(''.join(
            '< {line}\n'.format(line=line)
            for line in request_data.splitlines()
        ))

        # parse req, save data on instance
        self.parse_request(request_data)

        # make WSGI env dict using req data
        env = self.get_environ()

        # call application callable and get back a result
        # that will become our HTTP response body
        result = self.application(env, self.start_response)

        # build and send response to client
        self.finish_response(result)

    def parse_request(self, text):
        request_first_line = text.splitlines()[0].rstrip('\r\n')
        (self.request_method,
         self.path,
         self.http_version
        ) = request_first_line.split()

    def get_environ(self):
        # format environment dictionary with WSGI/CGI variables
        env = {}
        # required WSGI vars
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = StringIO.StringIO(self.request_data)
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        # Required CGI variables
        env['REQUEST_METHOD']    = self.request_method    # GET
        env['PATH_INFO']         = self.path              # /hello
        env['SERVER_NAME']       = self.server_name       # localhost
        env['SERVER_PORT']       = str(self.server_port)  # 8888
        return env

    def start_response(self, status, response_headers, exec_info=None):
        # add necessary server headers
        server_headers = [
            ('Date', strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime())),
            ('Server', 'WSGIServer 0.2')
        ]
        # combine status header, server and client headers
        self.headers_set = (status, response_headers + server_headers)

    def finish_response(self, result):
        try:
            # format response with our headers
            #   status = string, response_headers = ()
            status, response_headers = self.headers_set
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            # add required empty line after rsp header
            response += '\r\n'
            # format response with our result aka rsp data/body
            for data in result:
                response += data
            # print formatted response data
            print 'RESPONSE:\n'
            print(''.join(
                '> {line}\n'.format(line=line)
                for line in response.splitlines()
            ))
            self.client_connection.sendall(response)
        finally:
            self.client_connection.close()

def make_server(server_address, application):
    s = WSGIServer(server_address)
    s.set_app(application)
    return s

SERVER_ADDRESS = (HOST, PORT) = '', 8888

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.serve_forever()
