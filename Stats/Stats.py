import requests
import discord
from discord.ext import commands
import json
import os

from cogs.utils.dataIO import dataIO

class Stats:
    """Prints how many times you've used commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        """Prints how many times you've used commands."""
        datapath = "data/stats"
        userid = ctx.message.author.id
        displayname = ctx.message.author.display_name

        # Can't print if data invalid or if
        if not os.path.isfile(datapath + "/" + userid + ".json"):
            await self.bot.say("You don't have any stats tracked, " + displayname + "! Try using some commands.")
            return
        elif not dataIO.is_valid_json(datapath + "/" + userid + ".json"):
            await self.bot.say("Invalid stats JSON found. All your stats are gone forever. Blame a dev :^(")
            data = {}
            dataIO.save_json(datapath + "/" + userid + ".json", data)
            return

        output = ""
        # Print all available stats
        userdata = dataIO.load_json(datapath + "/" + userid + ".json")
        for commandname, count in userdata.items():
            output += commandname + ":  " + str(count) + "\n"
        await self.bot.say(output)

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])

        return


class StatsTracker:
    async def updateStat(self, userid, commandname):
        datapath = "data/stats"

        # Create directory if does not exist
        if not os.path.exists(datapath):
            print("Creating stats data directory...")
            os.makedirs(datapath)

        # Create JSON file if does not exist or if invalid
        invalidJSON = False
        if not os.path.isfile(datapath + "/" + userid + ".json"):
            invalidJSON = True
        elif not dataIO.is_valid_json(datapath + "/" + userid + ".json"):
            await self.bot.say("Invalid stats JSON found. All your stats are gone forever. Blame a dev :^(")
            invalidJSON = True

        if(invalidJSON):
            data = {}
            dataIO.save_json(datapath + "/" + userid + ".json", data)


        # Read in JSON file, increment command count, write
        userdata = dataIO.load_json(datapath + "/" + userid + ".json")
        if commandname not in userdata:
            userdata[commandname] = 0

        userdata[commandname] += 1
        dataIO.save_json(datapath + "/" + userid + ".json", userdata)

        return

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        return

def checkFolders():
    if not os.path.exists("data/stats"):
        print("Creating directory data/stats...")
        os.makedirs("data/stats")

def setup(bot):
    checkFolders()
    bot.add_cog(Stats(bot))