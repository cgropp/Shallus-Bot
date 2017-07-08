import discord
import time
import requests
import configparser
import time

from requests.auth import HTTPBasicAuth
from discord.ext import commands

#Stuff from Safebooru cog file
class WaifuWars:
    """Fetches images from Safebooru and allows for storing of waifus in waifulists."""
    def __init__(self, bot):
        self.bot = bot
        self.waifu1votes = 0
        self.waifu2votes = 0
        #Initialize empty set for users that have already voted
        self.alreadyVoted = set({})

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
        #Clear the set of already voted users, as a new vote has started
        self.alreadyVoted.clear()
        self.waifu1votes = 0
        self.waifu2votes = 0
        
        #Receive waifu
        params = {"tags": u'1girl solo'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        linkName2 = await self.getSafebooruLink(params, ctx.message.author)
        
        #Print out waifus
        await self.bot.say("Debug statement, unfinished command: Vote for the superior waifu with !waifuvote 1 or !waifuvote 2")
        await self.bot.say("Waifu #1: " + linkName)
        # Making it two seperate print statements to ensure the previews display in correct order
        await self.bot.say("Waifu #2: " + linkName2)
        
        
        #TODO: Fix later to not stall entire bot
        
        # Print results after time runs out
        # Don't use sleep, freezes entire bot
        
        # Calculate winner
        # await self.bot.say("Debug statement: timer currently set to 30 seconds, will make longer later")
        
        
        # if (self.waifu1votes == self.waifu2votes):
            # await self.bot.say("The waifu war resulted in a tie with " +self.waifu2votes + " votes for each waifu!")
            # return

        # elif (self.waifu1votes >self.waifu2votes):
            # winner = linkName
            # winnerVotes = self.waifu2votes
            # loserVotes = self.waifu2votes
        # else:
            # winner = linkName2
            # winnerVotes =self.waifu2votes
            # loserVotes = self.waifu2votes

        # await self.bot.say("The waifu war is over. " + winner + "has triumphed over her opponent with " + winnerVotes + " votes vs " + loserVotes + " votes.")
     
        return

    @commands.command(pass_context=True)
    async def waifuvote(self, ctx, voteNum: int):
        """Keeps track of votes."""
        
        #Checks if they have already voted
        userid = ctx.message.author.id
        if (userid in self.alreadyVoted):
            await self.bot.say("You've already voted for a waifu, " + ctx.message.author.mention + "! Please wait until the next vote starts before voting again.")
            return
        #If they haven't voted, add their id to the set
        else:
            self.alreadyVoted.add(userid)
        
        #Allows user to vote for waifu #1 or waifu #2
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