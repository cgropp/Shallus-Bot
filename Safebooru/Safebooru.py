import requests
import discord
from discord.ext import commands
import random
import json
import os
import time

from sys import maxsize
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
      #  if(ctx.message.author.id == "111629801206358016"):      #Syntax custom search, using my id for now
            #await self.bot.say("Inside if statement")
           # params = {"tags": u'loli'}         #Problem with loli tag?
       # else:
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

    async def addlist(self, ctx, name=None):
        author = ctx.message.author
        authorFile = "data/safebooru/WaifuList/" + str(author.id) + ".json"
        lists = self.waifuLists.get(author.id)

        if lists == None:                                                                 # first list
            self.waifuLists[author.id] = {"name": author.name, "waifu_lists": []}
        elif lists.get("waifu_list") != None:                                          # legacy list
            self.handle_legacy_list(author.id)

        if len(self.waifuLists[author.id]["waifu_lists"]) >= 5:                           # 5 or more lists
            await self.bot.say("You already have 3 lists!")
            return

        listName = name

        if listName == None:
            listName = "List " + str((len(self.waifuLists[author.id]["waifu_lists"]) + 1)) # List X, where X is its number in the list

        newList = {"name": listName, "list": []}
        self.waifuLists[author.id]["waifu_lists"].append(newList)
        dataIO.save_json(authorFile, self.waifuLists[author.id])
        await self.bot.say(listName + " successfully added!")
        return

    @commands.command(pass_context=True)
    async def createlist(self, ctx, name=None):
        """Adds another waifulist to your arsenal that you may name. Limit 3"""
        await self.addlist(ctx, name)

    @commands.command(pass_context=True)
    async def marrywaifu(self, ctx, index=maxsize):
        """Adds the last waifu you rolled to your either your first available waifu list or the specified list."""
        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

        author = ctx.message.author   
        waifu = self.lastWaifuRolled.get(author.id)
        authorFile = "data/safebooru/WaifuList/" + str(author.id) + ".json"

        if waifu == None:
            await self.bot.say("No character rolled this session.")
            return

        waifuList = self.waifuLists.get(author.id)

        if waifuList == None or waifuList.get("waifu_lists") == None or waifuList.get("waifu_list") != None:
            await self.bot.say("No waifu lists found. Making one now...")
            await self.addlist(ctx)
            self.waifuLists[author.id]["waifu_lists"][0]["list"].append(waifu)         # add to the first list
            dataIO.save_json(authorFile, self.waifuLists[author.id])
            self.lastWaifuRolled[author.id] = None                                     # can't save multiple of same waifu at same time
            await self.bot.say("Congratulations on your marriage, " + author.display_name + " and " + waifu["name"] + "!\n" + waifu["name"] + " has been added to List 1.")
            await StatsTracker.updateStat(self, "achievements", ctx, "Waifus Married")
            return

        if index != maxsize:

            if index < 1 or index > len(self.waifuLists[author.id]["waifu_lists"]):  # out of range
                await self.bot.say("Invalid index")
                return

            if len(self.waifuLists[author.id]["waifu_lists"][index - 1]["list"]) >= 5:   # list at index is full
                await self.bot.say("Specified list is full.")
                return
            
            self.waifuLists[author.id]["waifu_lists"][index - 1]["list"].append(waifu)   # success!
            dataIO.save_json(authorFile, self.waifuLists[author.id])
            self.lastWaifuRolled[author.id] = None
            listName = self.waifuLists[author.id]["waifu_lists"][index - 1]["name"]
            await self.bot.say("Congratulations on your marriage, " + author.display_name + " and " + waifu["name"] + "!\n" + waifu["name"] + " has been added to " + listName + ".")
            await StatsTracker.updateStat(self, "achievements", ctx, "Waifus Married")
            return

        i = 0
        for waifu_list in self.waifuLists[author.id]["waifu_lists"]:
            if len(waifu_list["list"]) < 5:
                break;
            i += 1

        if i >= len(self.waifuLists[author.id]["waifu_lists"]):
            await self.bot.say("Max number of waifus reached! Please divorce a waifu before marrying more.")
            return

        self.waifuLists[author.id]["waifu_lists"][i]["list"].append(waifu)
        dataIO.save_json(authorFile, self.waifuLists[author.id])
        self.lastWaifuRolled[author.id] = None
        listName = self.waifuLists[author.id]["waifu_lists"][i]["name"]
        await self.bot.say("Congratulations on your marriage, " + author.display_name + " and " + waifu["name"] + "!\n" + waifu["name"] + " has been added to " + listName + ".")

        await StatsTracker.updateStat(self, "achievements", ctx, "Waifus Married")

        return

    def handle_legacy_list(self, userId):
        tempMap = {"name": "List 1", "list": self.waifuLists[userId].pop("waifu_list")}
        self.waifuLists[userId]["waifu_lists"] = [tempMap]
        return

    @commands.command(pass_context=True)
    async def waifulist(self, ctx, index=1):
        """
        Displays one of your waifu lists. If no index is specified, it will default to the first one.
        To start a waifulist, either use !waifu to roll waifus and use !marrywaifu to marry one and start a list automatically,
        or use `!createlist <desired name>` to create a list

        To remove a waifu from a list, use `!divorcewaifu <index of list> <index of waifu in list>`; however, be wary that
        you can only divorce a waifu if it's been more than 24 hours after your previous divorce.

        For more information, please use `!help <command>` to get a detailed description of a command or `!help` to get a list of Shallus-Bot commands,
        including those involving waifulist
        """
        author = ctx.message.author     # set up local vars
        lastRolled = self.lastWaifuRolled.get(author.id)
        fullString = ""

        if lastRolled != None: # display the last rolled waifu
            fullString += "Last waifu rolled: " + lastRolled["name"] + "\n<" + lastRolled["img"] + ">\n"

        waifuList = self.waifuLists.get(author.id)

        if waifuList == None:   # no waifus
            fullString += "No waifus married yet! Go marry some waifus!"
            await self.bot.say(fullString)
            return

        if waifuList.get("waifu_lists") == None:            #no waifu lists
            if waifuList.get("waifu_list") != None:         # legacy waifu list
                self.handle_legacy_list(author.id)
            else:
                fullString += "No waifus married yet! Go marry some waifus!"
                await self.bot.say(fullString)
                return


        if index < 1 or index > len(waifuList["waifu_lists"]):
            await self.bot.say("Invalid index.")
            return

        fullString += "Here are your waifus from your list " + waifuList["waifu_lists"][index - 1]["name"] + ", " + author.mention + ": \n" #here here we go
        i = 1                          #so we're finally here, listing waifus for you
        for waifu in waifuList["waifu_lists"][index - 1]["list"]:     #if you know their names, you can join in too!
            fullString += "[" + str(i) + "] " + waifu["name"] + "\n<" + waifu["img"].replace("_", "%5F")+ ">\n" #so put your hands together, if you wanna clap
            i = i + 1   #as we take you through, this waifu list
        await self.bot.say(fullString) #WL, WAIFU LIST
        return

    @commands.command(pass_context=True)
    async def divorcewaifu(self, ctx, listIndex: int, waifuIndex: int):
        """Removes a waifu from your waifu list. Use !divorcewaifu <index of list> <index of waifu>"""

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

        cooldown = 1 * 24 * 60 * 60
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)
        if waifuList == None:
            await self.bot.say("No waifus to divorce.")
            return

        if waifuList.get("waifu_lists") == None:
            if waifuList.get("waifu_list") != None:
                self.handle_legacy_list(author.id)
            else:
                await self.bot.say("No waifus to divorce.")
                return

        if listIndex < 1 or waifuIndex < 1 or len(waifuList["waifu_lists"]) < listIndex or len(waifuList["waifu_lists"][listIndex - 1]["list"]) < waifuIndex:
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

        await self.bot.say("Are you sure you want to divorce " + waifuList["waifu_lists"][listIndex - 1]["list"][waifuIndex - 1]["name"] + "? (yes/no)") #confirm your divorce
        answer = await self.bot.wait_for_message(timeout=15, author=author)

        if answer == None or not answer.content.lower().strip() == "yes": #if it's not yes, then it's no
            await self.bot.say("I hope your marriage is happy.")
            return

        self.waifuLists[author.id]["waifu_lists"][listIndex - 1]["list"].pop(waifuIndex - 1) #pop out of the list
        self.waifuLists[author.id]["last_delete"] = time.time()
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id]) #json i/o stuff
        await self.bot.say("Waifu successfully divorced.")

        await StatsTracker.updateStat(self, "achievements", ctx, "Waifus Divorced")

        return
        
        
    @commands.command(pass_context=True)
    async def renamewaifu(self, ctx, listIndex: int, waifuIndex: int, newName: str):
        """Renames a waifu in your waifu list. Use !renamewaifu <index of list> <index of waifu> <desired name>"""
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)

        if waifuList == None:
            await self.bot.say("No waifus to rename.")
            return

        if waifuList.get("waifu_lists") == None:

            if waifuList.get("waifu_list") != None:
                self.handle_legacy_list(author.id)

            else:
                await self.bot.say("No waifus to rename.")
                return

        if listIndex < 1 or waifuIndex < 1 or len(waifuList["waifu_lists"]) < listIndex or len(waifuList["waifu_lists"][listIndex - 1]["list"]) < waifuIndex:
            await self.bot.say("Invalid index")
            return

        self.waifuLists[author.id]["waifu_lists"][listIndex - 1]["list"][waifuIndex - 1]["name"] = newName
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        await self.bot.say("Renamed waifu #" + str(waifuIndex) + " to " + newName + ".")
        return 

    @commands.command(pass_context=True)
    async def swapwaifus(self, ctx, listIndex1: int, waifuIndex1: int, listIndex2: int, waifuIndex2: int):
        """Swaps positions of two waifus. USe !swapwaifus <index of list of waifu1> <index of waifu1 in list> <index of list of waifu2>  <index of waifu2 in list>"""
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)

        if waifuList == None:
            await self.bot.say("No waifus to swap.")
            return

        if waifuList.get("waifu_lists") == None:
            
            if waifuList.get("waifu_list") != None:
                self.handle_legacy_list(author.id)

            await self.bot.say("No waifus to swap")
            return

        if ( listIndex1 < 1 or waifuIndex1 < 1 or listIndex2 < 1 or waifuIndex2 < 1 or 
             len(waifuList["waifu_lists"]) < listIndex1 or len(waifuList["waifu_lists"]) < listIndex2 or 
             len(waifuList["waifu_lists"][listIndex1 - 1]["list"]) < waifuIndex1 or 
             len(waifuList["waifu_lists"][listIndex2 - 1]["list"]) < waifuIndex2):
            await self.bot.say("Invalid index.")
            return

        tempWaifu = waifuList["waifu_lists"][listIndex1 - 1]["list"][waifuIndex1 - 1]
        self.waifuLists[author.id]["waifu_lists"][listIndex1 - 1]["list"][waifuIndex1 - 1] = waifuList["waifu_lists"][listIndex2 - 1]["list"][waifuIndex2 - 1]
        self.waifuLists[author.id]["waifu_lists"][listIndex2 - 1]["list"][waifuIndex2 - 1] = tempWaifu
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        await self.bot.say("Waifus successfully swapped!")
        return

    @commands.command(pass_context=True)
    async def renamelist(self, ctx, listIndex: int, newName: str):
        """Renames a list from your waifu lists. Use !renamelist <index of list> <desired name>"""
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)

        if waifuList == None:
            await self.bot.say("No lists to rename.")
            return

        if waifuList.get("waifu_lists") == None:

            if waifuList.get("waifu_list") != None:
                self.handle_legacy_list(author.id)

            else:
                await self.bot.say("No lists to rename.")
                return

        if listIndex < 1 or listIndex > len(waifuList["waifu_lists"]):
            await self.bot.say("Invalid index")
            return
        self.waifuLists[author.id]["waifu_lists"][listIndex - 1]["name"] = newName
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        await self.bot.say("Renamed list #" + str(listIndex) + " to " + newName + ".")

    @commands.command(pass_context=True)
    async def displaywaifu(self, ctx, listIndex: int, waifuIndex: int):
        """Show off your waifu! Use !displaywaifu <index of list> <index of waifu>"""
        author = ctx.message.author #set up local vars
        waifuList = self.waifuLists.get(author.id)

        if waifuList == None: #no waifus
            await self.bot.say("You have no waifus! Go marry some!")
            return

        if waifuList.get("waifu_lists") == None:
            if waifuList.get("waifu_list") != None:
                self.handle_legacy_list(author.id)
            else:
                await self.bot.say("You have no waifus! Go marry some!")
                return

        waifus = waifuList["waifu_lists"]  #no waifus case already handled, direct access is safe

        if listIndex < 1 or waifuIndex < 1 or listIndex > len(waifus) or waifuIndex > len(waifus[listIndex - 1]["list"]): #out of bounds
            print("length of waifus: " + str(len(waifus)) + "\nlength of waifus[listIndex][\"list\"]: " + str(len(waifus[listIndex - 1])) + "\n")
            await self.bot.say("Invalid index")
            return

        waifu = waifus[listIndex - 1]["list"][waifuIndex - 1] #display the waifu
        displayString = author.mention + "'s waifu/husbando, " + waifu["name"] + ":\n" + waifu["img"]
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
            return self.getSafebooruLink(self, paramDict, user)


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
        
        command = commandname
        if(stattype == "commands"):
            command = command.split(' ', 1)[0]

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
        if command not in userdata[stattype]:
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


