import socket

# '' means the socket is reachable by any address the machine happens to have
HOST, PORT = '', 8888

# create an INET (address family), STREAMing (socket type) socket
listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# add to avoid error 'Address already in use.' reason this works: previous execution
# left socket in TIME_WAIT state and can't be immediately reused
listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind socket to public host and known port
listening_socket.bind((HOST, PORT))
# become a server socket, queue up as many as 1 connect requests before refusing
listening_socket.listen(1)

print 'Serving HTTP on port %s...' % PORT

# mainloop of the web server
while True:
    # accept connections from the outside, that we listened for above
    #   client_socket is a socket object
    #   client_address is a tuple! (<host>, <port>)
    # server is PRODUCING client sockets here! this is all a server socket does!
    #   creating sockets in response to some client socket doing a connect() to the host
    #   and port this server socket is bound to
    client_socket, client_address = listening_socket.accept()
    # grab request - 1024 is the buffer size of the req data that we want
    #   buffer size should be small-ish power of 2
    # notes on send and recv
    #   - operate on the network buffers
    #   - they return when the associated network buffers have been filled (send)
    #     or emptied (recv). then they tell how you many bytes they handled
    request = client_socket.recv(1024)
    print request

    http_response = """\

HTTP/1.1 200 OK

Hello, world!
"""
    # send data to client socket
    client_socket.sendall(http_response)
    # close / discard connection
    client_socket.close()

