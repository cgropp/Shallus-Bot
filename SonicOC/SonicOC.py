#Cameron Gropp (Shallus)
import requests
import discord
from discord.ext import commands
from random import randint

import os
from cogs.utils.dataIO import dataIO

try: # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False
import aiohttp

...

from discord.ext import commands

...

try: # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False

...
        
class SonicOC:
    """Posts OC hedgehogs. Use command by typing !sonicOC <name> . Made by Shallus. Credit to evangelato for the idea"""



    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    async def sonicOC(self, ctx, name: str):
        """Posts OC hedgehogs. Use command by typing !sonicOC <name> . Made by Shallus. Credit to evangelato for the idea"""

     
		
        url = 'https://www.google.com/search?tbm=isch&q=' + name + '+the+hedgehog'

	# page = open('tower.html', 'r').read()
        count = 0
        page = requests.get(url).text
        imageList = []
        soup = BeautifulSoup(page, 'html.parser')

        for raw_img in soup.find_all('img'):
            link = raw_img.get('src')
            if link:
                #Increment count for later random selection
                imageList.append(link)
                count = count + 1
        
        #Makes sure there are enough results
        if len(imageList) > 6: 
            rando = randint(0,5)
            #await self.bot.say(len(imageList)) #Debug statement
            await self.bot.say("This is " + name + " the Hedgehog: " + imageList[rando])
        else: 
            await self.bot.say("Not enough results for " + name + " the Hedgehog")

        await StatsTracker.updateStat(self, ctx.message.author.id, "sonicOC")



class StatsTracker:
    async def updateStat(self, userid, commandname):
        datapath = "data/stats"
        command = commandname.split(' ', 1)[0]

        # Create directory if does not exist
        if not os.path.exists(datapath):
            print("Creating stats data directory...")
            os.makedirs(datapath)

        # Create JSON file if does not exist or if invalid
        invalidJSON = False
        if not os.path.isfile(datapath + "/" + userid + ".json"):
            invalidJSON = True
        elif not dataIO.is_valid_json(datapath + "/" + userid + ".json"):
            await self.bot.say("Invalid stats JSON found. All your stats are gone forever. Blame a dev :^(")
            invalidJSON = True

        if(invalidJSON):
            data = {"commands": {}, "achievements": {}}
            dataIO.save_json(datapath + "/" + userid + ".json", data)


        # Read in JSON file, increment command count, write
        userdata = dataIO.load_json(datapath + "/" + userid + ".json")
        if "commands" not in userdata:
            userdata["commands"] = {}
        if command not in userdata["commands"]:
            userdata["commands"][command] = 0

        userdata["commands"][command] += 1
        dataIO.save_json(datapath + "/" + userid + ".json", userdata)

        return

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        return


def setup(bot):
    if soupAvailable:
        bot.add_cog(SonicOC(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
