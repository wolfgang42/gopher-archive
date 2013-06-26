CREATE TABLE files (
	host TEXT,
	port INTEGER,
	dtype TEXT,
	path TEXT,
	state TEXT CHECK (state IN ('ErrorState','Excluded','NotVisited','Visited')),
	"timestamp" INTEGER,
	log TEXT,
	hash TEXT,
	PRIMARY KEY (host, port, path, "timestamp")
);

CREATE TABLE hosthits (
	host TEXT,
	port INTEGER,
	hit INTEGER, -- UNIX timestamp
	PRIMARY KEY (host, port)
);

-- See only the latest version of the files.
-- This is a read-only view.
CREATE VIEW latest AS
	SELECT * FROM files file
		WHERE "timestamp" = (
			SELECT MAX("timestamp") FROM files
				WHERE host = file.host AND port = file.port AND path = file.path
		);

