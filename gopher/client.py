import archive, robots, time
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
	_cache(host, port, path, state, log, document)
	# Return
	if state=="ErrorState": raise IOError(log)
	return document # TODO raise exception instead?

def parsemenu(menu):
	(dot,menu)=_normalizemenu(menu)
	for line in menu.split("\n"):
		yield parsemenuitem(line)
	if (dot):
		# yield an item for the dot, so it can be displayed as suggested
		yield parsemenuitem('i.\t\t\t')

# Convert all newlines to \n
def normalizenewlines(string):
	return string.replace("\r\n","\n").replace("\r","\n")

# Returns a tuple (dot, menu)
# dot:  Whether the menu ended with a dot
# menu: The menu, sans dot (if it was there to begin with), and with all newlines
#       normalized to \n
def normalizemenu(menu):
	menu=_normalizenewlines(menu)
	if menu.endswith("\n."):
		return (True,  menu[:-2])
	elif menu.endswith("\n.\n"):
		return (True,  menu[:-3])
	else:
		return (False, menu)

def parsemenuitem(line):
	split=line.split("\t")
	item={}
	item['type']      = split[0][0]
	item['title']     = split[0][1:]
	item['selector']  = split[1]
	item['host']      = split[2]
	item['port']      = split[3]
	item['remainder'] = split[4:] # Everything else, just in case (e.g. Gopher+)
	return item

def _cache(host, port, path, state, log, result):
	if state == "Visited" and not robots.allowed(host, port, path):
			state = "Excluded"
	if state == "Visited":
		resultHash = archive.hashFile(result)
	else: # ErrorState or Excluded, don't save data
		resultHash = ""
	archive.dbsave(host, port, "", path, state, time.time(), log, resultHash)

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
