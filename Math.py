import discord
from discord.ext import commands

class Math:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mycom(self):
        """This does stuff!"""

        #Your code will go here
        await self.bot.say("I can do stuff!")
    
    @commands.command()
    async def add(self, first: int, second: int):
        """This code adds stuff!"""
        
        await self.bot.say("The answer is " + str((first + second)) + ".")

def setup(bot):
    bot.add_cog(Math(bot))