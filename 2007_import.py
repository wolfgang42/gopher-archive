#!/usr/bin/python
# Import the 2007 gopher dump into the archive

# This reads gopher-arch.tar.bz2 and gopher-arch-sqldump.bz2 directly, so they
# don't need to be extracted first.

# Generally, reading an SQL dump directly is a poor idea, but this one will
# never change, so we don't need to worry about that.

import tarfile, bz2
import gopher.archive

def main():
	tar=tarfile.open('gopher-arch.tar.bz2')
	sql=bz2.BZ2File('gopher-arch-sqldump.bz2')

	# Seek to beginning of list
	while True:
		if sql.readline().startswith("COPY files"): break

	count=0
	while True:
		line=sql.readline()
		if sql.readline().startswith("\."): break # End of list
	
		(host, port, dtype, path, state, timestamp, log) = line.split("\t")
	
		# Create a path and make it conform to UNIX path format
		tarpath = "/".join([host,port,path])
		if tarpath.endswith("/"): tarpath += '.gophermap'
		tarpath=tarpath.replace('/../','/')
		tarpath=tarpath.replace('//','/')
	
		try: # Get the file and save it as an object
			fileHash=gopher.archive.hashFile(tar.getmember(tarpath).tobuf())
		except KeyError:
			fileHash = "" # No object
	
		gopher.archive.dbsave(host, port, dtype, path, state, timestamp, log, fileHash)
	
		count += 1
		print count, "files imported...\r",

	print "Committing database...\r",
	gopher.archive.dbcommit()
	print "Import complete.", count, "files imported."

if __name__ == "__main__":
	main()

