try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import discord
import re
from discord.ext import commands
from random import randint
import random
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
        
class Yuri:
    """Posts waifus from safebooru. Made by Shallus."""

    

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def yuri(self):
        """Posts yuri from safebooru. Made by Shallus."""
        rando = randint(0,64)
        rando = rando * 40
        #Store url of random female booru page
        url = "https://safebooru.org/index.php?page=post&s=list&tags=holding_hands+yuri+-1boy+-2boys&pid=" + str(rando)
        html = urllib2.urlopen(url)
        soup = BeautifulSoup(html)
        imgs = soup.findAll("div", {"class":"thumb-pic"})
        
        list = []
        
        
        #Obtains all posts from page
        #links = soup.find_all('href')
        #await self.bot.say("url is " + url)
        for link in soup.findAll('a'):
            link = link["href"].split("href=")[-1]
            if 'safebooru' not in link and 'index' in link and 'safechibi' not in link and "tags" not in link and 'http' not in link and "id=" in link and "post" in link:
                           # await self.bot.say(link + " was added to list of links")
                            list.append("http://safebooru.org/" + link)
        
        #sets new URL to a random choice from page
       # await self.bot.say("Debug statement: about to determine url2")
        url2 = random.choice(list)
       # await self.bot.say("Debug statement: This is url2 " + url2)
        html = urllib2.urlopen(url2)
        soup = BeautifulSoup(html)
        imgs = soup.findAll("div", {"class":"thumb-pic"})
        
        #finds all images, picks a random one
        links2 = soup.find_all('img', src=True)
        for link2 in links2:
            link2 = link2["src"].split("src=")[-1]
            if 'safebooru' in link2:
                if 'safechibi' not in link2:
                    await self.bot.say("Here's some (SFW) yuri: http:" + link2)
        
        
        
        #await self.bot.say("Here's some (SFW) yuri: http:" + random.choice(list))
  
      
...

def setup(bot):
    if soupAvailable:
        bot.add_cog(Yuri(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
