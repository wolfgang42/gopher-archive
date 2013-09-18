import robotparser, time
import client, archive

USER_AGENT="GopherArchive/0.0"

_CACHE = {}

def allowed(host, port, path):
	"""Find out if a particular path should be archived.
	TODO unit tests
	"""
	if path == "robots.txt":
		return True # Duh.
	# robotparser ignores the protocol and host components
	return __getrobots(host, port).can_fetch('fakegopher://host/'+path, USER_AGENT)

# Make sure we have a robots.txt
def __getrobots(host, port):
	"""Get a RobotFileParser object for a particular server.
	First it checks for an up-to-date and already parsed version in __CACHE. If
	that doesn't exist it tries to get a copy from the database, and if *that*
	doesn't exist or is out of date it gets a copy from the server and parses
	it.
	TODO unit tests
	"""
	key=host+":"+str(port)
	cache=None
	if _CACHE.has_key(key) and not __expired(_CACHE[key]['modified']):
		# Try to get it from the in-memory cache
		cache=_CACHE[key]
	if cache == None: # Nope, not in memory (or in-memory cache expired)
		cache={}
		data=None
		modified=None
		# try to get it from the database
		robots=archive.getlatest(host, port, "robots.txt")
		if robots is not None and not __expired(robots['timestamp']):
			data=archive.gethash(robots['hash'])
			modified=robots['timestamp']
		else: # We still don't have it!
			# Retrieve it from the host
			data=client.get(host, port, '0', "robots.txt")
			modified=time.time()
		cache['parsed']=robotparser.RobotFileParser()
		cache['parsed'].parse(data)
		cache['modified']=modified
		_CACHE[key]=cache
		
	return cache['parsed']

def __expired(timestamp):
	"""Find out if a timestamp is more than a day out of date.
	TODO unit tests
	"""
	return timestamp < time.time() - 60*60*24

