import archive, robots
import socket

TIMEOUT = 10 # Timeout to use for sockets

def get(host, port=70, selector="", query=None):
	# Arguments
	if query is None:
		path = selector
	else:
		path = selector + "\t" + query
	# Retrieve
	log=""; document=""
	try:
		document = _get(host, port, path)
		state="Visited"
	except socket.error, e:
		state="ErrorState"
		log=e[1] # Error message (e[0] is error number)
	# Cache
	_cache(host, port, path, state, document)
	# Return
	if state=="ErrorState": raise IOException(log)
	return document # TODO raise exception instead?

def _cache(host, port, path, state, result):
	if not robots.allowed(host, port, path):
		state = "Excluded"
	if state == "Visited":
		resultHash = archive.hashFile(result)
	else: # ErrorState or Excluded, don't save data
		resultHash = ""
	# TODO save to db

def _get(host, port, path):
	# Connect
	s = socket.create_connection((host, port), TIMEOUT)
	# Send
	s.sendall(path)
	s.sendall("\r\n");
	# Receive
	document=""
	data=True
	while data:
		data=s.recv(4096)
		document += data
	# Close
	s.close()
	# Return
	return document
