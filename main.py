# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# main.py serves the Morningstar home page.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import rules

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
class MainHandler(webapp.RequestHandler):
    def get(self):
        _trace = TRACE+'MainHandler:: get() '
        logging.info(_trace)        
        template_values = {
            'players': simplejson.dumps(DEATH_PINS),
            'monsters': simplejson.dumps(MONSTER_PINS),
            'battles': simplejson.dumps(BATTLE_PINS)
        }        
        generate(self, 'main.html', template_values)               

######################## METHODS #############################################
##############################################################################
def generate(self, template_name, template_values):
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 
                        os.path.join('templates', template_name))

    self.response.out.write(template.render(path, 
                                            template_values, 
                                            debug=DEBUG))

######################## DATA ################################################
##############################################################################
BATTLE_PINS = [
    {'lat':47.6, 'lon':-122.3, 'location': 'Seattle, Washington'},
    {'lat':38.651198, 'lon':-90.2362, 'location': 'St. Louis, Missouri'},
    {'lat':38.66, 'lon':-109.59, 'location': 'Arches National Park'}    
  ]
 
MONSTER_PINS = [
    {'lat':47.6355, 'lon':-122.2953, 'location': 'Seattle, Washington'},
    {'lat':32.7272, 'lon':-117.1692, 'location': 'San Diego, California'},
    {'lat':33.9616, 'lon':-117.4109, 'location': 'Riverside, California'},    
    {'lat':34.1755, 'lon':-118.8501, 'location': 'Thousand Oaks, California'},  
    {'lat':37.3204, 'lon':-113.0747, 'location': 'Zion National Park'}
  ]

DEATH_PINS = [
    {'lat':47.6621, 'lon':-122.1130, 'location': 'Redmond, Washington'},
    {'lat':41.8817, 'lon':-87.6227, 'location': 'Chicago, Illinois'},
    {'lat':41.88796, 'lon':-87.7859, 'location': 'Oak Park, Illinois'},
    {'lat':37.7707, 'lon':-122.4701, 'location': 'San Francisco, Washington'}
  ]

                                            
##############################################################################
##############################################################################
application = webapp.WSGIApplication([(r'/.*', MainHandler)],
                                       debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()