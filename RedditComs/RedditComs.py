import discord
from discord.ext import commands
from random import randint
import asyncio
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

  #Gets meme url from subreddit
async def getMemeUrl(subreddit : str, randoLimit : int):    
    #Store url of subreddit
    url = ("https://reddit.com/r/" + subreddit + ".json")
            
    #Random index between 1 and 25 (higher numbers dont work for some reason?) #TODO FIX LATER
    rando = randint(0,randoLimit)

            
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
    #Directly link to image
    if 'imgur' in memeurl and "i.imgur" not in memeurl and "/a/" not in memeurl:
        memeurl = (memeurl + ".png")
       
    return str(memeurl)      
  
class RedditComs:
    """Fetches content from reddit."""

    def __init__(self, bot):
        self.bot = bot
   
    
    @commands.command()
    async def animeme(self):
        """Posts dank animemes from /r/anime_irl."""
        memeurl = await getMemeUrl("anime_irl/top", 25)
        await self.bot.say("Here's a dank animeme: " + str(memeurl))
        
    @commands.command()
    async def birb(self):
        """Posts stuff from /r/birbs."""
        memeurl = await getMemeUrl("birbs", 20)
        await self.bot.say("Chirp chirp: " + str(memeurl))

    @commands.command()
    async def cute(self):
        """Posts stuff from /r/aww."""
        memeurl = await getMemeUrl("aww/top", 25)
        await self.bot.say("Aww: " + str(memeurl))
        
    @commands.command()
    async def dogmeme(self):
        """Posts stuff from /r/woof_irl"""
        memeurl = await getMemeUrl("woof_irl", 25)
        await self.bot.say("Woof: " + str(memeurl))
        
    @commands.command()
    async def sponge(self):
        """Posts stuff from /r/bikinibottomtwitter."""
        memeurl = await getMemeUrl("bikinibottomtwitter", 20)
        await self.bot.say("Fresh from Bikini Bottom: " + str(memeurl))        
        

        

        
        
...

def setup(bot):
    if soupAvailable:
        bot.add_cog(RedditComs(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
