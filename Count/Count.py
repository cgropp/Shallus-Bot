import discord
from discord.ext import commands
from random import randint
import random

import os
from cogs.utils.dataIO import dataIO

...

from discord.ext import commands

...

...


# Find nth occurence of word
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


class Count:
    """Counts. The most useless command yet!"""

    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists("data/counter"):
            print("Creating directory for count...")
            os.makedirs("data/counter")
        if not os.path.isfile("data/counter/counter.txt"):
            txtfile = open("data/counter/counter.txt", "w")
            txtfile.write("0")
            txtfile.close()

    @commands.command(pass_context=True)
    async def count(self, ctx):
        """Counts. The most useless command yet!"""
        rando = randint(0, 1000)
        if rando == (0):
            await StatsTracker.updateStat(self, "achievements", ctx.message.author.id, "Summoned The Count")
            await self.bot.say(
                "You have been visited by The Count. He only visits once in every 1,000 counts! Congratulations! http://vignette3.wikia.nocookie.net/muppet/images/3/3c/CT-p0001-ST.jpg/revision/latest?cb=20060205225316")

        counter = 0
        countFile = open("data/counter/counter.txt", "r")
        counter = int(countFile.read())
        counter = counter + 1
        countFile.close()
        countFile = open("data/counter/counter.txt", "w")
        countFile.write(str(counter))
        countFile.close()
        await self.bot.say(counter)

        await StatsTracker.updateStat(self, "commands", ctx.message.author.id, ctx.message.content[1:])

class StatsTracker:
    async def updateStat(self, stattype, userid, commandname):
        datapath = "data/stats"
        command = commandname.split(' ', 1)[0]

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
            data = {"commands": {}, "achievements": {}}
            dataIO.save_json(datapath + "/" + userid + ".json", data)


        # Read in JSON file, increment command count, write
        userdata = dataIO.load_json(datapath + "/" + userid + ".json")
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
    bot.add_cog(Count(bot))
