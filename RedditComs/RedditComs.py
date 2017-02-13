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


# Find nth occurence of word
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start

    # Gets meme url from subreddit


async def getMemeUrl(subreddit: str, randoLimit: int):
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

    # Remove NSFW or sticked post from list if one come across, keep rerolling
    rolls = 0
    while (posts[randpostnum]["data"]["stickied"] or posts[randpostnum]["data"]["over_18"]):
        posts.pop(randpostnum)
        if (not posts):
            return ("No SFW content found!")

        randpostnum = random.randrange(len(posts))
        print(posts)

    memeurl = unescape(posts[randpostnum]["data"]["url"])

    # Bot print message
    # Directly link to image
    if 'imgur' in memeurl and "i.imgur" not in memeurl and "/a/" not in memeurl:
        memeurl = (memeurl + ".png")

    return str(memeurl)


class RedditComs:
    """Fetches content from reddit."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def animeme(self, ctx):
        """Posts dank animemes from /r/anime_irl."""
        memeurl = await getMemeUrl("anime_irl/top", 25)
        await self.bot.say("Here's a dank animeme: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def birb(self, ctx):
        """Posts stuff from /r/birbs."""
        memeurl = await getMemeUrl("birbs", 20)
        await self.bot.say("Chirp chirp: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def cute(self, ctx):
        """Posts stuff from /r/aww."""
        memeurl = await getMemeUrl("aww/top", 25)
        await self.bot.say("Aww: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def dogmeme(self, ctx):
        """Posts stuff from /r/woof_irl"""
        memeurl = await getMemeUrl("woof_irl", 25)
        await self.bot.say("Woof: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def sponge(self, ctx):
        """Posts stuff from /r/bikinibottomtwitter."""
        memeurl = await getMemeUrl("bikinibottomtwitter", 20)
        await self.bot.say("Fresh from Bikini Bottom: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])

    @commands.command(pass_context=True)
    async def bpt(self, ctx):
        """Posts stuff from /r/blackpeopletwitter."""
        memeurl = await getMemeUrl("blackpeopletwitter/top", 25)
        await self.bot.say("Here's a post from /r/blackpeopletwitter: " + str(memeurl))

        await StatsTracker.updateStat(self, ctx.message.author.id, ctx.message.content[1:])


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
        if commandname not in userdata["commands"]:
            userdata["commands"][commandname] = 0

        userdata["commands"][commandname] += 1
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
