from ftplib import FTP
from config import ftpHost, ftpPort, ftpUser, ftpPass, logfile, logLoc, ftpLogLoc, usermaps
import os
import random
#import cPickle as Pickle

'''
Created on Dec 3, 2009

@author: ghoti
'''
class ftptail:
    def __init__(self):
        self.ftp = FTP()
        self.ftp.connect(ftpHost, ftpPort)
        self.ftp.login(ftpUser, ftpPass)
        self.ftp.voidcmd("TYPE I")

    def updateLog(self):
        if os.path.isfile(logLoc + logfile):
            #load the current file size pickle
            #self.where = Pickle.load(open(os.path.join("pickles/", "ftpwhere"), "r"))
            self.where = os.path.getsize(logLoc + logfile)
            #os.remove(os.path.join("pickles/", "ftpwhere"))
            #do we need to download more log?
            if os.path.getsize(logLoc + logfile) == self.ftp.size(ftpLogLoc + logfile):
                #Pickle.dump(self.where, open(os.path.join("pickles/", "ftpwhere")).write)
                pass
            #download the new log parts
            else:
                self.ftp.retrbinary("RETR " + ftpLogLoc + logfile, open(logLoc + logfile, "ab").write, 8192, self.where)
                #Pickle.dump(self.where, open(os.path.join("pickles/", "ftpwhere")).write)
        else:
            self.ftp.retrbinary("RETR " + ftpLogLoc + logfile, open(logLoc + logfile, "ab").write)
        self.ftp.close()

    #returns a random map from the usermaps folder on the gameserver
    def randomMap(self):
        self.ftp.cwd(usermaps)
        return random.choice(self.ftp.nlst())
        