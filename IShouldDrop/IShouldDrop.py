import discord
from discord.ext import commands
from random import randint
import random
import time

import os
from cogs.utils.dataIO import dataIO

...

from discord.ext import commands

...

...




class IShouldDrop:
    """Drop your main for a top-tier."""

    def __init__(self, bot):
        self.bot = bot
        self.topTiers = ['Bayo', 'Cloud', 'Diddy', 'Sheik', 'Rosa']
        self.badCharacters = ['Dedede', 'Mii Swordfighter', 'Mii Brawler']

    @commands.command(pass_context=True)
    async def ishoulddrop(self, ctx, name: str):
        """Gives a random top-tier for you to drop in favor of your main."""
        topTier = random.choice(self.topTiers)
        
        if(random.randint(0, 75) == 0):
            topTier = random.choice(self.badCharacters)
        
        await self.bot.say( name + " sucks, I should drop " + name + " for " + topTier)

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

class StatsTracker:
    async def updateStat(self, stattype, ctx, commandname):
        userid = ctx.message.author.id
        name = ctx.message.author.display_name
        # Check if stats is being called in a private message
        if (ctx.message.server == None):
            serverid = "PrivateMessage"
        else:
            serverid = ctx.message.server.id
        datapath = "data/stats"
        command = commandname.split(' ', 1)[0]

        # Create directory if does not exist
        if not os.path.exists(datapath):
            print("Creating stats data directory...")
            os.makedirs(datapath)
            
        #Create directory for server if it doesn't already exist
        datapath += "/" + serverid
        if not os.path.exists(datapath):
            print("Creating server data directory...")
            os.makedirs(datapath)        

        # Create JSON file if does not exist or if invalid
        invalidJSON = False
        if not os.path.isfile(datapath + "/" + userid + ".json"):
            invalidJSON = True
        elif not dataIO.is_valid_json(datapath + "/" + userid + ".json"):
            await self.bot.say("Invalid stats JSON found. All your stats are gone forever. Blame a dev :^(")
            invalidJSON = True

        if(invalidJSON):
            data = {"commands": {}, "achievements": {}}
            dataIO.save_json(datapath + "/" + userid + ".json", data)


        # Read in JSON file, increment command count, write
        userdata = dataIO.load_json(datapath + "/" + userid + ".json")
        userdata["username"] = name
        if stattype not in userdata:
            userdata[stattype] = {}
        if command not in userdata["commands"]:
            userdata[stattype][command] = 0

        userdata[stattype][command] += 1
        dataIO.save_json(datapath + "/" + userid + ".json", userdata)

        return

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        return


...


def setup(bot):
    bot.add_cog(IShouldDrop(bot))
