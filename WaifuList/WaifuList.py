import discord
from discord.ext import commands
from random import randint
import random

...

from discord.ext import commands

...


...
        
class WaifuList:
    """Keeps track of a list of saved waifus."""


    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def waifulist(self):
        """Displays a list of your saved waifus."""
        
    
...

def setup(bot):
    bot.add_cog(WaifuList(bot))
    