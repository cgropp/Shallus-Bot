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
            
        #Read from file
        countFile = open("data/counter/counter.txt", "r")
        self.counter = int(countFile.read())
        countFile.close()
        #Initialize lastWrite time
        self.lastWrite = 0

    @commands.command(pass_context=True)
    async def count(self, ctx):
        """Counts. The most useless command yet!"""
        #Small chance for the count to appear
        rando = randint(0, 1000)
        if rando == (0):
            await StatsTracker.updateStat(self, "achievements", ctx.message.author.id, "Summoned The Count")
            await self.bot.say(
                "You have been visited by The Count. He only visits once in every 1,000 counts! Congratulations! http://vignette3.wikia.nocookie.net/muppet/images/3/3c/CT-p0001-ST.jpg/revision/latest?cb=20060205225316")
        
        
        #Increment count
        self.counter = self.counter + 1
        
        
        #Calculate how long it has been since last write
        timeSinceWrite = (time.time() - self.lastWrite)
        #If write is necessary, write to file and update lastWrite time
        if (timeSinceWrite >= 60*1):
            countFile = open("data/counter/counter.txt", "w")
            countFile.write(str(self.counter))
            countFile.close()
            self.lastWrite = time.time()
        #Print out current count number
        await self.bot.say(self.counter)

        #Write to stats
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
    bot.add_cog(Count(bot))
