import discord
import time
import requests
import configparser
import time
import asyncio
import math
import aiohttp
import atexit

from requests.auth import HTTPBasicAuth
from discord.ext import commands

class WaifuWars:
    """Fetches images from Safebooru and allows for storing of waifus in waifulists."""
    def __init__(self, bot):
        self.bot = bot
        self.waifu1votes = 0
        self.waifu2votes = 0
        self.startTime = 0
        self.duration = 120
        
        #Initialize empty set for users that have already voted
        self.alreadyVoted = set({})
        #Initialize empty list for channels to announce winners to
        self.channels = set({})

        #Login stuff from Safebooru
        parser = configparser.ConfigParser()
        parser.read('data/auth/auth.ini')
        self.has_login = False
        if not parser.has_section("Safebooru Login"):
            self.session = aiohttp.ClientSession()
            print("No Safebooru credentials provided; api calls will be anonymous")
        else:
            self.loginName = parser['Safebooru Login']['Username']
            self.loginToken = parser['Safebooru Login']['Token']
            if self.loginName != "" and self.loginToken != "":
                self.session = aiohttp.ClientSession(auth=aiohttp.BasicAuth(self.loginName, self.loginToken))
                self.has_login = True
            else:
                self.session = aiohttp.ClientSession()
            atexit.register(self.closeConnection)

                
    #Starts the waifu war            
    @commands.command(pass_context=True)
    async def waifuWar(self, ctx):
        """May the best waifu win."""
        self.channels.add(ctx.message.channel)
        #Checks if a new vote should start:
        if (await self.checkTime() == False):
            return
            
        
        #Clear the set of already voted users, as a new vote has started
        self.alreadyVoted.clear()
        self.waifu1votes = 0
        self.waifu2votes = 0
        #Timer 
        
        self.startTime = time.time()

        
        #Receive waifu
        params = {"tags": u'1girl solo'}
        self.linkName = await self.getSafebooruLink(params, ctx.message.author)
        self.linkName2 = await self.getSafebooruLink(params, ctx.message.author)
        
        #Print out waifus
        await self.bot.say("Now starting a new waifu war. Vote for the superior waifu with !waifuvote 1 or !waifuvote 2 \n" + "Waifu #1: " + self.linkName + " (" + str(self.waifu1votes) + " votes)")
        #Making it two seperate print statements to ensure the previews display in correct order
        await self.bot.say("Waifu #2: " + self.linkName2 + " (" + str(self.waifu2votes) + " votes)")
        
        #Print results after time runs out
        #Don't use sleep, freezes entire bot
        await asyncio.sleep(self.duration)


        #await self.bot.say("Debug statement: timer currently set to 20 seconds, will make longer later")
        
        #Calculate winner
        if (self.waifu1votes == self.waifu2votes):
            for channel in self.channels:
                await self.bot.send_message(channel, "The waifu war resulted in a tie with " + str(self.waifu2votes) + " vote(s) for each waifu!")
            return

        elif (self.waifu1votes >self.waifu2votes):
            winner = self.linkName
            winnerVotes = str(self.waifu1votes)
            loserVotes = str(self.waifu2votes)
        else:
            winner = self.linkName2
            winnerVotes = str(self.waifu2votes)
            loserVotes = str(self.waifu1votes)
        
        
        for channel in self.channels:
            await self.bot.send_message(channel, "The waifu war is over. " + winner + " has triumphed over her opponent with " + winnerVotes + " vote(s) vs " + loserVotes + " vote(s).")    
        #Empty list of channels to send to
        self.channels.clear()
     
        return

        
    #Allows for voting
    @commands.command(pass_context=True)
    async def waifuvote(self, ctx, voteNum: int):
        """Keeps track of votes."""
        
        #Checks if they have already voted
        userid = ctx.message.author.id
        if (userid in self.alreadyVoted):
            await self.bot.say("You've already voted for a waifu, " + ctx.message.author.mention + "! Please wait until the next vote starts before voting again.")
            return


        
        #Allows user to vote for waifu #1 or waifu #2
        if (voteNum == 1):
            self.waifu1votes += 1
            #If they haven't voted, add their id to the set
            self.alreadyVoted.add(userid)
            await self.bot.say("You have voted for waifu #" + str(voteNum) + ", " + ctx.message.author.name +". This waifu now has " + str(self.waifu1votes) + " vote(s)." )
        elif (voteNum == 2):
            self.waifu2votes += 1
            self.alreadyVoted.add(userid)
            await self.bot.say("You have voted for waifu #" + str(voteNum) + ", " + ctx.message.author.name +". This waifu now has " + str(self.waifu2votes) + " vote(s)." )
        else:
            await self.bot.say("Invalid waifu number. Please use !waifuvote 1 or !waifuvote 2")
     
        return    
    
    #Safebooru file's waifu fetching code
    async def getSafebooruLink(self, paramDict, user, numTries=5):

        if numTries == 0:
            return "Either something went wrong multiple times or Safebooru is down for maintenance. Please try again at a later time."

        reqLink = "https://safebooru.donmai.us/posts/random.json" #base link
        async with self.session.get(reqLink, params=paramDict) as reqReply:    #request

            if reqReply == None:                                      # http request error?
                return "\n(something went wrong, please try again)"
            if reqReply.status != 200:                                #request didn't go through
                return "\n(error sending the request, please try again later)"

            try:
                reqJson = await reqReply.json()                        # get the json!
            except ValueError:
                return await self.getSafebooruLink(paramDict, user, numTries - 1)

            waifuName = "(name not provided)"                  #default character name assuming name isn't provided

            if "tag_count_character" in reqJson and reqJson["tag_count_character"] != 0: #character name provided
                waifuName = reqJson["tag_string_character"]

            fileUrl = reqJson.get("large_file_url")          #check which file url is available
            if fileUrl == None:
                fileUrl = reqJson.get("file_url")
            if fileUrl == None:
                fileUrl = reqJson.get("preview_file_url")
            if fileUrl == None:
                return await self.getSafebooruLink(paramDict, user, numTries - 1)  #none are available, try again


        return waifuName + "\nhttps://safebooru.donmai.us" + fileUrl
    
    #Checks if another waifuWar should be started.
    #@commands.command(pass_context=True)
    async def checkTime(self):
        self.currentTime = time.time()
        self.timePassed = self.currentTime - self.startTime
        #Check if another war should be started (No war started yet or duration has passed since last war)
        if (self.startTime == 0) or (self.timePassed >= self.duration):
            #await self.bot.say("Debug message, remove later: A sufficient amount of time has passed")
            return True
            
        else: 
            self.timeRemaining = (self.duration - self.timePassed)
            #Round up to nearest second
            await self.bot.say("The current waifu war is not over yet. Please wait " + str(math.ceil(self.timeRemaining)) + " second(s) before starting a new war." )
            await self.bot.say("The current war is Waifu #1: " + self.linkName + " (" + str(self.waifu1votes) + " votes)")
            await self.bot.say("vs. \n" + "Waifu #2: " + self.linkName2 + " (" + str(self.waifu2votes) + " votes)")
            return False
            
    async def closeConnection():
        await self.session.close()
def setup(bot):
    bot.add_cog(WaifuWars(bot))