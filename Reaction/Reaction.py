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
        
class Reaction:
    """Posts anime reaction images. Use command by typing !reaction <term> ."""



    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def reaction(self, name: str):
        """Posts anime reaction images. Use command by typing !reaction <term> ."""

     
		
        url = 'https://www.google.com/search?tbm=isch&q=anime+reaction+' + name

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
            await self.bot.say("Here's a " + name + " anime reaction image: " + imageList[rando])
        else: 
            await self.bot.say("Not enough results for " + name + " Pepe")
  
...

def setup(bot):
    if soupAvailable:
        bot.add_cog(Reaction(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
