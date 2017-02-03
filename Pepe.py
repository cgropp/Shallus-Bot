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
    
    @commands.command()
    async def pepe(self, name: str):
        """Posts rare pepes. Use command by typing !pepe <term> . Made by Shallus."""

     
		
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
            await self.bot.say("Here's a rare " + name + " Pepe: " + imageList[rando])
        else: 
            await self.bot.say("Not enough results for " + name + " Pepe")
  
...

def setup(bot):
    if soupAvailable:
        bot.add_cog(Pepe(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
