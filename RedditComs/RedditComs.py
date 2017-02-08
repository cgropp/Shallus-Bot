import discord
from discord.ext import commands
from random import randint
import asyncio

# Additional imports
import random
import urllib.request

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

            
    #Get JSON data from website and parse for frontpage posts
    rawjson = urllib.request.urlopen(url).read()
    parsedjson = json.loads(rawjson)
    posts = parsedjson["data"]["children"]  # List

    # Get random meme from frontpage
    randpostnum = random.randrange(len(posts))

    # Keep rerolling if post is stickied
    while (posts[randpostnum]["data"]["stickied"]):
        randpostnum = random.randrange(len(posts))

    memeurl = posts[randpostnum]["data"]["url"]

        
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
