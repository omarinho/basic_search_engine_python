#!/usr/bin/env python
import os
import sys
import sqlite3
import urllib2
import json
import web

# Just a few global variables to make modifications easier
ALLOWED_PLATFORMS = [(9,"SNES"),(21,"NES"),(43,"N64")]
GIANT_BOMB_API_KEY = '6fe6fb576b0c7bef2364938b2248e1628759508d' 
FETCH_URL = 'http://www.giantbomb.com/api/games/';
URLS_TO_CLASSES = (
    '/','home',
    '/search/', 'search',
    '/search','search',
    '/game/(.*)/','game_view',
    '/game/(.*)','game_view',
)
SQLITE_DB = 'games.db'
RENDER = web.template.render('templates', globals={'urllib2':urllib2, 'json':json, 'str':str})

class Game:
  def save(self, data):
    """Create a game in both main and virtual tables 
    Args:
        data (Unicode string): Data fetched from the external website
    """
    connection = sqlite3.connect(SQLITE_DB)
    # Sometimes data come without image
    if data.get('image'):
      iconURL =  data['image'].get('icon_url','')
      mediumURL = data['image'].get('medium_url','')
      screenURL = data['image'].get('screen_url','')
      smallURL =  data['image'].get('small_url','')
      superURL =  data['image'].get('super_url','') 
      thumbURL =  data['image'].get('thumb_url','')
      tinyURL =  data['image'].get('tiny_url','')
    else:
      iconURL =  ''
      mediumURL = ''
      screenURL = ''
      smallURL =  ''        
      superURL =  ''
      thumbURL = ''
      tinyURL = ''
    """
    We use a try/catch block just to skip error with the already inserted
    records (i.e. when the game is supported by several platforms)
    """
    try:
      cursor = connection.cursor()
      cursor.execute("INSERT INTO Game VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
						(data.get('name',''), 
						data['aliases'], 
						data['api_detail_url'],
						data['date_added'],
						data['date_last_updated'],
						data['deck'],
						data['description'],
						data['expected_release_day'],
						data['expected_release_month'],
						data['expected_release_quarter'],
						data['expected_release_year'],
						data['id'],
						iconURL,
						mediumURL,
						screenURL,
						smallURL,
						superURL,
						thumbURL,
						tinyURL,
						data['number_of_user_reviews'],
						json.dumps(data['original_game_rating']),
						data['original_release_date'],
						json.dumps(data['platforms']),
						data['site_detail_url']
					))
      cursor.execute("INSERT INTO GameSearch (game_id, name) VALUES (?,?)", (cursor.lastrowid, data.get('name','')) )
      connection.commit()
    except:
      pass
    connection.close()
                                        
  def read(self,id): 
    """Get data for specific game 
    Args:
        id (integer number): Row id in table (Game) 
    """
    connection = sqlite3.connect(SQLITE_DB)
    q = web.input()
    try:
      format = q.format
    except:
      format = 'html'
    if format=='json':
      connection.row_factory = dict_factory
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM Game  WHERE rowid=?", (id,))
    if format=='json':
      return cursor.fetchall()
    else:
      for row in rows:
        aGame = row
      return aGame

class Fetch:
  def __init__(self):
    """Create needed tables to store data 
    """
    connection = sqlite3.connect(SQLITE_DB)
    cursor = connection.cursor()
    sql = '''CREATE TABLE Game (
      name TEXT,
			aliases TEXT,
      api_detail_url TEXT,
      date_added TEXT,
      date_last_updated TEXT,
      deck TEXT,
      description TEXT,
      expected_release_day TEXT,
      expected_release_month TEXT,
      expected_release_quarter TEXT,
      expected_release_year TEXT,
      id TEXT,
      image_icon_url TEXT,
			image_medium_url TEXT,
			image_screen_url TEXT,
			image_small_url TEXT,
			image_super_url TEXT,
			image_thumb_url TEXT,
			image_tiny_url TEXT,
			number_of_user_reviews TEXT,
			original_game_rating TEXT,
			original_release_date TEXT,
			platforms TEXT,
			site_detail_url TEXT);'''
    cursor.execute(sql)
    connection.commit();
    """
    We create a virtual table to index our main table by name. This allow us
    to make fast searches by using full text search approach.
    """
    sql = '''CREATE VIRTUAL TABLE GameSearch USING fts3(game_id, name);'''
    cursor.execute(sql)
    connection.commit();
    connection.close()    

  def get_data(self):
    """Fetch process. Connecting to external website
    """
    print 'Starting to fetch...'
    for Key,Value in ALLOWED_PLATFORMS:
      i = 0
      print 'Getting games for ' + Value
      while True:	
        response = urllib2.urlopen(FETCH_URL + '?api_key=' + GIANT_BOMB_API_KEY + '&format=json&offset=' + str(i) + '&platforms=' + str(Key))
        data = json.load(response)
        if len(data['results']) == 0:
          break
        else:
          for result in data['results']:
            game = Game()
            game.save(result)
          i = i + 100
          print str(i) + ' records fetched so far...'
    print 'FINISHED! - You can search now in the web app'    
  
class game_view:
  def GET(self, gameID):
    """Show data for a game in a web view
    """
    game = Game()
    game = game.read(gameID)
    q = web.input()
    try:
      format = q.format
    except:
      format = 'html'
    if format=='json':
      return game
    else:
      return RENDER.game(game)

class search:        
  def GET(self):
    """Show search box without results
    """
    return RENDER.search([],'')
  def POST(self):
    """Show search box with search results for POST param (query)
    """
    q = web.input()
    try:
      format = q.format
    except:
      format = 'html'
    connection = sqlite3.connect(SQLITE_DB)
    if format=='json':
      connection.row_factory = dict_factory
    cursor = connection.cursor()
    rows = cursor.execute("SELECT game_id, name FROM GameSearch WHERE name MATCH ?", (q.query,) );
    if format=='json':
      return cursor.fetchall()
    else:
      return RENDER.search(rows,q.query)
    connection.close() 

class home:
  """Homepage
  """
  def GET(self):
    return RENDER.home()

def dict_factory(cursor, row):
  """A miscelaneous function to convert a SQLite query result into a json dictionary.
  Intended to be call as a row_factory when the app is used as an API. 
  """
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d


if __name__ == "__main__":
  """To run this program:
  
  python game_search.py IP_SERVER fetch
  
  - Replace IP_SERVER by your specific IP or 0.0.0.0
  - Second argument is optional (if omitted, fetch process is not called) 
  """
  args = sys.argv
  try:
    action = args[2]
  except:
    action='nofetch'

  # If second argument = 'fetch' we re-create the database
  if (action == 'fetch'):
    try:
      os.remove(SQLITE_DB)
    except:
      pass 
    process = Fetch();
    process.get_data()

  # Starting webapp in http://YOUR_SERVER_IP:8080/
  webapp = web.application(URLS_TO_CLASSES, globals())
  webapp.run()    