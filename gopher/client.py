import archive, robots
import socket, time

TIMEOUT = 10 # Timeout to use for sockets

def get(host, port=70, selector="", query=None):
	"""Retrieve a document from a gopher server, cache it, and return it."""
	# Arguments
	if query is None:
		path = selector
	else:
		path = selector + "\t" + query
	# Retrieve
	log = ""
	document = ""
	try:
		document = __get(host, port, path)
		state="Visited"
	except socket.error, err:
		state="ErrorState"
		log=err[1] # Error message (e[0] is error number)
	# Cache
	__cache(host, port, path, state, log, document)
	# Return
	if state=="ErrorState":
		raise IOError(log)
	return document

def parsemenu(menu):
	"""Parses a menu into its component lines. This is an iterator.
	
	>>> for i in parsemenu('iWelcome to Floodgap Systems\\' official gopher server.\\t\\terror.host\\t1\\r\\n1Getting started with gopher, software, more\\t/gopher\\tgopher.floodgap.com\\t70\\r\\n0United States Geological Survey earthquake list\\t/quakes\\tgopher.floodgap.com\\t70\\r\\n.\\r\\n'): print i
	{'title': "Welcome to Floodgap Systems' official gopher server.", 'type': 'i', 'selector': '', 'host': 'error.host', 'remainder': '', 'port': '1'}
	{'title': 'Getting started with gopher, software, more', 'type': '1', 'selector': '/gopher', 'host': 'gopher.floodgap.com', 'remainder': '', 'port': '70'}
	{'title': 'United States Geological Survey earthquake list', 'type': '0', 'selector': '/quakes', 'host': 'gopher.floodgap.com', 'remainder': '', 'port': '70'}
	{'title': '.', 'type': 'i', 'selector': '', 'host': '', 'remainder': '', 'port': ''}
	"""
	(dot, menu)=normalizetext(menu)
	for line in menu.split("\n"):
		yield parsemenuitem(line)
	if (dot):
		# yield an item for the dot, so it can be displayed as suggested
		yield parsemenuitem('i.\t\t\t')

def normalizenewlines(string):
	"""# Convert all newlines to \\n
	
	>>> normalizenewlines("Foo\\nBar\\rBaz\\r\\nBak\\n")
	'Foo\\nBar\\nBaz\\nBak\\n'
	"""
	return string.replace("\r\n","\n").replace("\r","\n")

def normalizetext(text):
	"""Returns a tuple (dot, text)
	dot:  Whether the text ended with a dot
	text: The text, sans dot (if it was there to begin with), and with all newlines
	      normalized to \\n
	
	>>> normalizetext('iThis is a simple menu with one item.\\t\\terror.host\\t1\\r\\n.\\r\\n')
	(True, 'iThis is a simple menu with one item.\\t\\terror.host\\t1')
	
	>>> normalizetext('iThis is a simple menu with one item and no dot.\\t\\terror.host\\t1\\n')
	(False, 'iThis is a simple menu with one item and no dot.\\t\\terror.host\\t1')
	"""
	text=normalizenewlines(text)
	if text.endswith("\n.\n"):
		return (True,  text[:-3])
	elif text.endswith("\n."):
		return (True,  text[:-2])
	elif text.endswith("\n"):
		return (False, text[:-1])
	else:
		return (False, text)

def parsemenuitem(line):
	"""Given a line from a gopher menu, splits it into its component pieces,
	saving them to an associative array.
	
	>>> parsemenuitem('1Weather maps and forecasts via Floodgap Groundhog\\t/groundhog\\tgopher.floodgap.com\\t70')
	{'title': 'Weather maps and forecasts via Floodgap Groundhog', 'type': '1', 'selector': '/groundhog', 'host': 'gopher.floodgap.com', 'remainder': '', 'port': '70'}
	"""
	split=line.split("\t")
	item={}
	item['type']      = split[0][0]
	item['title']     = split[0][1:]
	item['selector']  = split[1]
	item['host']      = split[2]
	item['port']      = split[3]
	item['remainder'] = "\t".join(split[4:]) # Everything else, for e.g. Gopher+
	return item

def __cache(host, port, path, state, log, result):
	"""Save a result to the database, including the actual document, if allowed.
	"""
	if state == "Visited" and not robots.allowed(host, port, path):
		state = "Excluded"
	if state == "Visited":
		resulthash = archive.hashfile(result)
	else: # ErrorState or Excluded, don't save data
		resulthash = ""
	archive.dbsave(host, port, "", path, state, time.time(), log, resulthash)

def __get(host, port, path):
	"""Actually connects to the server and makes the request.
	"""
	# Connect
	sock = socket.create_connection((host, port), TIMEOUT)
	# Send
	sock.sendall(path)
	sock.sendall("\r\n")
	# Receive
	document=""
	data=True
	while data:
		data=sock.recv(4096)
		if data:
			document += data
	# Close
	sock.close()
	# Return
	return document
