import re
'''
Created on Dec 3, 2009

@author: ghoti
'''
class Logparse:
    removeTime = re.compile(r"^(?:[0-9:]+\s?)?")
    timePat = re.compile("r'^(?P<minutes>[0-9]+):(?P<seconds>[0-9]+).*'")
    removeColor = re.compile(r"(\^[0-9a-z])|[\x80-\xff]")
    serverStatus = re.compile(r'^(?P<slot>[0-9]+)\s+(?P<score>[0-9-]+)\s+(?P<ping>[0-9]+)\s+(?P<guid>[a-z0-9]+)\s+(?P<name>.*?)\s+(?P<last>[0-9]+)\s+(?P<ip>[0-9.]+):(?P<port>[0-9-]+)\s+(?P<qport>[0-9]+)\s+(?P<rate>[0-9]+)$', re.I)
    lineTypes = (
        # server events
        re.compile(r"^(?P<action>[a-z]+):\s?(?P<data>.*)$", re.IGNORECASE),
        # world kills
        re.compile(r'^(?P<action>[A-Z]);(?P<data>(?P<guid>[^;]+);(?P<cid>[0-9-]{1,2});(?P<team>[a-z]+);(?P<name>[^;]+);(?P<aguid>[^;]*);(?P<acid>-1);(?P<ateam>world);(?P<aname>[^;]*);(?P<aweap>[a-z0-9_-]+);(?P<damage>[0-9.]+);(?P<dtype>[A-Z_]+);(?P<dlocation>[a-z_]+))$', re.IGNORECASE),
        # player kills/damage
        re.compile(r'^(?P<action>[A-Z]);(?P<data>(?P<guid>[^;]+);(?P<cid>[0-9]{1,2});(?P<team>[a-z]*);(?P<name>[^;]+);(?P<aguid>[^;]+);(?P<acid>[0-9]{1,2});(?P<ateam>[a-z]*);(?P<aname>[^;]+);(?P<aweap>[a-z0-9_-]+);(?P<damage>[0-9.]+);(?P<dtype>[A-Z_]+);(?P<dlocation>[a-z_]+))$', re.IGNORECASE),
        # suicides (cod4)
        re.compile(r'^(?P<action>[A-Z]);(?P<data>(?P<guid>[^;]+);(?P<cid>[0-9]{1,2});(?P<team>[a-z]*);(?P<name>[^;]+);(?P<aguid>[^;]*);(?P<acid>-1);(?P<ateam>[a-z]*);(?P<aname>[^;]+);(?P<aweap>[a-z0-9_-]+);(?P<damage>[0-9.]+);(?P<dtype>[A-Z_]+);(?P<dlocation>[a-z_]+))$', re.IGNORECASE),
        #A;168004;7;allies;^4[^9SaW^4] ^9|| ^1IvEl;bomb_plant
        #team actions
        re.compile(r'^(?P<action>[A-Z]);(?P<data>(?P<guid>[^;]+);(?P<cid>[0-9]{1,2});(?P<team>[a-z]+);(?P<name>[^;]+);(?P<type>[a-z_]+))$', re.IGNORECASE),
        # tell like events
        re.compile(r'^(?P<action>[a-z]+);(?P<data>(?P<guid>[^;]+);(?P<cid>[0-9]{1,2});(?P<name>[^;]+);(?P<aguid>[^;]+);(?P<acid>[0-9]{1,2});(?P<aname>[^;]+);(?P<text>.*))$', re.IGNORECASE),
        # say like events
        re.compile(r'^(?P<action>[a-z]+);(?P<data>(?P<guid>[^;]+);(?P<cid>[0-9]{1,2});(?P<name>[^;]+);(?P<text>.*))$', re.IGNORECASE),
        # all other events
        re.compile(r'^(?P<action>[A-Z]);(?P<data>(?P<guid>[^;]+);(?P<cid>[0-9]{1,2});(?P<name>[^;]+))$', re.IGNORECASE)
                )
    command = re.compile(r'^(?P<cid>\'[^\']{2,}\'|[0-9]+|[^\s]{2,}|@[0-9]+)\s?(?P<parms>.*)$')
    pbinfo = regPlayer = re.compile(r'^.*?:\s+(?P<slot>[0-9]+)\s+(?P<pbid>[a-z0-9]+)\s?\([^>)]+\)\s(?P<ip>[0-9.:]+):(?P<port>[0-9-]+) (?P<status>[a-z]+)\s+(?P<power>[0-9]+)\s+(?P<auth>[0-9.]+)\s+(?P<ss>[0-9]+)(\{[^}]+\})?\s+\((?P<os>[^)]+)\)\s+"?(?P<name>[^"]+)"?$', re.I)
