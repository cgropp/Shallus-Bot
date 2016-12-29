import discord
from discord.ext import commands
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

class Mycog:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    async def animeme(self):
        """This does stuff!"""

        #Store url of subreddit
        url = "https://reddit.com/r/anime_irl/top.json"
        
        #Get data from website using BeautifulSoup
        async with aiohttp.get(url) as response:
            soupObject = BeautifulSoup(await response.text(), "html.parser")
        
        meme = soupObject.get_text()
        
        #Trim website text
        shortmeme = meme[:1500]
        
        #Search for start of url
        urlstart = shortmeme.find('https')
        #Adjust urlstart index
        
        #Search for end of url
        urlend= shortmeme.find('author_flair_text')
        #adjust urlend index
        urlend = urlend-4
        
        #Shorten to URL
        memeurl = shortmeme[urlstart:urlend]
        
        #Bot print message
        await self.bot.say(memeurl + ' is currently the dankest animeme.')
        
        #try:
           # meme = soupObject.find(class_='title').find('href').get_text()
          #  await self.bot.say(meme + ' is the animeme of the day')
        #except:
         #   await self.bot.say("Couldn't load animeme of the day")

    # @commands.command()
    # async def animeme(self):
     #   """How many players are online atm?"""

        #Your code will go here
     #   await self.bot.say('testing')
     #   url = "https://steamdb.info/app/570/graphs/" #build the web adress
      #  async with aiohttp.get(url) as response:
       #     soupObject = BeautifulSoup(await response.text(), "html.parser")
        #try:
         #   online = soupObject.find(class_='home-stats').find('li').find('strong').get_text()
          #  await self.bot.say(online + ' players are playing this game at the moment')
        #except:
         #   await self.bot.say("Couldn't load amount of players. No one is playing this game anymore or there's an error.")

...

def setup(bot):
    if soupAvailable:
        bot.add_cog(Mycog(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
