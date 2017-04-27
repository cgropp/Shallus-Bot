import discord
from discord.ext import commands
from random import randint
import asyncio

import os
from cogs.utils.dataIO import dataIO

# Additional imports
import random
import json
import urllib.request
from urllib.request import urlopen
from html import unescape

try:  # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup

    soupAvailable = True
except:
    soupAvailable = False
import aiohttp

...

from discord.ext import commands

...

try:  # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup

    soupAvailable = True
except:
    soupAvailable = False

...





class RedditComs:
    """Fetches content from reddit."""

    def __init__(self, bot):
        self.bot = bot
        self.latestMeme = {}
        
    
    async def getRedditPost(self, ctx, subreddit: str):
        """Gets a random post from a subreddit."""
        # Store url of subreddit
        url = ("https://reddit.com/r/" + subreddit + ".json")

        # Set up http request
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Python:Shallus-Bot:v1.0 (by /u/Shallus)'
            }
        )

        # Get JSON data from website and parse for frontpage posts
        rawjson = urlopen(req).read().decode('utf8')
        parsedjson = json.loads(rawjson)
        posts = parsedjson["data"]["children"]  # List

        # Get random meme from frontpage
        randpostnum = random.randrange(len(posts))

        
        # Load in dictionary entry for latest meme if none exists
        command = ctx.message.content[1:].split(' ', 1)[0]
        if command not in self.latestMeme:
            self.latestMeme[command] = ""
        
        # Remove NSFW or sticked post from list if one come across, keep rerolling
        while (True):
            postData = posts[randpostnum]["data"]
            
            if(posts[randpostnum]["data"]["stickied"] or posts[randpostnum]["data"]["over_18"] or postData["permalink"] == self.latestMeme[command]):
                posts.pop(randpostnum)
            else:
                break
        
            if (not posts):
                return ("No new and/or SFW content found!")

            randpostnum = random.randrange(len(posts))

        postData = posts[randpostnum]["data"]
        
        # Got post, save link to prevent us from getting same meme (per command)
        self.latestMeme[command] = postData["permalink"]
        
        return postData
     
    # Checks if URL is an album, gif, or mp4
    async def checkIfImage(self, postURL: str):
        # Checks for non image
        if 'gfycat' in postURL or ".gif" in postURL or ".mp4" in postURL or "youtu" in postURL or '/a/' in postURL:
            return False
        else:
            return True
        
    # Processes url to get direct link to image 
    async def processURL(self, postURL: str):
        directURL = postURL
        # Temp solution to get direct image URL
        if 'imgur' in postURL and "i.imgur" not in postURL and "/a/" not in postURL and ".jpg" not in postURL and ".png" not in postURL:
            directURL = (postURL + ".png")
        return directURL

    # Embeds post from postData and posts embedded message in chat
    async def embedPost(self, pData):
        postData = pData
        embedData = discord.Embed()
        embedData.add_field(name=postData["title"], value=postData["url"])
        directURL = await self.processURL(postData["url"])
        embedData.set_image(url=directURL)
        await self.bot.say(embed=embedData)
    
    @commands.command(pass_context=True)
    async def animeme(self, ctx):
        """Posts dank animemes from /r/anime_irl."""
        postData = await self.getRedditPost(ctx, "anime_irl")
        URL = postData["url"]
        title = postData["title"]
        
        # Checks if URL is an image, embeds if it is
        if (await self.checkIfImage(URL)):
            await self.embedPost(pData=postData)
            
        # If URL is a gif/album/video, do not embed
        else:
            await self.bot.say(title + ": " + URL)
            
        await StatsTracker.updateStat(self, ctx, ctx.message.content[1:])
    
    @commands.command(pass_context=True)
    async def boot(self, ctx):
        """Grabs a post from /r/boottoobig."""
        postData = await self.getRedditPost(ctx, "boottoobig")
        URL = postData["url"]
        title = postData["title"]
        
        # Checks if URL is an image, embeds if it is
        if (await self.checkIfImage(URL)):
            await self.embedPost(pData=postData)
            
        # If URL is a gif/album/video, do not embed
        else:
            await self.bot.say(title + ": " + URL)
            
        await StatsTracker.updateStat(self, ctx, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def birb(self, ctx):
        """Grabs a post from /r/birbs or /r/birdswitharms ."""
        rando5050 = random.randint(0,1)
        if (rando5050):
            postData = await self.getRedditPost(ctx, "birbs")
        else: 
            postData = await self.getRedditPost(ctx, "birdswitharms")
        
        URL = postData["url"]
        title = postData["title"]
        
        # Checks if URL is an image, embeds if it is
        if (await self.checkIfImage(URL)):
            await self.embedPost(pData=postData)
            
        # If URL is a gif/album/video, do not embed
        else:
            await self.bot.say(title + ": " + URL)
            
        await StatsTracker.updateStat(self, ctx, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def cute(self, ctx):
        """Grabs a post from /r/aww."""
        postData = await self.getRedditPost(ctx, "aww")
        URL = postData["url"]
        title = postData["title"]
        
        # Checks if URL is an image, embeds if it is
        if (await self.checkIfImage(URL)):
            await self.embedPost(pData=postData)
            
        # If URL is a gif/album/video, do not embed
        else:
            await self.bot.say(title + ": " + URL)
            
        await StatsTracker.updateStat(self, ctx, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def dogmeme(self, ctx):
        """Grabs a post from /r/woof_irl"""
        postData = await self.getRedditPost(ctx, "woof_irl")
        URL = postData["url"]
        title = postData["title"]
        
        # Checks if URL is an image, embeds if it is
        if (await self.checkIfImage(URL)):
            await self.embedPost(pData=postData)
            
        # If URL is a gif/album/video, do not embed
        else:
            await self.bot.say(title + ": " + URL)
            
        await StatsTracker.updateStat(self, ctx, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def sponge(self, ctx):
        """Grabs a post from /r/bikinibottomtwitter."""
        postData = await self.getRedditPost(ctx, "bikinibottomtwitter") 
        URL = postData["url"]
        title = postData["title"]
        
        # Checks if URL is an image, embeds if it is
        if (await self.checkIfImage(URL)):
            await self.embedPost(pData=postData)
            
        # If URL is a gif/album/video, do not embed
        else:
            await self.bot.say(title + ": " + URL)
            
        await StatsTracker.updateStat(self, ctx, ctx.message.content[1:])
        
    @commands.command(pass_context=True)
    async def wholesome(self, ctx):
        """Grabs a post from /r/wholesomememes"""
        postData = await self.getRedditPost(ctx, "wholesomememes")     
        URL = postData["url"]
        title = postData["title"]
        
        # Checks if URL is an image, embeds if it is
        if (await self.checkIfImage(URL)):
            await self.embedPost(pData=postData)
            
        # If URL is a gif/album/video, do not embed
        else:
            await self.bot.say(title + ": " + URL)
            
        await StatsTracker.updateStat(self, ctx, ctx.message.content[1:])
    
        @commands.command(pass_context=True)
    async def hmmm(self, ctx):
        """Grabs a post from /r/hmmm."""
        postData = await self.getRedditPost(ctx, "hmmm")
        URL = postData["url"]
        title = postData["title"]
        
        # Checks if URL is an image, embeds if it is
        if (await self.checkIfImage(URL)):
            await self.embedPost(pData=postData)
            
        # If URL is a gif/album/video, do not embed
        else:
            await self.bot.say(title + ": " + URL)
            
        await StatsTracker.updateStat(self, ctx, ctx.message.content[1:])
    



class StatsTracker:
    async def updateStat(self, ctx, commandname):
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
            
        # Create directory for server if it doesn't already exist
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



...


def setup(bot):
    if soupAvailable:
        bot.add_cog(RedditComs(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
