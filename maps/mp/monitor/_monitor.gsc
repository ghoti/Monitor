// PowerAdmin Tools and Plugin for BigBrotherBot(B3) (www.bigbrotherbot.com)
// 2006 www.xlr8or.com
// Modified 2008 SpacepiG
// further modified 2009 GHOTI

init()

{
  // We're in the server init routine. Do stuff before the game starts.
  Precache();

  // The server may move on now so we thread the rest.
  thread SetupDvars();
  thread StartThreads();
}

PreCache()
{
	//we don't use fancy effects, or nifty scripts that do random things, so we have nothing to precache yet
}

SetupDvars()
{
  //make sure things exist, or are empty before we go mucking around
  //setdvar("g_spectate", "")
}

StartThreads()
{
    wait .05;
    level endon("trm_killthreads");
  
  thread switchspec();
}

switchspec()
{
	level endon("trm_killthreads");
	setdvar("g_spectate", "");
	while(1)
	{
		if(getdvar("g_spectate") != "")
		{
			if (getdvar("g_spectate") == "all")
				setdvar("g_spectate", "-1");

			movePlayerNum = getdvarint("g_spectate");
			players = getentarray("player", "classname");
			for(i = 0; i < players.size; i++)
			{
				thisPlayerNum = players[i] getEntityNumber();
				if(thisPlayerNum == movePlayerNum || movePlayerNum == -1) // this is the one we're looking for
				{
					player = players[i];

					if(isAlive(player))
					{

						player unlink();
						player suicide();

						player.switching_teams = true;
						player.joining_team = "spectator";
						player.leaving_team = player.pers["team"];

            			//we are a nice bunch, and don't want to cost the team a death, or the player either, sigh
            		    player.deaths--;
  		      

						wait 2;
					}
						
					player.pers["team"] = "spectator";
					player.pers["teamTime"] = 1000000;
					player.pers["weapon"] = undefined;
					player.pers["weapon1"] = undefined;
					player.pers["weapon2"] = undefined;
					player.pers["spawnweapon"] = undefined;
					player.pers["savedmodel"] = undefined;
					player.pers["secondary_weapon"] = undefined;
					
					player.sessionteam = "spectator";
					player.sessionstate = "spectator";
					player.spectatorclient = -1;
					player.archivetime = 0;
					player.friendlydamage = undefined;
					player setClientDvar("g_scriptMainMenu", game["menu_team"]);
					player setClientDvar("ui_weapontab", "0");
					player.statusicon = "";
					
					player notify("spawned");
					player notify("end_respawn");
					resettimeout();

					player thread maps\mp\gametypes\_spectating::setSpectatePermissions();

					spawnpointname = "mp_teamdeathmatch_intermission";
					spawnpoints = getentarray(spawnpointname, "classname");
					spawnpoint = maps\mp\gametypes\_spawnlogic::getSpawnpoint_Random(spawnpoints);
	
					if(isDefined(spawnpoint))
						player spawn(spawnpoint.origin, spawnpoint.angles);
					else
						maps\mp\_utility::error("NO " + spawnpointname + " SPAWNPOINTS IN MAP");

					if(movePlayerNum != -1)
            //iprintln(player.name + "^7 was forced to Spectate by the admin");
					self notify("joined_spectators");
					
					self.TeamKillPunish = true;
				}
			}

			//if(movePlayerNum == -1)
			//	iprintln("The admin forced all players to Spectate.");

			setdvar("g_spectate", "");
		}
		wait 0.05;
	}
}
