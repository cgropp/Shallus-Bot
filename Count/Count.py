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
        rando = randint(0,1000)
        if rando == (999):
            await self.bot.say("You have been visited by The Count. He only visits once in every 1,000 counts! Congratulations! http://vignette3.wikia.nocookie.net/muppet/images/3/3c/CT-p0001-ST.jpg/revision/latest?cb=20060205225316")
        
        counter = 0
        countFile = open("data/counter/counter.txt","r")
        counter = int(countFile.read())
        counter = counter + 1
        countFile.close()
        countFile = open("data/counter/counter.txt","w")
        countFile.write(str(counter))
        countFile.close()
        await self.bot.say(counter)
  
...

def setup(bot):
    bot.add_cog(Count(bot))
    