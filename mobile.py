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

from model import character
from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging

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
        logging.debug(_trace)
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
        logging.debug(_trace)        
        templates = models.PlayerCharacterTemplate.all().fetch(100) 
        user = users.get_current_user()
        template_values = {
            'templates': templates,
            'user': user
        }        
        generate(self, 'character_create.html', template_values)
        
    def post(self):  
        _trace = TRACE+'CharacterHandler.post() '
        logging.debug(_trace)
        user = users.get_current_user()
        key = self.request.get('template')
        name = self.request.get('name')
        template = db.get(key)
        if template is not None:
            player = character.createPlayerFromTemplate(template, name, user)

        template_values = {
            'player': player,
            'template': template,
            'user': user
        }        
        generate(self, 'character_sheet.html', template_values)        

class CharacterSheetHandler(BaseHandler):
    def get(self, key):
        _trace = TRACE+'CharacterSheetHandler.get() '
        logging.debug(_trace)        
        character = db.get(key) 
        user = users.get_current_user()
        template_values = {
            'character': character,
            'user': user
        }        
        generate(self, 'character_sheet.html', template_values)

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