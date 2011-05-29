# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# app.py serves the Morningstar application to end users on mobile devices.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import rules
import utils

from model import character
from model import party
from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

############################# REQUEST HANDLERS ############################### 
##############################################################################   
class BaseHandler(webapp.RequestHandler):
    def get_user(self):
        '''Returns a User object associated with a Google account.
        '''
        _trace = TRACE+'APIBase:: get_user() '
        logging.info(_trace)
        user = users.get_current_user()
        logging.info(_trace+'user = '+ str(user.email()))            
        return user    

class MainHandler(BaseHandler):
    def get(self):
        _trace = TRACE+'MainHandler.get() '
        logging.info(_trace)
        user = users.get_current_user()
        characters = models.Character.all().filter('user =', user).fetch(100)
        template_values = {
            'characters': characters,
            'user': user
        }
        generate(self, 'start.html', template_values)  

class CharacterHandler(BaseHandler):
    def get(self):
        _trace = TRACE+'CharacterHandler.get() '
        logging.info(_trace)        
        templates = models.PlayerCharacterTemplate.all().fetch(100) 
        user = users.get_current_user()
        template_values = {
            'templates': templates,
            'user': user
        }        
        generate(self, 'character_create.html', template_values)
        
    def post(self):  
        _trace = TRACE+'CharacterHandler.post() '
        logging.info(_trace)
        user = users.get_current_user()
        key = self.request.get('template')
        name = self.request.get('name')
        template = db.get(key)
        if template is not None:
            _player = character.createPlayerFromTemplate(template, name, user)
            lat = self.request.get('lat')
            lon = self.request.get('lon')
            location = db.GeoPt(utils.strToIntOrFloat(lat), 
                                utils.strToIntOrFloat(lon))
            
            _party = party.createJSONParty(_player, location)            
            
        self.redirect('/mobile/character/'+str(_player.key()))      

class CharacterSheetHandler(BaseHandler):
    def get(self, key):
        _trace = TRACE+'CharacterSheetHandler.get() '
        logging.info(_trace)        
        _character = db.get(key) 
        player = character.getJSONPlayer(_character)
        user = users.get_current_user()
        template_values = {
            'player': player,
            'user': user
        }        
        generate(self, 'character_sheet.html', template_values)

class CharacterQuestHandler(BaseHandler):
    def get(self, key):
        _trace = TRACE+'CharacterQuestHandler.get() '
        logging.info(_trace)        
        _character = db.get(key) 
        _player = character.getJSONPlayer(_character)
        user = users.get_current_user()
        
        # Get Pins
        battles = models.BattlePin.all().fetch(100)
        monsters = models.MonsterPartyPin.all().fetch(100)
        players = models.PlayerPartyPin.all().fetch(100) 
        battles_json = []
        monsters_json = []
        players_json = []
        for b in battles:
            lat, lon = utils.parseGeoPt(b.location)
            data = {'name': b.name,'lat': lat,'lon': lon}
            battles_json.append(data)
        for m in monsters:
            lat, lon = utils.parseGeoPt(m.location)
            data = {'name': m.name,'lat': lat,'lon': lon}
            monsters_json.append(data)  
        for p in players:
            lat, lon = utils.parseGeoPt(p.location)
            data = {'name': p.name,'lat': lat,'lon': lon}
            players_json.append(data)
              
        logging.info(_trace+'battles = '+simplejson.dumps(battles_json))
        logging.info(_trace+'monsters = '+simplejson.dumps(monsters_json))
        logging.info(_trace+'players = '+simplejson.dumps(players_json))
        
        template_values = {
            'players': simplejson.dumps(players_json),
            'monsters': simplejson.dumps(monsters_json),
            'battles': simplejson.dumps(battles_json),
            'player': _player,
            'user': user
        }        
        generate(self, 'character_quest.html', template_values)

    def post(self, key):
        _trace = TRACE+'CharacterQuestHandler.post() '
        logging.info(_trace)
        logging.info(_trace+'key = '+key)
        #return {'foo': 123}
        self.redirect('/mobile/character/'+key+'/quest')
        
######################## METHODS #############################################
##############################################################################
def generate(self, template_name, template_values):
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 
                        os.path.join('templates/mobile', template_name))

    self.response.out.write(template.render(path, 
                                            template_values, 
                                            debug=DEBUG))
                                            
##############################################################################
##############################################################################
application = webapp.WSGIApplication([('/mobile/character/create', 
                                       CharacterHandler),
                                      (r'/mobile/character/(.*)/quest', 
                                       CharacterQuestHandler),
                                      (r'/mobile/character/(.*)', 
                                       CharacterSheetHandler),
                                      (r'/mobile/.*', 
                                       MainHandler)
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()