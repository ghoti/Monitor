from socket import socket, AF_INET, SOCK_DGRAM
import threading, time, re

'''
Created on Dec 3, 2009

@author: ghoti
'''

class RCon:
    '''
    RCon class to manage sending commands to the game server.  Credits
    to users from fpsadmin.com forums for details and unicode explanation.
    '''
    SAY = 0
    MAP = 1
    RESTART = 2
    GAMETYPE = 3
    KICK = 4
    BAN = 5
    TELL = 6
    PUNISH = 7
    STATUS = 8
    PLIST = 9
    def __init__(self, host, port, password):
        self.host = host
        self.port= port
        self.password = password
        self.link = socket(AF_INET, SOCK_DGRAM)
        self.link.connect((host, port))
    def command(self, cmd):
        if cmd == RCon.SAY: return "say"
        elif cmd == RCon.TELL:  return "tell"
        elif cmd == RCon.MAP:   return "map"
        elif cmd == RCon.RESTART:   return "map_restart"
        elif cmd == RCon.GAMETYPE:  return "g_gametype"
        elif cmd == RCon.PUNISH:    return "g_spectate"
        elif cmd == RCon.KICK:  return "pb_sv_kick"
        elif cmd == RCon.BAN:   return "pb_sv_ban"
        elif cmd == RCon.STATUS:    return "status"
        elif cmd == RCon.PLIST: return "PB_SV_PList"
    def sndcmd(self, action, name=""):
        action = self.command(action)
        self.cmd = u"\xFF\xFF\xFF\xFFrcon %s %s %s" % (self.password, action, name)
        self.link.sendall(self.cmd.encode("latin_1"))
        if action == "status" or action == "PB_SV_PList":
            try:
                msg = self.link.recv(5000)
                last = msg
                if len(msg) == 5000:
                    while last != '':
                        last = self.link.recv(5000)
                        if last == '': break
                        else: msg = msg + last
                return msg.strip("\n\xFF\xFF\xFF\xFFprint")
            except:
                pass
