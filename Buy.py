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

    #Find nth occurence of word
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
        
class Buy:
    """Gets frame data"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def WhatToBuy(self):
        """Suggests what to buy"""

        #Store url of website
        url = "view-source:https://awesomestufftobuy.com/"
        
        #Random index between 1 and 25 (higher numbers dont work for some reason?) #TODO FIX LATER
        rando = randint(0,20)

        
        #Get data from website using BeautifulSoup
        async with aiohttp.get(url) as response:
            soupObject = BeautifulSoup(await response.text(), "html.parser")
        
        page = soupObject.get_text()
        
        #Use findnth to find start index of what to buy
        startIndex = find_nth(page, 'title', rando)
        
        startIndex = startIndex + 7
        
        i = startIndex
        
        j = 0
        
        while (page[i:i+4] != 'href'):
            j = j + 1
            i = i + 1
            if (j > 200)
                break
            
        endIndex = startIndex + j
        
        suggestion = page[startIndex:endIndex]
        
        await self.bot.say("You should buy a " + suggestion)


def setup(bot):
    if soupAvailable:
        bot.add_cog(Buy(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")