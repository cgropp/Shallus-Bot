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
    #Find nth occurence of word
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
        
class Mycog:
    """My custom cog that does stuff!"""



    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def animeme(self):
        """Posts dank animemes from /r/anime_irl."""

        #Store url of subreddit
        url = "https://reddit.com/r/anime_irl/top.json"
        
        #Random index between 1 and 25 (higher numbers dont work for some reason?) #TODO FIX LATER
        rando = randint(0,25)

        
        #Get data from website using BeautifulSoup
        async with aiohttp.get(url) as response:
            soupObject = BeautifulSoup(await response.text(), "html.parser")
        
        meme = soupObject.get_text()
        
        #Website text
        shortmeme = meme
        
        #Use findnth to find start index of first meme 
        memeindex = find_nth(shortmeme, 'author_flair_text', rando)
        #await self.bot.say(memeindex)
        #Search for start of url
        urlstart = shortmeme.find('http',(memeindex-200), (memeindex+10))
        #Adjust urlstart index
        
        #await self.bot.say(urlstart)
        
        #Search for end of url
        urlend= shortmeme.find('author_flair_text',memeindex-70,memeindex+70)
        #adjust urlend index
        urlend = urlend-4
        #await self.bot.say(urlend)
        
        #Shorten to URL
        memeurl = shortmeme[urlstart:urlend]
        
        #Bot print message
        await self.bot.say("Here's a dank animeme: " + memeurl)
  
...

def setup(bot):
    if soupAvailable:
        bot.add_cog(Mycog(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
