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
        
class Story:
    """Collaborative story. What could possible go wrong?"""


    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def story(self):
        """Shows the current story. Made by Shallus."""

        
        curStory = ""
        storyFile = open("cogs/story.txt","r")
        curStory = storyFile.read()
        storyFile.close()
        await self.bot.say(curStory)

    
    @commands.command()
    async def addChar(self, charToAdd: str):
        """Adds a char to the story. Made by Shallus."""
        
        
        curStory = ""
        charToAdd = charToAdd[0:1]
        storyFile = open("cogs/story.txt","r+")
        
        #Covers max discord message length case
       # if len(curStory) > 1990:
          #  storyFile.close()
         #   storyFile = open("cogs/story.txt","w")
          #  await self.bot.say("Story has reached max length, and is being reset...")
        curStory = storyFile.read()     
        storyFile.write(charToAdd)
      #  curStory = storyFile.read()
        await self.bot.say("'" + charToAdd + "' has been added to the story." )
        storyFile.close()
        #Read for printing
        storyFile = open("cogs/story.txt","r")
        curStory = storyFile.read()
        await self.bot.say(curStory)
        storyFile.close()
        
        
...

def setup(bot):
    bot.add_cog(Story(bot))
    