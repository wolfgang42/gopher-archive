import os, sqlite3, hashlib

db=sqlite3.connect('data.sqlite')

def hashFile(fileContents):
	fileHash=hashlib.sha256(fileContents).hexdigest()
	
	# save fileContents
	hashFolder="/".join([ 'data', fileHash[0:2], fileHash[2:4], fileHash[4:6], fileHash[6:8] ])
	hashFileName=hashFolder+"/"+fileHash
	if not os.path.exists(hashFileName):
		if not os.path.exists(hashFolder): # Create parent directories, if needed
			os.makedirs(hashFolder)
		with open(hashFileName, 'w') as f:
			f.write(fileContents)
	
	return fileHash;
