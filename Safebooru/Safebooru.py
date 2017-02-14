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
        await self.bot.say("Here is your waifu: " + linkName)

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])
        return

    @commands.command(pass_context=True)
    async def husbando(self, ctx):
        """Posts a random husbando from Safebooru."""
        params = {"tags": u'1boy solo'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's your husbando: " + linkName)

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])
        return        
        
    @commands.command(pass_context=True)
    async def yuri(self, ctx):
        """Posts a random (SFW) yuri image from Safebooru."""
        params = {"tags": u'holding_hands yuri'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's some (SFW) yuri: " + linkName)

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])
        return
        
    @commands.command(pass_context=True)
    async def yaoi(self, ctx):
        """Posts a random (SFW) yaoi image from Safebooru."""
        params = {"tags": u'yaoi'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's some (SFW) yaoi: " + linkName)

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])
        return


    @commands.command(pass_context=True)
    async def marrywaifu(self, ctx):
        """Adds the last waifu you rolled to your waifu list."""
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
            await self.bot.say("Waifu successfully married!")
            return
        if len(waifuList["waifu_list"]) >= 5:
            await self.bot.say("Max number of waifus reached! Please divorce a waifu before marrying more.")
            return
        self.waifuLists[author.id]["waifu_list"].append(waifu)
        dataIO.save_json(authorFile, self.waifuLists[author.id])
        self.lastWaifuRolled[author.id] = None
        await self.bot.say("Waifu successfully married!")
        return

    @commands.command(pass_context=True)
    async def waifulist(self, ctx):
        """Displays your waifu list."""
        author = ctx.message.author
        lastRolled = self.lastWaifuRolled.get(author.id)
        fullString = ""
        if lastRolled != None:
            fullString += "Last waifu rolled: " + lastRolled["name"] + "\n<" + lastRolled["img"] + ">\n"
        waifuList = self.waifuLists.get(author.id)
        if waifuList == None or len(waifuList["waifu_list"]) == 0:
            fullString += "No waifus married yet! Go marry some waifus!"
            await self.bot.say(fullString)
            return
        fullString += "Here are your waifus, " + author.mention + ": \n"
        i = 0
        for waifu in waifuList["waifu_list"]:
            fullString += "[" + str(i) + "] " + waifu["name"] + "\n<" + waifu["img"] + ">\n"
            i = i + 1
        await self.bot.say(fullString)
        return

    @commands.command(pass_context=True)
    async def divorcewaifu(self, ctx, index: int):
        """Removes a waifu from your waifu list. Use !divorcewaifu <list index>"""
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)
        if index < 0 or waifuList == None or len(waifuList["waifu_list"]) - 1 < index:
            await self.bot.say("Invalid index")
            return
        lastDelete = waifuList.get("last_delete")
        if lastDelete != None and time.time() - float(lastDelete) < (5 * 24 * 60 * 60):
            await self.bot.say("It hasn't been 5 days since your last divorce! Spare some hearts, would ya?")
            #   return
        self.waifuLists[author.id]["waifu_list"].pop(index)
        self.waifuLists[author.id]["last_delete"] = time.time()
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        await self.bot.say("Waifu successfully divorced.")
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

    async def getSafebooruLink(self, paramDict, user):
        reqLink = "https://safebooru.donmai.us/posts/random.json"
        reqReply = requests.get(reqLink, params=paramDict,
                                auth=HTTPBasicAuth('Shallus', 'lGVqSuermFGo9ivh4zO3_vOqgC2Sr74CkUbed4QhsSA'))
        if reqReply == None:
            return "\n(something went wrong, please try again)"
        reqJson = reqReply.json()
        waifuName = "(name not provided)"
        if reqJson["tag_count_character"] != 0:
            waifuName = reqJson["tag_string_character"]
        fileUrl = reqJson.get("large_file_url")
        if fileUrl == None:
            fileUrl = reqJson.get("file_url")
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
    async def updateStat(self, userid, commandname):
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
        if "commands" not in userdata:
            userdata["commands"] = {}
        if command not in userdata["commands"]:
            userdata["commands"][command] = 0

        userdata["commands"][command] += 1
        dataIO.save_json(datapath + "/" + userid + ".json", userdata)

        return

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        return



def setup(bot):
    checkFolders()
    bot.add_cog(Safebooru(bot))


