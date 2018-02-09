#Cameron Gropp (Shallus)
import requests
import discord
from discord.ext import commands
from random import randint
try: # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False
import aiohttp

...

from discord.ext import commands
from cogs.utils.dataIO import dataIO
import os

...

try: # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False

...
        
class Pepe:
    """Posts rare pepes. Use command by typing !pepe <term> . Made by Shallus."""



    def __init__(self, bot):
        self.bot = bot
        self.censorListPath = "data/pepe/censorList.json"
        self.censoredList = {}
        if not os.path.exists(self.censorListPath):
            print("Censor list for Pepe does not exist. Creating list...")
            self.censoredList = {}
            os.makedirs("data/pepe")
            dataIO.save_json(self.censorListPath, self.censoredList)
        elif not dataIO.is_valid_json(self.censorListPath):
            print("Censor list corrupted. Creating a new one...")
            self.censoredList = {}
            os.makedirs("data/pepe")
            dataIO.save_json(self.censorListPath, self.censoredList)
        elif not dataIO.is_valid_json(self.censorListPath):
            print("Censor list corrupted. Creating a new one...")
            dataIO.save_json(self.censorListPath, self.censoredList)
        else:
            self.censoredList = dataIO.load_json(self.censorListPath)

    
    @commands.command()
    async def pepe(self, name: str):
        """Posts rare pepes. Use command by typing !pepe <term> . Made by Shallus."""

        #if (name == "big"):
        #    await self.bot.say("oco no")
        #    return
        
        url = 'https://www.google.com/search?tbm=isch&q=' + name + '+pepe'

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
            img = imageList[rando]
            if img in self.censoredList:
                await self.bot.say(self.censoredList[img])
                return
            await self.bot.say("Here's a rare " + name + " Pepe: " + img)
        else: 
            await self.bot.say("Not enough results for " + name + " Pepe")

    @commands.command(pass_context=True)
    async def pepeCensor(self, ctx, url, offStr = "The provided url has been censored."):
        leadRole = "Officer"
        botRole = "ShallusBot Dev"
        roleList = ctx.message.author.roles
        if leadRole or botRole:
            self.censoredList[url] = offStr
            await self.bot.say("URL will now be censored.")

  
...

def setup(bot):
    if soupAvailable:
        bot.add_cog(Pepe(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
