import requests
import discord
from discord.ext import commands
import random
import json
import os 

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
        return 
        
    @commands.command(pass_context=True)
    async def yuri(self, ctx):
        params = {"tags": u'holding_hands yuri' }
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's some (SFW) yuri: " + linkName)
        return 
        
    @commands.command(pass_context=True)
    async def husbando(self, ctx):
        params = {"tags": u'1boy solo' }
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's your husbando: " + linkName)
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
        if lastRolled != None:
            await self.bot.say("Last waifu rolled: " + lastRolled["name"] + "\n" + lastRolled["img"] + "\n")
        waifuList = self.waifuLists.get(author.id)
        if waifuList == None or len(waifuList["waifu_list"]) == 0:
            await self.bot.say("No waifus married yet! Go marry some waifus!")
            return
        await self.bot.say("Here are your waifus: \n")
        i = 0
        for waifu in waifuList["waifu_list"]:
            await self.bot.say("[" + str(i) + "] " + waifu["name"] + "\n" + waifu["img"] + "\n")
            i = i + 1
        return

    @commands.command(pass_context=True)
    async def divorce_waifu(self, ctx, index: int):
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)
        if waifuList == None or len(waifuList["waifu_list"]) < index:
            await self.bot.say("Invalid index")
            return
        self.waifuLists[author.id]["waifu_list"].pop(index)
        dataIO.save_json("data/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        await self.bot.say("Waifu successfully divorced.")
        return
        
        
    async def getSafebooruLink(self, paramDict, user):
        reqLink = "https://safebooru.donmai.us/posts/random.json"
        reqReply = requests.get(reqLink, params=paramDict, auth=HTTPBasicAuth('Shallus', 'lGVqSuermFGo9ivh4zO3_vOqgC2Sr74CkUbed4QhsSA'))
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

    

def setup(bot):
    checkFolders()
    bot.add_cog(Safebooru(bot))
        
        
