import socket

HOST, PORT = '', 8888

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)

print('Serving HTTP on port %s...', PORT)

while True:
    client_connection, client_address = listen_socket.accept()
    print('CLIENT CXN & ADDRESS\n', client_connection, '\n', client_address, '\n')
    request = client_connection.recv(1024)
    print('REQUEST\n', request, '\n')
    http_response = """\
HTTP/1.1 200 OK

Hello, world!
"""
    client_connection.sendall(http_response)
    client_connection.close()

