INSTRUCTIONS TO INSTALL THE VIDEO GAMES SEARCH APP (ON A LINUX SERVER)

1. Dependency 1: You need sqlite3 in your server. It is included in the Python standard library (since Python 2.5).

1. Dependency 2: Install web.py in your server (it is an easy & light framework)
For example, by running: 
	sudo easy_install web.py

	or 

	pip install web.py

For more info: http://webpy.org/

2. Extract and copy the app files (game_search.zip) to your server (for example in /var/ directory)

3. Make sure the port 8080 of your server is available and open to connections

4. And run:

python game_search.py 0.0.0.0 fetch

You can use the IP of your server in case 0.0.0.0 doesn't work for your specific configuration.

Initially, this will fetch all NES, SNES, N64 games in order to save them in a local text database (SQLite). 
Wait until the process completes. It will take a couple minutes.

When fetch process is finished, the program will create a web server on your IP:8080 to serve up the requests.

Go to the browser and call:
	http://YOUR_SERVER_IP:8080

In the homepage, you will find instructions about the API (data in json format). But you also can see search results in HTML format.
