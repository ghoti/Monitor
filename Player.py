'''
Created on Dec 3, 2009

@author: ghoti
'''
class player:
    """
    Our player class will hold each client on the game server,
    tracking kills, deaths, tks, pbpower, and maybe more in 
    the future
    """
    def __init__(self, name, guid, slot):
        self.name = name
        self.guid = guid
        self.pbid = ''
        self.slot = slot
        self.pbslot = ''
        self.kills = 0
        self.deaths = 0
        self.streak = 0
        self.teamkills = 0
        self.teamkiller = None
        self.power = False
    def kill(self):
        self.kills += 1
        self.streak += 1
    def death(self):
        self.deaths += 1
        self.streak = 0
    def teamkill(self):
        self.teamkills += 1
    def teamkilled(self, cid):
        self.teamkiller = cid
    def forgive(self, player):
        player.forgiven()
        self.teamkiller = None
    def forgiven(self):
        self.teamkills -= 1
