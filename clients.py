import Player
import weakref

class clients(dict):
   def connect(self, slot, name, guid):
       if not self.has_key(slot):
           self[slot] = Player.player(name, guid, slot)
   def disconnect(self, slot):
       if self.has_key(slot):
           del self[slot]
   def getAll(self):
       plist = []
       for player in self.values():
           plist.append(weakref.ref(player)())
       return plist
   def getPlayer(self, slot):
       return self[slot]
       