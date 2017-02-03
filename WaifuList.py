import discord
from discord.ext import commands
from random import randint
import random

...

from discord.ext import commands

...


...
    #Find nth occurence of word
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
        
class Count:
    """Counts. The most useless command yet! Made by Shallus."""


    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def count(self):
        """Counts. The most useless command yet! Made by Shallus."""
       s
        await self.bot.say(counter)
  
...

def setup(bot):
    bot.add_cog(WaifuList(bot))
    