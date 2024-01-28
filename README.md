# Python-Web-Server
*'Languages' section is lying, this is mostly programmed in python, there just happen to be 4 html files, one of which is the file for the RFC 2616 webpage, which is large.

Simple implementation of a web server in python. This project was really fun and it taught me a huge amount about http and using the sockets module in python. 

http_client.py is my simple curl clone. it makes http/1.0 requests over the socket specified in arg[1] when run in terminal.

http_server1 is a simple http 1.0 web server which can be connected to by up to 1 client at a time and will make serve http GET requests asking for .html files with a reachable path. If it isn't a GET request, the server closes the connection. If it isn't an html file, but the file exists, the server returns a 403 Forbidden response, and if the file doesn't exist the server returns a 404 Not Found response.

http_server2 is a slightly more robust version of server 1, which can handle multiple connections and serve requests to each of them whilst all are connected. This version taught me about Python's select module. Previously, I probably would have tried to solve the issue using multithreading, which may have been a bigger strain on the CPU.

http_server3 is a version of the server that does NOT serve html files, only serves one connection at a time, and is capable of handling json '/product?' queries. A non '/product?' path returns a 400 Bad Request response, and if anything else is wrong with the query it serves a 404 Not Found response.

rfc2616.html is the html file for the webpage describing RFC 2616, and is here merely for proof of concept.
