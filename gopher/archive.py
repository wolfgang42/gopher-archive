import os, sqlite3, hashlib

_db=sqlite3.connect('data.sqlite')

def hashFile(fileContents):
	fileHash=hashlib.sha256(fileContents).hexdigest()
	
	# save fileContents
	(hashFolder,hashFileName)=_hashPath(fileHash)
	if not os.path.exists(hashFileName):
		if not os.path.exists(hashFolder): # Create parent directories, if needed
			os.makedirs(hashFolder)
		with open(hashFileName, 'w') as f:
			f.write(fileContents)
	
	return fileHash;

def getHash(fileHash):
	with open(_hashPath(fileHash)[1], 'r') as f:
		return f.read()

def _hashPath(fileHash):
	hashFolder = "/".join([ 'data', fileHash[0:2], fileHash[2:4], fileHash[4:6], fileHash[6:8] ])
	return (hashFolder, hashFolder+"/"+fileHash)

def getlatest(host, port, path):
	c = _db.cursor()
	cols=['host', 'port', 'dtype', 'path', 'state', 'timestamp', 'log', 'hash']
	c.execute("SELECT "+", ".join(cols)+
			" FROM latest WHERE host=? AND port=? AND path=?;",(host, port, path))
	data=c.fetchone()
	if data is None:
		return None
	result={}
	for i in range(len(cols)):
		result[cols[i]] = data[i]
	return result

# Insert a row into the files table.
# autoCommit should be set to false if a lot of rows are to be inserted at once.
def dbsave(host, port, dtype, path, state, timestamp, log, fileHash, autoCommit=True):
	_db.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?);", (host, port, dtype, path, state, int(timestamp), log, fileHash))
	if autoCommit:
		dbcommit()

def dbcommit():
	_db.commit()
