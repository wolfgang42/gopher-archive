# gopher.client Unit Tests ##
<!-- Imports needed for testing, but aren't part of the documentation.
	>>> import gopher.client  as client
	>>> import gopher.archive as archive
	>>> import gopher.robots  as robots
	>>> import socket, hashlib
	>>> import minimock # -->

## gopher.client.get ##

	>>> minimock.mock('client.__cache')

Normally, `gopher.client.get` should simply return the document from the server,
then cache it in the database.

	>>> minimock.mock('client.__get',returns='This is an example text document.',tracker=None)
	>>> client.get('gopher.floodgap.com',70,'/example')
	Called client.__cache(
	    'gopher.floodgap.com',
	    70,
	    '/example',
	    'Visited',
	    '',
	    'This is an example text document.')
	'This is an example text document.'

If something goes wrong with the retrieval, however, it should save it to the
database with no `document`, and a `state` of `'ErrorState'`, then raise an
`IOError` with the message that the socket returned.

	>>> minimock.mock('client.__get',raises=socket.error(-1,"socket.error message"),tracker=None)
	>>> try:
	... 	client.get('gopher.floodgap.com',70,'/example')
	... except IOError, e:
	... 	print "Test caught IOError:", e
	Called client.__cache(
	    'gopher.floodgap.com',
	    70,
	    '/example',
	    'ErrorState',
	    'socket.error message',
	    '')
	Test caught IOError: socket.error message

<!--
	>>> minimock.restore() #-->

## gopher.client.__cache ##

<!--
	>>> minimock.mock('archive.dbsave')
	>>> minimock.mock('archive.hashfile',
	... 	returns_func=lambda filecontents: hashlib.sha256(filecontents).hexdigest()) #-->

If robots.txt allows this document, its hash should be computed and saved to the
database:

	>>> minimock.mock('robots.allowed',returns=True,tracker=None)
	>>> client.__cache('gopher.floodgap.com', 70, '/example', 'Visited', '',
	... 'This is an example text document.') # doctest: +ELLIPSIS
	Called archive.hashfile('This is an example text document.')
	Called archive.dbsave(
	    'gopher.floodgap.com',
	    70,
	    '',
	    '/example',
	    'Visited',
	    ...,
	    '',
	    '2f8f8282c6cc13fa6daa3e45c9c8dacc83b4ae298b30386ea3e6314d31fc98c7')

If it's not allowed according to robots.txt, it saves saves with a `state` of
`Excluded` and a blank `hash`.

	>>> minimock.mock('robots.allowed',returns=False,tracker=None)
	>>> client.__cache('gopher.floodgap.com', 70, '/example', 'Visited', '',
	... 'This is an example text document.') # doctest: +ELLIPSIS
	Called archive.dbsave(
	    'gopher.floodgap.com',
	    70,
	    '',
	    '/example',
	    'Excluded',
	    ...,
	    '',
	    '')


If there was an error, that should be noted, and robots.txt shouldn't even be
checked:

	>>> minimock.mock('robots.allowed')   # Shouldn't be called
	>>> client.__cache('gopher.floodgap.com', 70, '/example', 'ErrorState',
	... 'socket.error message', '') # doctest: +ELLIPSIS
	Called archive.dbsave(
	    'gopher.floodgap.com',
	    70,
	    '',
	    '/example',
	    'ErrorState',
	    ...,
	    'socket.error message',
	    '')

<!--
	>>> minimock.restore() #-->

## gopher.client.__get ##
This one is quite simple. It should open a connection to the server, send
the selector, get back the entirety of the document, and finally close the
connection.

	>>> minimock.mock('socket.create_connection',returns=minimock.Mock('socket.socket'))
	>>> client.__get('gopher.floodgap.com',70,'/example')
	Called socket.create_connection(('gopher.floodgap.com', 70), 10)
	Called socket.socket.sendall('/example')
	Called socket.socket.sendall('\r\n')
	Called socket.socket.recv(4096)
	Called socket.socket.close()
	''

<!--
	>>> minimock.restore() #-->

## TODO test everything working together as a whole
