Express/React frontend for Maniwani
===================================


Building
--------

The frontend builds with Docker, so the following should work:

	docker build -t maniwani-frontend .
	

Running
-------

The frontend currently takes no options, so running it should be as simple as:

	docker run -p 3000:3000 maniwani-frontend
	
Point to the hostname and port combo of the frontend in `maniwani.cfg`, and
the backend should communicate with it correctly. See the `docker-compose.yml`
and `maniwani.cfg` included with this repository for an example.
