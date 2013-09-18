import os, sqlite3, hashlib, atexit

_DATABASE=sqlite3.connect('data.sqlite')

def hashfile(filecontents):
	"""Save a string to a file and return the hash for lookup.
	The string can then be retrieved by gethash().
	TODO unit tests
	"""
	filehash=hashlib.sha256(filecontents).hexdigest() # pylint: disable-msg=E1101
	# save filecontents
	(hashfolder, hashfilename)=__hashpath(filehash)
	if not os.path.exists(hashfilename):
		if not os.path.exists(hashfolder): # Create parent directories, if needed
			os.makedirs(hashfolder)
		with open(hashfilename, 'w') as filehandle:
			filehandle.write(filecontents)
	
	return filehash

def gethash(filehash):
	"""Given a hash, returns the string which was saved by hashfile()
	TODO unit test
	"""
	with open(__hashpath(filehash)[1], 'r') as filehandle:
		return filehandle.read()

def __hashpath(filehash):
	"""Turn a hex digest into a folder and file path.
	>>> __hashpath('954e65600cf9ab574449316106c8df9ef12d09f1e4b525132c0a13d4e9ff8899')
	('data/95/4e/65/60', 'data/95/4e/65/60/954e65600cf9ab574449316106c8df9ef12d09f1e4b525132c0a13d4e9ff8899')
	"""
	hashfolder = "/".join([ 'data', filehash[0:2], filehash[2:4],
			filehash[4:6], filehash[6:8] ])
	return (hashfolder, hashfolder+"/"+filehash)

def getlatest(host, port, path):
	"""Get the latest archived version of a file.
	"""
	cursor = _DATABASE.cursor()
	cols=['host', 'port', 'dtype', 'path', 'state', 'timestamp', 'log', 'hash']
	cursor.execute("SELECT "+", ".join(cols)+
			" FROM latest WHERE host=? AND port=? AND path=?;",
			(host, port, path))
	data=cursor.fetchone()
	if data is None:
		return None
	result={}
	for i in range(len(cols)):
		result[cols[i]] = data[i]
	return result

def dbsave(host, port, dtype, path, state, timestamp, log, filehash,
		autocommit =True):
	"""Insert a row into the files table.
	autocommit should be set to false if a lot of rows are to be inserted at once.
	"""
	_DATABASE.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
			(host, port, dtype, path, state, int(timestamp),log, filehash))
	if autocommit :
		dbcommit()

def dbcommit():
	"""Commit the current database transaction.
	Called by dbclose() when the program exits.
	"""
	_DATABASE.commit()

@atexit.register
def dbclose():
	"""Commit changes to the database and close the connection.
	Called automatically when the program exits.
	"""
	dbcommit()
	_DATABASE.close()
