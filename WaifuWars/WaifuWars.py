import discord
import time
import requests
import configparser

from requests.auth import HTTPBasicAuth
from discord.ext import commands

#Stuff from Safebooru cog file
class WaifuWars:
    """Fetches images from Safebooru and allows for storing of waifus in waifulists."""
    def __init__(self, bot):
        self.bot = bot
        self.waifu1votes = 0
        self.waifu2votes = 0

        parser = configparser.ConfigParser()
        parser.read('data/auth/auth.ini')
        self.has_login = False
        if not parser.has_section("Safebooru Login"):
            print("No Safebooru credentials provided; api calls will be anonymous")
        else:
            self.loginName = parser['Safebooru Login']['Username']
            self.loginToken = parser['Safebooru Login']['Token']
            if self.loginName != "" and self.loginToken != "":
                self.has_login = True

                
    @commands.command(pass_context=True)
    async def waifuWar(self, ctx):
        """Posts a random waifu from Safebooru."""
        params = {"tags": u'1girl solo'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        linkName2 = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Debug statement, unfinished command: Vote for the superior waifu with !waifuvote 1 or !waifuvote 2 ")
        await self.bot.say("Waifu #1: " + linkName + "\nWaifu #2: " + linkName2)
     
        return

    @commands.command(pass_context=True)
    async def waifuvote(self, ctx, voteNum: int):
        """Keeps track of votes."""
        if (voteNum == 1):
            self.waifu1votes += 1
            await self.bot.say("You have voted for waifu #" + str(voteNum) + ". This waifu now has " + str(self.waifu1votes) + " vote(s)." )
        elif (voteNum == 2):
            self.waifu2votes += 1
            await self.bot.say("You have voted for waifu #" + str(voteNum) + ". This waifu now has " + str(self.waifu2votes) + " vote(s)." )
        else:
            await self.bot.say("Invalid waifu number. Please use !waifuvote 1 or !waifuvote 2")
     
        return    
        
    async def getSafebooruLink(self, paramDict, user, numTries=5):
        if numTries == 0:
            return "Either something went wrong multiple times or Safebooru is down for maintenance. Please try again at a later time."
        reqLink = "https://safebooru.donmai.us/posts/random.json" #base link
        if self.has_login:
            reqReply = requests.get(reqLink, params=paramDict, 
                                    auth=HTTPBasicAuth(self.loginName, self.loginToken))
        else:
            reqReply = requests.get(reqLink, params=paramDict)
        if reqReply == None: # http request error?
            return "\n(something went wrong, please try again)"

        try:
            reqJson = reqReply.json()                        # get the json!
        except ValueError:
            return await self.getSafebooruLink(paramDict, user, numTries - 1)

        waifuName = "(name not provided)"

        if "tag_count_character" in reqJson and reqJson["tag_count_character"] != 0: #character name provided
            waifuName = reqJson["tag_string_character"]

        fileUrl = reqJson.get("large_file_url")          #check which file url is available
        if fileUrl == None:
            fileUrl = reqJson.get("file_url")
        if fileUrl == None:
            fileUrl = reqJson.get("preview_file_url")
        if fileUrl == None:
            return await self.getSafebooruLink(paramDict, user, numTries - 1)

        return waifuName + "\nhttps://safebooru.donmai.us" + fileUrl
    


def setup(bot):
    bot.add_cog(WaifuWars(bot))