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

    def __init__(self, bot):
        self.bot = bot
        self.waifuLists = {}
        self.lastWaifuRolled = {}
        invalidLists = []
        for userId in os.listdir("data/WaifuList"):
            if not dataIO.is_valid_json("data/WaifuList/" + userId):
                invalidLists.append(userId + "\n")
            else:
                self.waifuLists[userId[:-5]] = dataIO.load_json("data/WaifuList/" + userId)
        if not len(invalidLists) == 0:
            print("Warning: the following files were not saved properly, and have been lost: \n")
            for user in invalidLists:
                print(user)


    @commands.command(pass_context=True)
    async def waifu(self, ctx):
        params = {"tags": u'1girl solo' }
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here is your waifu: " + linkName)

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])
        return 
        
    @commands.command(pass_context=True)
    async def yuri(self, ctx):
        params = {"tags": u'holding_hands yuri' }
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's some (SFW) yuri: " + linkName)

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])
        return 
        
    @commands.command(pass_context=True)
    async def husbando(self, ctx):
        params = {"tags": u'1boy solo' }
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's your husbando: " + linkName)

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])
        return 

    @commands.command(pass_context=True)
    async def marry_waifu(self, ctx):
        author = ctx.message.author
        waifu = self.lastWaifuRolled.get(author.id)
        authorFile = "data/WaifuList/" + str(author.id) + ".json"
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
    async def waifu_list(self, ctx):
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
    async def divorce_waifu(self, ctx, index: int):
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)
        if waifuList == None or len(waifuList["waifu_list"]) < index:
            await self.bot.say("Invalid index")
            return
        lastDelete = waifuList.get("last_delete")
        if lastDelete != None and time.time() - float(lastDelete) < (5 * 24 * 60 * 60):
            await self.bot.say("It hasn't been 5 days since your last divorce! Spare some hearts, would ya?")
         #   return
        self.waifuLists[author.id]["waifu_list"].pop(index)
        self.waifuLists[author.id]["last_delete"] = time.time()
        dataIO.save_json("data/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        await self.bot.say("Waifu successfully divorced.")
        return
        
        
    async def getSafebooruLink(self, paramDict, user):
        reqLink = "https://safebooru.donmai.us/posts/random.json"
        reqReply = requests.get(reqLink, params=paramDict, auth=HTTPBasicAuth('Shallus', 'lGVqSuermFGo9ivh4zO3_vOqgC2Sr74CkUbed4QhsSA'))
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
    if not os.path.exists("data/WaifuList"):
        print("Creating directory data/WaifuList...")
        os.makedirs("data/WaifuList")
    if not os.path.exists("data/stats"):
        print("Creating directory data/stats...")
        os.makedirs("data/stats")


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
            await self.bot.say("No userdata exists for " + userid + "! Creating...")
            invalidJSON = True
        elif not dataIO.is_valid_json(datapath + "/" + userid + ".json"):
            await self.bot.say("Invalid stats JSON found. All your stats are gone forever. Blame a dev :^(")
            invalidJSON = True

        if(invalidJSON):
            data = {}
            dataIO.save_json(datapath + "/" + userid + ".json", data)


        # Read in JSON file, increment command count, and write
        userdata = dataIO.load_json(datapath + "/" + userid + ".json")
        if commandname not in userdata:
            userdata[commandname] = 0

        userdata[commandname] += 1
        dataIO.save_json(datapath + "/" + userid + ".json", userdata)

        return

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        return

def setup(bot):
    checkFolders()
    bot.add_cog(Safebooru(bot))
        
        
