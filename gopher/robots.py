import robotparser, time
import client, archive

USER_AGENT="GopherArchive/0.0"

_cache = {}

def allowed(host, port, path):
	if path == "robots.txt": return True # Duh.
	# robotparser ignores the protocol and host components
	return _getrobots(host, port).can_fetch('fakegopher://host/'+path,USER_AGENT)

# Make sure we have a robots.txt
def _getrobots(host, port):
	key=host+":"+str(port)
	cache=None
	if _cache.has_key(key) and not _expired(_cache[key]['modified']):
		# Try to get it from the in-memory cache
		cache=_cache[key]
	if cache == None: # Nope, not in memory (or in-memory cache expired)
		cache={}
		data=None
		modified=None
		# try to get it from the database
		robots=archive.getlatest(host, port, "robots.txt")
		if robots is not None and not _expired(robots['timestamp']):
			data=archive.getHash(robots['hash'])
			modified=robots['timestamp']
		else: # We still don't have it!
			# Retrieve it from the host
			data=client.get(host, port, "robots.txt")
			modified=time.time()
		cache['parsed']=robotparser.RobotFileParser()
		cache['parsed'].parse(data)
		cache['modified']=modified
		_cache[key]=cache
		
	return cache['parsed']

def _expired(timestamp):
	return timestamp < time.time() - 60*60*24;
