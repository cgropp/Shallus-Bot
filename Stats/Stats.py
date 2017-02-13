import requests
import discord
from discord.ext import commands
import json
import os

from cogs.utils.dataIO import dataIO

class Stats:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def stats(self, ctx):
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

        return

def checkFolders():
    if not os.path.exists("data/stats"):
        print("Creating directory data/stats...")
        os.makedirs("data/stats")

def setup(bot):
    checkFolders()
    bot.add_cog(Stats(bot))