import requests
import discord
from discord.ext import commands
import random
import json
import os
import time

from cogs.utils.dataIO import dataIO
from requests.auth import HTTPBasicAuth


class Safebooru:
    """Fetches images from Safebooru and allows for storing of waifus in waifulists."""
    def __init__(self, bot):
        self.bot = bot
        self.waifuLists = {}
        self.lastWaifuRolled = {}
        invalidLists = []
        for userId in os.listdir("data/safebooru/WaifuList"):
            if not dataIO.is_valid_json("data/safebooru/WaifuList/" + userId):
                invalidLists.append(userId + "\n")
            else:
                self.waifuLists[userId[:-5]] = dataIO.load_json("data/safebooru/WaifuList/" + userId)
        if not len(invalidLists) == 0:
            print("Warning: the following files were not saved properly, and have been lost: \n")
            for user in invalidLists:
                print(user)

    @commands.command(pass_context=True)
    async def waifu(self, ctx):
        """Posts a random waifu from Safebooru."""
        params = {"tags": u'1girl solo'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here is your waifu, " + ctx.message.author.display_name + ": " + linkName)

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])
        return

    @commands.command(pass_context=True)
    async def husbando(self, ctx):
        """Posts a random husbando from Safebooru."""
        params = {"tags": u'1boy solo'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's your husbando, " + ctx.message.author.display_name + ": " + linkName)

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])
        return        
        
    @commands.command(pass_context=True)
    async def yuri(self, ctx):
        """Posts a random (SFW) yuri image from Safebooru."""
        params = {"tags": u'holding_hands yuri'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's some (SFW) yuri, " + ctx.message.author.display_name + ": " + linkName)

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])
        return
        
    @commands.command(pass_context=True)
    async def yaoi(self, ctx):
        """Posts a random (SFW) yaoi image from Safebooru."""
        params = {"tags": u'yaoi'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's some (SFW) yaoi, " + ctx.message.author.display_name + ": " + linkName)

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])
        return


    @commands.command(pass_context=True)
    async def marrywaifu(self, ctx):
        """Adds the last waifu you rolled to your waifu list."""
        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

        author = ctx.message.author
        waifu = self.lastWaifuRolled.get(author.id)
        authorFile = "data/safebooru/WaifuList/" + str(author.id) + ".json"
        if waifu == None:
            await self.bot.say("No character rolled this session.")
            return
        waifuList = self.waifuLists.get(author.id)
        if waifuList == None:
            self.waifuLists[author.id] = {"name": author.name, "waifu_list": [waifu]}
            dataIO.save_json(authorFile, self.waifuLists[author.id])
            self.lastWaifuRolled[author.id] = None
            await self.bot.say("Congratulations on your marriage, " + author.display_name + " and " + waifu["name"] + "!")
            return
        if len(waifuList["waifu_list"]) >= 5:
            await self.bot.say("Max number of waifus reached! Please divorce a waifu before marrying more.")
            return
        self.waifuLists[author.id]["waifu_list"].append(waifu)
        dataIO.save_json(authorFile, self.waifuLists[author.id])
        self.lastWaifuRolled[author.id] = None
        await self.bot.say("Congratulations on your marriage, " + author.display_name + " and " + waifu["name"] + "!")

        await StatsTracker.updateStat(self, "achievements", ctx, "Waifus Married")

        return

    @commands.command(pass_context=True)
    async def waifulist(self, ctx):
        """Displays your waifu list."""
        author = ctx.message.author     # set up local vars
        lastRolled = self.lastWaifuRolled.get(author.id)
        fullString = ""

        if lastRolled != None: # display the last rolled waifu
            fullString += "Last waifu rolled: " + lastRolled["name"] + "\n<" + lastRolled["img"] + ">\n"

        waifuList = self.waifuLists.get(author.id)

        if waifuList == None or len(waifuList["waifu_list"]) == 0:   # no waifus
            fullString += "No waifus married yet! Go marry some waifus!"
            await self.bot.say(fullString)
            return

        fullString += "Here are your waifus, " + author.mention + ": \n" #here here we go
        i = 0                          #so we're finally here, listing waifus for you
        for waifu in waifuList["waifu_list"]:     #if you know their names, you can join in too!
            fullString += "[" + str(i) + "] " + waifu["name"] + "\n<" + waifu["img"].replace("_", "%5F")+ ">\n" #so put your hands together, if you wanna clap
            i = i + 1   #as we take you through, this waifu list
        await self.bot.say(fullString) #WL, WAIFU LIST
        return

    @commands.command(pass_context=True)
    async def divorcewaifu(self, ctx, index: int):
        """Removes a waifu from your waifu list. Use !divorcewaifu <list index>"""

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

        cooldown = 1 * 24 * 60 * 60
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)

        if index < 0 or waifuList == None or len(waifuList["waifu_list"]) - 1 < index:
            await self.bot.say("Invalid index")
            return

        lastDelete = waifuList.get("last_delete")

        if lastDelete != None and time.time() - float(lastDelete) < cooldown: # cooldown still active

            timeRemaining = cooldown - (time.time() - float(lastDelete))       # calculate remaining time in hrs/minutes
            timeInHours = timeRemaining / (60**2)
            remainingMins = (timeInHours - int(timeInHours)) * 60

            retString = "It hasn't been 24 hours since your last divorce! Please wait " + str(int(timeInHours)) + " hours and " + str(int(remainingMins)) + " minutes before divorcing again."

            if random.randint(1, 100) == 100:      # shallus-bot is the offspring of glados
                retString += " You monster."

            await self.bot.say(retString)
            return

        await self.bot.say("Are you sure you want to divorce " + waifuList["waifu_list"][index]["name"] + "? (yes/no)") #confirm your divorce
        answer = await self.bot.wait_for_message(timeout=15, author=author)

        if answer == None or not answer.content.lower().strip() == "yes": #if it's not yes, then it's no
            await self.bot.say("I hope your marriage is happy.")
            return

        self.waifuLists[author.id]["waifu_list"].pop(index) #pop out of the list
        self.waifuLists[author.id]["last_delete"] = time.time()
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id]) #json i/o stuff
        await self.bot.say("Waifu successfully divorced.")

        await StatsTracker.updateStat(self, "achievements", ctx, "Waifus Divorced")

        return
        
        
    @commands.command(pass_context=True)
    async def renamewaifu(self, ctx, index: int, newName: str):
        """Renames a waifu in your waifu list. Use !renamewaifu <list index> <desired name>"""
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)
        if index < 0 or waifuList == None or len(waifuList["waifu_list"]) - 1 < index:
            await self.bot.say("Invalid index")
            return
        self.waifuLists[author.id]["waifu_list"][index]["name"] = newName
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        await self.bot.say("Renamed waifu #" + str(index) + " to " + newName + ".")
        return       

    @commands.command(pass_context=True)
    async def displaywaifu(self, ctx, index: int):
        """Show off your waifu! Use !displaywaifu <list index>"""
        author = ctx.message.author #set up local vars
        waifuList = self.waifuLists.get(author.id)

        if waifuList == None or len(waifuList["waifu_list"]) == 0: #no waifus
            await self.bot.say("You have no waifus! Go marry some!")
            return

        waifus = waifuList["waifu_list"]  #no waifus case already handled, direct access is safe

        if index < 0 or index > len(waifus) - 1: #out of bounds
            await self.bot.say("Invalid index")
            return

        waifu = waifus[index] #display the waifu
        displayString = author.mention + "'s waifu, " + waifu["name"] + ":\n" + waifu["img"]
        await self.bot.say(displayString)
        return


    async def getSafebooruLink(self, paramDict, user):
        reqLink = "https://safebooru.donmai.us/posts/random.json" #base link
        reqReply = requests.get(reqLink, params=paramDict, 
                                auth=HTTPBasicAuth('Shallus', 'lGVqSuermFGo9ivh4zO3_vOqgC2Sr74CkUbed4QhsSA'))
        if reqReply == None: # http request error?
            return "\n(something went wrong, please try again)"

        reqJson = reqReply.json()                        # get the json!
        waifuName = "(name not provided)"

        if reqJson["tag_count_character"] != 0:           #character name provided
            waifuName = reqJson["tag_string_character"]

        fileUrl = reqJson.get("large_file_url")          #check which file url is available
        if fileUrl == None:
            fileUrl = reqJson.get("file_url")
        if fileUrl == None:
            fileUrl = reqJson.get("preview_file_url")
        if fileUrl == None:
            return "\n(something went wrong, please try again)"


        self.lastWaifuRolled[user.id] = {"name": waifuName, "img": "https://safebooru.donmai.us" + fileUrl}
        return waifuName + "\nhttps://safebooru.donmai.us" + fileUrl


def checkFolders():
    if not os.path.exists("data/safebooru/WaifuList"):
        print("Creating directory data/safebooru/WaifuList...")
        os.makedirs("data/safebooru/WaifuList")
    if not os.path.exists("data/stats"):
        print("Creating directory data/stats...")
        os.makedirs("data/stats")


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



def setup(bot):
    checkFolders()
    bot.add_cog(Safebooru(bot))


