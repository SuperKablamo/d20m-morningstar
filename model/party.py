# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# party.py defines the Data and Methods for providing access to Party 
# resources as well as actions Characters can invoke, as a member of a Party,
# on other Parties and their members.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import rules

from model import pin
from settings import *
from utils import roll

############################# GAE IMPORTS ####################################
##############################################################################
import character
import logging
import monster
import time

from google.appengine.ext import db

######################## METHODS #############################################
##############################################################################
def getJSONParty(party):
    '''Returns a JSON representation of a Party.
    '''
    _trace = TRACE+'getJSONParty() '
    logging.info(_trace) 
    logging.info(_trace + 'player = ' + str(party.key()))
    json = {'key': str(party.key()), 'location': str(party.location),
            'log': party.log}

    if party.class_name() == 'PlayerParty':
        json['leader'] = str(party.leader.key())
        players_json = []
        players = db.get(party.players)
        for j in players:
            players_json.append(character.getJSONPlayer(j))
        json['players'] = players_json

    if party.class_name() == 'NonPlayerParty':
        if party.owner:
            json['owner'] = str(party.owner.nickname())
        monsters_json = []    
        monsters = db.get(party.monsters)
        for m in monsters:
            monsters_json.append(monster.getJSONMonster(m))
        json['monsters'] = monsters_json      
       
    return json
    
def updateJSONParty(party, *characters):
    '''Updates a Party with one or more Characters, and Returns a JSON 
    representation of the Party.
    '''
    _trace = TRACE+'updateJSONParty() '
    logging.info(_trace)
    
    return

def createJSONParty(leader, location, players=None):       
    """Creates a new Party for the Character.
    Returns: JSON representation of the Party.
    """
    _trace = TRACE+'createJSONParty() '
    logging.info(_trace)
    log = {'encounter_log': 
           {'total': 0, 'uniques': 0, 'start_time': time.time(),
            'last_encounter': {'time_since': 0, 'checks': 0}}}
            
    party = models.PlayerParty(location = location,
                               leader = leader,
                               players = [leader.key()],
                               log = log)

    db.put(party)
    
    _pin = pin.createPlayerPartyPin(location, 
                                    party, 
                                    leader)
                                    
    json = {'key': str(party.key()), 'pin_key': str(_pin.key()),   
            'leader_key': str(party.leader.key()), 'location': str(location), 
            'players': [str(party.leader.key())], 'log': str(log)}
                         
    return json

def getJSONQuest(party, player, geo_loc):
    '''Returns any events, parties, and traps found at the PlayerParties 
    location.
    '''
    quest = rules.rollEncounter(party, geo_loc)
    return quest 

def getJSONAttack(party, monsters, attacker, attack):
    '''Returns the damage inflicted on any monsters.
    '''
    damage = []
    for m in monsters:
        result = rules.attackMonster(attacker, attack, m)
        damage.append(result)
            
    return damage    
    
####################### DATA ################################################
##############################################################################
