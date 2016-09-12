def app(environ, start_response):
    """A barebones WSGI app.

    This is a starting point for your own Web framework ;)
    """
    print('environ!\n', environ)
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world from a simple WSGI app!\n']
