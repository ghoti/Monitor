from config import *
import Player
import clients
import RCon
from Logparse import Logparse
from logger import logger
import ftptail
import os
import time
import re
import cPickle as Pickle
'''
Created on Dec 3, 2009

@author: ghoti

dev branch for pickle power to be used with cron
'''
class monitor:
    def __init__(self):

        #a simple lock to prevent multiple instances running since a 3rd party (cron) will be running us.
        if os.path.isfile(os.path.join('') + '.monitor.lock'):
            os.remove(os.path.join('') + '.monitor.lock')
            os.sys.exit()
        else:
            open(os.path.join('') + '.monitor.lock', 'w')

        #the local copy of the game log must meet some specific criteria to be actively parsed by us.  if it is a dated
        #copy or nonexistent, then we play catch up before we start parsing.  this is mostly a 'initial-run' check/fix.
        #this _should_ also catch up if monitor has not run in some time (20 minutes-ish)
        if os.path.isfile(logLoc + logfile) and (time.time() - os.path.getmtime(logLoc + logfile) > 1200):
            self.ftp = ftptail.ftptail()
            self.ftp.updateLog()
            self.where = os.path.getsize(logLoc + logfile)
            Pickle.dump(self.where, open(os.path.join('pickles/', 'where'), 'w'))
            #remove any left behind player pickles with an out of date log
            os.remove(os.path.join('pickles/', 'players'))
        elif not os.path.isfile(logLoc + logfile):
            self.ftp = ftptail.ftptail()
            self.ftp.updateLog()
            self.where = os.path.getsize(logLoc + logfile)
            Pickle.dump(self.where, open(os.path.join('pickles/', 'where'), 'w'))
        
        #initialize rcon'ness
        self.rcon = RCon.RCon(host, port, rconPass)

        #set up a dict to hold players referenced by game slot number
        if os.path.isfile(os.path.join('pickles/', 'players')):
            self.players = Pickle.load(open(os.path.join('pickles/', 'players'), 'r'))
        else:
            self.players = clients.clients()

        #load or create the chatqueue
        if os.path.isfile(os.path.join('pickles/', 'chat')):
            self.chat = Pickle.load(open(os.path.join('pickles/', 'chat'), 'r'))
        else:
            self.chat = []
            self.chatq([time.strftime('%H:%M:%S', time.localtime()), 'Monitor has started'])
        #download new log bits
        ftptail.ftptail()

        #parse our new info, this is the 'meat of the program ;)
        self.where = Pickle.load(open(os.path.join('pickles/', 'where'), 'r'))
        while 1:
            if self.where == os.path.getsize(logLoc + logfile):
                break
            f = open(logLoc + logfile, 'r')
            f.seek(self.where)
            line = f.readline()
            self.where = f.tell()       #read a line, mark our spot
            if line:
                line = line.lstrip()
                line = line.strip('\n')
                line = line.strip('\r') # windows and linux each use different endlines, hur hur hur
                line = re.sub(Logparse.removeTime, "", line, 1)

            #InitGame signifies either a server start or a map start
                if line.count('InitGame') > 0:
                    logLine = line.split("\\")
                    self.map = logLine[26]
                    self.gtype = logLine[22]
                    #dump these as soon as we get them :D
                    Pickle.dump(self.gtype, open(os.path.join('pickles/', 'gtype'), 'w'))
                    Pickle.dump(self.map, open(os.path.join('pickles/', 'map'), 'w'))
                    self.chatq([time.strftime('%H:%M:%S', time.localtime()), 'Map changed to  %s' % self.map])

                    #reset streak and teamkills each map.
                    for p in self.players.getAll():
                        p.teamkills = 0
                        p.teamkiller = None
                        p.streak = 0

                else:
                    for i in Logparse.lineTypes:
                        #this is so clever, i could poop.
                        m = re.match(i, line)
                        if m:
                            break
                    if m and hasattr(self, m.group('action')):
                            getattr(self, m.group('action'))(m)
                #if we are handling multiple loglines at once we need a slight pause to avoid rcon block
                time.sleep(.5)

        #Pickle the players - I will never get over the naming scheme of this
        Pickle.dump(self.players, open(os.path.join('pickles/', 'players'), 'w'))
        Pickle.dump(self.chat, open(os.path.join('pickles/', 'chat'), 'w'))
        Pickle.dump(self.where,  open(os.path.join('pickles/', 'where'), 'w'))

        #remove our lock
        os.remove(os.path.join('') + '.monitor.lock')

    #J signifies a player connecting/joining a game.  A player already playing will still show a 'j' each map as well.
    def J(self, m):
        playername = re.sub(Logparse.removeColor, '', m.group('name'))    #strip color before we do anything
        self.players.connect(int(m.group('cid')), m.group('name'), m.group('guid'))
        self.setPower(self.players.getPlayer(int(m.group('cid'))))

    #a K line is a kill event.  Kills can be any form of player->player including suicide as well as world->player
    def K(self, m):
        #suicide?
        if not m.group('acid') == '-1':
            self.gtype = Pickle.load(open(os.path.join('pickles/', 'gtype'), 'r'))
            #handle a teamkill
            if m.group('team') == m.group('ateam') and not self.gtype == 'dm':
                tkline = m.group('aname') + ' ^1TEAMKILLED ^8' + m.group('name') + '!!!'
                self.rcon.sndcmd(self.rcon.SAY, tkline)
                self.chatq([time.strftime('%H:%M:%S', time.localtime()), tkline])
                self.players.getPlayer(int(m.group('acid'))).teamkill()
                self.players.getPlayer(int(m.group('cid'))).teamkilled(int(m.group('acid')))

                #a "hack" to fix the deaths for tk's.  TK's dont affect k/d, just score
                self.players.getPlayer(int(m.group('cid'))).deaths - 1

                #If a player starts accumulating tk's...
                if self.players.getPlayer(int(m.group('acid'))).teamkills == 2:
                    self.rcon.sndcmd(self.rcon.TELL, \
                                '%s %s: "Be careful! Any more unforgiven Teamkills and you WILL be kicked!"' \
                                % (m.group('acid'), m.group('aname')))
                    self.chatq([time.strftime('%H:%M:%S', time.localtime()), \
                                '%s was warned for teamkilling' % m.group('aname')])

                #!kick
                elif self.players.getPlayer(int(m.group('acid'))).teamkills == 3:
                    #we kick dirty tk'ers! >:( -- but we are nice, we only kick for 0 minutes
                    self.rcon.sndcmd(self.rcon.KICK, m.group('aname') + ' "0 Teamkilling too much!"')
                    self.chatq([time.strftime('%H:%M:%S', time.localtime()), \
                                              '%s was kicked for teamkilling' % m.group('name')])
            else:
                #if is isn't a suicide, or a teamkill, then it is a legitimate kill.
                self.players.getPlayer(int(m.group('acid'))).kill()

                #awesome!  a simple streak announcer!
                if (self.players.getPlayer(int(m.group('acid'))).streak % 5) == 0:
                    self.rcon.sndcmd(self.rcon.SAY, '%s is on fire with %i kills since their last death!' % \
                     (self.players.getPlayer(int(m.group('acid'))).name, self.players.getPlayer(int(m.group('acid'))).streak))

        #and a streak ending announcement!  double awesome!
        if self.players.getPlayer(int(m.group('cid'))).streak >= 5:
            #another pause, rcon block makes life difficult in some cases and I hate purposely slowing myself down >:(
            time.sleep(.5)
            self.rcon.sndcmd(self.rcon.SAY, '%s\'s streak of %i kills was brutally ended by %s' % \
                            (self.players.getPlayer(int(m.group('cid'))).name, self.players.getPlayer(int(m.group('cid'))).streak, \
                            self.players.getPlayer(int(m.group('acid'))).name))
        #finally, add the death (and reset the streak) of the victim
        self.players.getPlayer(int(m.group('cid'))).death()

    #chat lines.  we loggem and savem to show on the status page and we check for potential commands
    def say(self, m):
        playername = re.sub(Logparse.removeColor, '', m.group('name'))
        text = re.sub(Logparse.removeColor, '', m.group('text'))
        self.chatq([time.strftime('%H:%M:%S', time.localtime()), playername + ': ' + m.group('text')])
        if text.lower().count('!forgive') > 0:

            #ignore a player's forgive if no one has teamkilled them."
            if self.players.getPlayer(int(m.group('cid'))).teamkiller:
                self.chatq([time.strftime('%H:%M:%S', time.localtime()), '%s was forgiven by %s' % \
                                         (self.players.getPlayer(self.players.getPlayer(int(m.group('cid'))).teamkiller).name, m.group('name'))])
                forgiven = self.players.getPlayer(self.players.getPlayer(int(m.group('cid'))).teamkiller).name
                forgiveline = m.group('name') + ' has forgiven ' + forgiven
                self.rcon.sndcmd(self.rcon.SAY, forgiveline)
                self.players.getPlayer(int(m.group('cid'))).forgive(players.getPlayer( \
                                        self.players.getPlayer(int(m.group('cid'))).teamkiller))

        if text.lower().count("!stats") > 0:
            #gotta avoid the nasty div by 0, oh noes!!11!1!
            if self.players.getPlayer(int(m.group('cid'))).deaths < 1 and featureStats:
                statline = playername + ': %i kills and 0 deaths for a ratio of %.2f' % \
                        (self.players.getPlayer(int(m.group('cid'))).kills, self.players.getPlayer(int(m.group('cid'))).kills)
            else:
                stats = float(self.players.getPlayer(int(m.group('cid'))).kills) / float(self.players.getPlayer(int(m.group('cid'))).deaths)
                statline = playername + ': %i kills and %i deaths for a ratio of %.2f' % \
                           (self.players.getPlayer(int(m.group('cid'))).kills, self.players.getPlayer(int(m.group('cid'))).deaths, stats)
            self.rcon.sndcmd(self.rcon.SAY, statline)
            self.chatq([time.strftime('%H:%M:%S', time.localtime()), statline])
            if logFeatureStats:
                logger.comlog.info('%s used the STATS command' % playername)
        elif text.lower().count('!map') > 0 and featureMap:
            if self.players.getPlayer(int(m.group('cid'))).power:
                p = re.match(Logparse.command, text)
                if p:
                    self.rcon.sndcmd(self.rcon.MAP, p.group('parms'))
                    logger.comlog.info('%s used the MAP command and changed the map to %s' % \
                                       (playername, p.group('parms')))
        elif text.lower().count('!restart') > 0 and featureRestart:
            if self.players.getPlayer(int(m.group('cid'))).power:
                self.rcon.sndcmd(self.rcon.RESTART)
                logger.comlog.info('%s used the RESTART command' % playername)

        elif text.lower().count('!gametype') > 0 and featureGametype:
            if self.players.getPlayer(int(m.group('cid'))).power:
                p = re.match(Logparse.command, text)
                if p:
                    self.rcon.sndcmd(self.rcon.GAMETYPE, p.group('parms').lower())
                    logger.comlog.info('%s used the GAMETYPE command and changed the gametype to %s' % \
                                       (playername, p.group('parms')))
                    
        elif text.lower().count('!punish') > 0:# and featurePunish:
            if self.players.getPlayer(int(m.group('cid'))).power:
                p = re.match(Logparse.command, text)
                if p:
                    for i, j in self.players.items():
                        if j.name.lower().count(p.group('parms').lower()) > 0:
                            self.rcon.sndcmd(self.rcon.PUNISH, i)
                            #another slight pause to avoid dreaded rcon block
                            time.sleep(.5)
                            self.rcon.sndcmd(self.rcon.TELL, '%s You are being Punished!' % i)
                            self.chatq([time.strftime('%H:%M:%S', time.localtime()), \
                                      ('%s has been punished' % j.name)])
                            logger.comlog.info('%s used the PUNISH command and punished %s' \
                                               % (self.players.getPlayer(int(m.group('cid'))).name, j.name))
        #hardcoded disabled for the moment
        elif text.lower().count('!kick') > 0 and featureKick:
            if self.players.getPlayer(int(m.group('cid'))).power:
                p = re.match(Logparse.command, text)
                if p:
                    for i, j in self.players.items():
                        if j.name.lower().count(p.group('parms').lower()) > 0:
                           self.rcon.sndcmd(self.rcon.KICK, self.players.getPlayer(i).pbslot + ' "0 Kicked by Admuin"')
                           self.chatq([time.strftime('%H:%M:%S', time.localtime()), \
+                                     ('%s has been kicked by an Admin' % j.name)])
                           logger.comlog.info("%s used the KICK command to kick player %s" % \
                                             (playername, j.name))
        #hardcoded disabled for the moment
        elif text.lower().count('!ban') > 0 and featureBan:
            if self.players.getPlayer(int(m.group('cid'))).power:
                p = re.match(Logparse.command, m.group('text'))
                if p:
                   for i, j in self.players.items():
                       if j.name.lower().count(p.group('parms').lower()) > 0:
                           self.rcon.sndcmd(self.rcon.BAN, self.players.getPlayer(i).pbslot + ' " Banned by Admin"')
                           self.chatq([time.strftime('%H:%M:%S', time.localtime()), \
+                                      ('%s has been Banned by an Admin' % j.name)])
                           logger.comlog.info("%s used the BAN command to ban player %s" % \
                                             (playername, j.name))

        #lets monitor decide a random custom map to play, randomly picked from the usermap folder on the server so new
        #maps are automagically added to the pool of potential maps to play :D
        elif text.lower().count('!rcustom') > 0 and featureRCustom:
            if self.players.getPlayer(int(m.group('cid'))).power:
                self.rcon.sndcmd(self.rcon.MAP, ftptail.ftptail.randomMap())

    #team chat is the same thing as regular chat, we do not concern ourselves with team chat so we send it all to chat
    def team_say(self, m):
        self.say(m)

    #player disconnects, delete their entry from the dict
    def Q(self, m):
        self.players.disconnect(int(m.group('cid')))

    #set the player's power abilities upon joining the server
    def setPower(self, play):
        #use rcon pblist to get guids and decide if we get power. Much more fancier and foolproof and safer than ftp!
        pblist = self.rcon.sndcmd(self.rcon.PLIST)
        for line in pblist.split('\n'):
            g = re.match(Logparse.pbinfo, line)
            if g:
                if g.group('name') == play.name:
                    play.power = g.group('power') == '100'
                    play.pbid = g.group('pbid')
                    play.pbslot = g.group('slot')
        #play.power = power.count(player.guid) > 0

    #simple (oh so simple!) chat stack for status page log
    def chatq(self, chat):
        if len(self.chat) == 20:
            self.chat.pop(0)
        self.chat.append(chat)

    #to handle players that may not be in our clients dict we cheat and add them when we see them perform their first action
    def firstSeen(self, m):
        pass                            
    
if __name__ == "__main__":
    mon = monitor()

   