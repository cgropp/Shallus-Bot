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
        
class SonicOC:
    """Posts OC hedgehogs. Use command by typing !sonicOC <name> . Made by Shallus. Credit to evangelato for the idea"""



    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def sonicOC(self, name: str):
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
  
...

def setup(bot):
    if soupAvailable:
        bot.add_cog(SonicOC(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
