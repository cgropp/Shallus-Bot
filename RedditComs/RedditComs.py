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
        
    
    async def getMemeUrl(self, ctx, subreddit: str, randoLimit: int):
        """Gets meme url from subreddit."""
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
            memeurl = unescape(posts[randpostnum]["data"]["url"])
            if(posts[randpostnum]["data"]["stickied"] or posts[randpostnum]["data"]["over_18"] or memeurl == self.latestMeme[command]):
                posts.pop(randpostnum)
            else:
                break
        
            if (not posts):
                return ("No new and/or SFW content found!")

            randpostnum = random.randrange(len(posts))
            print(posts)

        memeurl = unescape(posts[randpostnum]["data"]["url"])
        
        # Got meme, save link to prevent us from getting same meme
        self.latestMeme[command] = memeurl
        
        # Bot print message
        # Directly link to image
        if 'imgur' in memeurl and "i.imgur" not in memeurl and "/a/" not in memeurl:
            memeurl = (memeurl + ".png")

        return str(memeurl)
     
        
    @commands.command(pass_context=True)
    async def animeme(self, ctx):
        """Posts dank animemes from /r/anime_irl."""
        memeurl = await self.getMemeUrl(ctx, "anime_irl/top", 25)
        await self.bot.say("Here's a dank animeme: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def birb(self, ctx):
        """Posts stuff from /r/birbs and /r/birdswitharms ."""
        rando5050 = random.randint(0,1)
        if (rando5050):
            memeurl = await self.getMemeUrl(ctx, "birbs", 20)
            await self.bot.say("Chirp chirp: " + str(memeurl))
        else: 
            memeurl = await self.getMemeUrl(ctx, "birdswitharms", 20)
            await self.bot.say("CHIRP CHIRP: " + str(memeurl))
        

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def cute(self, ctx):
        """Posts stuff from /r/aww."""
        memeurl = await self.getMemeUrl(ctx, "aww/top", 25)
        await self.bot.say("Aww: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def dogmeme(self, ctx):
        """Posts stuff from /r/woof_irl"""
        memeurl = await self.getMemeUrl(ctx, "woof_irl", 25)
        await self.bot.say("Woof: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def sponge(self, ctx):
        """Posts stuff from /r/bikinibottomtwitter."""
        memeurl = await self.getMemeUrl(ctx, "bikinibottomtwitter", 20)
        await self.bot.say("Fresh from Bikini Bottom: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])
        
    @commands.command(pass_context=True)
    async def wholesome(self, ctx):
        """Posts stuff from /r/wholesomememes"""
        memeurl = await self.getMemeUrl(ctx, "wholesomememes/top", 20)
        await self.bot.say("Good for the soul: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])
        
    



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


...


def setup(bot):
    if soupAvailable:
        bot.add_cog(RedditComs(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
