# Unit testing
if __name__ == "__main__":
	import doctest
	import gopher.client, gopher.robots, gopher.archive
	doctest.testmod(gopher.client)
	doctest.testfile('client.test.md')
	doctest.testmod(gopher.robots)
	doctest.testmod(gopher.archive)
