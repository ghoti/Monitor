"""
Configuration options
all directory names require the trailing slash to work
example: "/home/user/monitor/"
"""
#log location on local computer, this will also determine where to put the file if we download one
logLoc = ""
#name of the logfile to use"
logfile = "games_mp.log"
#ip or hostname of the ame server
host = ""
#game port
port = 28960
#number of slots in the game
gameSlots = 20
#rcon password
rconPass = ""
#ftp ip or hostname
ftpHost = ""
#ftp port - if you dont know, then 21 should work
ftpPort = 21
#ftp username
ftpUser = ""
#ftp password
ftpPass = ""
#log location on ftp site - either absolute path, or relative to ftp home dir
ftpLogLoc = "/"
#filename for our command log, will be created if not exists and placed in the monitor dir
monitorLog = "commands.log"
#Option flags for all features, ban and kick are disabled by default until they are safe :-p
featureStats = True
featureRestart = True
featureMap = True
featureGametype = True
featurePunish = True
featureKick = False
featureBan = False
logFeatureStats = False
'''
status page options, disabled by default - statusPageLocation MUST be writable, I suggest leaving it in the monitor
directory and softlinking it to a web-directory (ln -s in linux)
'''
featureStatusPage = False
statusPageLocation = "./"
