import requests
import discord
from discord.ext import commands
import random
import json
import os
import time
import configparser
import aiohttp
import atexit

from sys import maxsize
from cogs.utils.dataIO import dataIO
from requests.auth import HTTPBasicAuth


class Safebooru:
    """Fetches images from Safebooru and allows for storing of waifus in waifulists."""
    def __init__(self, bot):
        self.bot = bot
        self.waifuLists = {}
        self.lastWaifuRolled = {}
        self.LISTSIZE = 5
        self.MAXLISTS = 5
        self.TRADELISTSIZE = 10
        self.MAXTRADEREQS = 10
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

    


    @commands.command(pass_context=True)
    async def waifu(self, ctx):
        """Posts a random waifu from Safebooru."""
      #  if(ctx.message.author.id == "111629801206358016"):      #Syntax custom search, using my id for now
            #await self.bot.say("Inside if statement")
           # params = {"tags": u'loli'}         #Problem with loli tag?
       # else:
        params = {"tags": u'1girl solo'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here is your waifu, " + ctx.message.author.mention + ": " + linkName)

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])
        return

    @commands.command(pass_context=True)
    async def husbando(self, ctx):
        """Posts a random husbando from Safebooru."""
        params = {"tags": u'1boy solo'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's your husbando, " + ctx.message.author.mention + ": " + linkName)

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])
        return        
        
    @commands.command(pass_context=True)
    async def yuri(self, ctx):
        """Posts a random (SFW) yuri image from Safebooru."""
        params = {"tags": u'holding_hands yuri'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's some (SFW) yuri, " + ctx.message.author.mention + ": " + linkName)

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])
        return
        
    @commands.command(pass_context=True)
    async def yaoi(self, ctx):
        """Posts a random (SFW) yaoi image from Safebooru."""
        params = {"tags": u'yaoi'}
        linkName = await self.getSafebooruLink(params, ctx.message.author)
        await self.bot.say("Here's some (SFW) yaoi, " + ctx.message.author.mention + ": " + linkName)

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

        if len(self.waifuLists[author.id]["waifu_lists"]) >= self.MAXLISTS:                           # 5 or more lists
            await self.bot.say("You already have " + self.MAXLISTS + " lists!")
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
        """Adds another waifulist to your arsenal that you may name. Limit 5"""
        await self.addlist(ctx, name)

    @commands.command(pass_context=True)
    async def displaylastwaifu(self, ctx):
        """Shows your last rolled waifu."""
        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

        author = ctx.message.author
        waifu = self.lastWaifuRolled.get(author.id)
        if waifu == None:
            await self.bot.say("No waifu in queue to display.")
            return
        displayString = "Here is your last rolled, waifu, " + author.mention + ": " + waifu["name"] + "\n" + waifu["img"]
        await self.bot.say(displayString)
        return

    @commands.command(pass_context=True)
    async def movewaifu(self, ctx, listIndex1: int, waifuIndex: int, listIndex2: int):
        """Moves a waifu from one list to another. Use !movewaifu <index of original list> <index of waifu> <index of new list>"""

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)

        if waifuList == None or waifuList.get("waifu_lists") == None:          # no waifus
            await self.bot.say("No waifus to move. Go marry some waifus!")
            return

        indices = [listIndex1, waifuIndex, listIndex2]

        if (any(index < 1 for index in indices) or                               
               listIndex1 > len(waifuList["waifu_lists"]) or
               waifuIndex > len(waifuList["waifu_lists"][listIndex1 - 1]["list"]) or
               listIndex2 > len(waifuList["waifu_lists"])):
            await self.bot.say("Invalid index")
            return

        if len(waifuList["waifu_lists"][listIndex2 - 1]["list"]) >= self.LISTSIZE:
            await self.bot.say("Target list is full.")
            return

        self.waifuLists[author.id]["waifu_lists"][listIndex2 - 1]["list"].append( waifuList["waifu_lists"][listIndex1 - 1]["list"].pop(waifuIndex - 1) )
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id]) #json i/o stuff
        await self.bot.say("Waifu successfully moved!")

    @commands.command(pass_context=True)
    async def divorcecooldown(self, ctx):
        """Displays the remaining time before you can divorce again."""

        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)
        cooldown = 6 * 60 * 60
        
        if waifuList == None or waifuList.get("last_delete") == None:
            await self.bot.say("You've never divorced! Good on you!")

        lastDelete = waifuList["last_delete"]
        timeRemaining = cooldown - (time.time() - float(lastDelete))       # calculate remaining time in hrs/minutes
        if(timeRemaining <= 0):
            await self.bot.say("Cooldown is up. You are free to divorce a waifu.")
            return

        timeInHours = timeRemaining / (60**2)
        remainingMins = (timeInHours - int(timeInHours)) * 60
        await self.bot.say("You have " + str(int(timeInHours)) + " hours and " + str(int(remainingMins)) + " minutes before you can divorce again.")
        return 

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
            await self.addlist(ctx, None)
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
            if len(waifu_list["list"]) < self.LISTSIZE:
                break;
            i += 1

        if i >= len(self.waifuLists[author.id]["waifu_lists"]):
            if i >= self.MAXLISTS:
                await self.bot.say("Max number of waifus reached! Please divorce a waifu before marrying more.")
                return
            else:
                await self.bot.say("All lists full, but you still have room for more lists. Create another list? (yes/no)")
                answer = await self.bot.wait_for_message(timeout=15, author=author)
                if answer == None or not answer.content.lower().strip() == "yes": #if it's not yes, then it's no
                    await self.bot.say("Alright, the marriage is off.")
                    return
                await self.bot.say("Creating new list...")
                await self.addlist(ctx, None)

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
        you can only divorce a waifu if it's been more than 6 hours after your previous divorce.

        For more information, please use `!help <command>` to get a detailed description of a command or `!help` to get a list of Shallus-Bot commands,
        including those involving waifulist
        """
        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

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

        cooldown = 6 * 60 * 60
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

            retString = "It hasn't been 6 hours since your last divorce! Please wait " + str(int(timeInHours)) + " hours and " + str(int(remainingMins)) + " minutes before divorcing again."

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
        await StatsTracker.updateStat(self, "commands", ctx, ctx.message.content[1:])

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

    @commands.command(pass_context=True)
    async def movetotrade(self, ctx, listIndex: int, waifuIndex: int):
        """Move your waifu to the trade list. Use !movetotrade <index of list> <index of waifu>"""
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)

        if waifuList == None:
            await self.bot.say("You have no waifus! Go marry some!")
            return

        if waifuList.get("waifu_lists") == None:
            if waifuList.get("waifu_list") != None:
                self.handle_legacy_list(author.id)
            else:
                await self.bot.say("You have no waifus! Go marry some!")
                return

        waifus = waifuList["waifu_lists"]
        indices = [listIndex, waifuIndex]

        if any(index < 1 for index in indices) or listIndex > len(waifus) or waifuIndex > len(waifus[listIndex - 1]["list"]):
            await self.bot.say("Invalid index")
            return

        if waifuList.get("trade_list") == None:
            waifu = self.waifuLists[author.id]["waifu_lists"][listIndex - 1]["list"].pop(waifuIndex - 1)
            self.waifuLists[author.id]["trade_list"] = [waifu]
        elif len(waifuList["trade_list"]) >= self.TRADELISTSIZE:
            await self.bot.say("Your trade list is full!")
            return
        else:
            waifu = self.waifuLists[author.id]["waifu_lists"][listIndex - 1]["list"].pop(waifuIndex - 1)
            self.waifuLists[author.id]["trade_list"].append(waifu)

        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        await self.bot.say(waifu["name"] + " has been moved to the trade list.")
        return

    @commands.command(pass_context=True)
    async def movefromtrade(self, ctx, waifuIndex: int, listIndex: int):
        """Move a waifu from the trade list into a waifulist. Use !movefromtrade <index of waifu in trade list> <index of list to move to>"""
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)

        if waifuList == None:
            await self.bot.say("You have no waifus! Go marry some!")
            return

        if waifuList.get("trade_list") == None:
            await self.bot.say("No waifus in the trade list.")
            return

        indices = [waifuIndex, listIndex]

        if any(index < 1 for index in indices) or waifuIndex > len(waifuList["trade_list"]) or listIndex > len(waifuList["waifu_lists"]):
            await self.bot.say("Invalid index")
            return

        if len(waifuList["waifu_lists"][listIndex - 1]["list"]) >= self.LISTSIZE:
            await self.bot.say("Target list is full.")
            return

        tradingWith = waifuList["trade_list"][waifuIndex - 1].get("pending_trade")

        if tradingWith != None:
            await self.bot.say("This waifu is currently pending on a trade request. Cancel the request? (yes/no)")
            answer = await self.bot.wait_for_message(timeout=15, author=author)

            if answer == None or answer.content.lower().strip() != "yes":
                await self.bot.say("Move cancelled.")
                return

            targetList = self.waifuLists.get(tradingWith)
            otherWaifu = None

            if targetList != None and targetList.get("trade_reqs") != None:

                for i in range(len(targetList["trade_reqs"])):
                    if targetList["trade_reqs"][i]["user"] == author.id and targetList["trade_reqs"][i]["exchange_waifu"]["img"] == waifuList["trade_list"][waifuIndex - 1]["img"]:
                        otherWaifu = targetList["trade_reqs"][i]["target_waifu"]
                        self.waifuLists[tradingWith]["trade_reqs"].pop(i)
                        break

            if waifuList.get("trade_reqs") != None:

                for i in range(len(waifuList["trade_reqs"])):
                    if waifuList["trade_reqs"][i]["user"] == tradingWith and waifuList["trade_reqs"][i]["target_waifu"]["img"] == waifuList["trade_list"][waifuIndex - 1]["img"]:
                        otherWaifu = waifuList["trade_reqs"][i]["exchange_waifu"] 
                        self.waifuLists[author.id]["trade_reqs"].pop(i)
                        break

            if otherWaifu != None:
                for i in range(len(targetList["trade_list"])):
                    waifu = targetList["trade_list"][i]
                    if waifu["img"] == otherWaifu["img"] and waifu["pending_trade"] == author.id:
                        self.waifuLists[tradingWith]["trade_list"][i]["pending_trade"] = None
                        break


            self.waifuLists[author.id]["trade_list"][waifuIndex - 1]["pending_trade"] = None
            dataIO.save_json("data/safebooru/WaifuList/" + str(tradingWith) + ".json", self.waifuLists[tradingWith])
            target = await self.bot.get_user_info(tradingWith)
            await self.bot.send_message(target, "A trade request involving you has been cancelled. Please check your trade list and trade requests to verify.")
                

        waifu = self.waifuLists[author.id]["trade_list"].pop(waifuIndex - 1)
        self.waifuLists[author.id]["waifu_lists"][listIndex - 1]["list"].append(waifu)
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        await self.bot.say(waifu["name"] + " has been successfully moved from the trade list to " + waifuList["waifu_lists"][listIndex - 1]["name"] + ".")
        return

    @commands.command(pass_context=True)
    async def tradelist(self, ctx, user=""):
        """
        Display the trade list of someone else or yourself. Name can be supplied via mention, username, or nickname. 
        If a name is not supplied, defaults to your own list. Use !tradelist <user>
        """
        author = ctx.message.author
        if user == "":
           target = author

        else:
            mentionList = ctx.message.mentions
            if len(mentionList) != 0:
                target = mentionList[0]
            elif ctx.message.server != None:
                target = ctx.message.server.get_member_named(user)
                if target == None:
                    await self.bot.say("Target not found.")
                    return
            else:
                await self.bot.say("Target not found.")
                return

        tradeList = self.waifuLists.get(target.id)
        if tradeList == None or tradeList.get("trade_list") == None:
            await self.bot.say("No trade list found.")
            return

        fullString = "Here are " + target.display_name + "'s waifus available for trade:\n"
        i = 1
        for waifu in tradeList["trade_list"]:
            fullString += "[" + str(i) + "] " + waifu["name"] + ":\n<" + waifu["img"].replace("_", "%5F") + ">\n"
            if waifu.get("pending_trade") != None:
                fullString += "(pending trade)\n"
            i += 1

        if len(fullString) > 2000:
            strArray = fullString.split(">")
            hlfString1 = ""
            hlfString2 = ""
            for i in range(len(strArray)):
                if strArray[i] != "\n":
                    if i < len(strArray) / 2:
                        hlfString1 += strArray[i] + ">"
                    else:
                        hlfString2 += strArray[i] + ">"
            await self.bot.send_message(author, hlfString1)
            await self.bot.send_message (author, hlfString2)
            await self.bot.say("I've pm'd you the requested tradelist.")
            return
        await self.bot.say(fullString)
        return

    @commands.command(pass_context=True)
    async def sendtradereq(self, ctx, target: str, targetIndex: int, selfIndex: int):
        """Send a waifu trade request. Use !sendtradereq <name of user you want to trade with> <index of waifu you want in their list> <index of waifu in your trade list you want to trade>"""
        author = ctx.message.author
        if len(ctx.message.mentions) != 0:
            targetUser = ctx.message.mentions[0]
        else:
            if ctx.message.server != None:
                targetUser = ctx.message.server.get_member_named(target)
                if target == None:
                    await self.bot.say("Target not found.")
                    return
            else:
                await self.bot.say("Target not found.")
                return

        targetList = self.waifuLists.get(targetUser.id)
        if targetList == None or targetList.get("trade_list") == None or len(targetList["trade_list"]) <= 0:
            await self.bot.say("Target has no waifus to trade.")
            return

        userList = self.waifuLists.get(author.id)
        if userList == None or targetList.get("trade_list") == None or len(targetList["trade_list"]) <= 0:
            await self.bot.say("You have no waifus to trade.")
            return

        indices = [targetIndex, selfIndex]
        if any(index < 1 for index in indices) or targetIndex > len(targetList["trade_list"]) or selfIndex > len(userList["trade_list"]):
            await self.bot.say("Invalid index")
            return

        waifus = [targetList["trade_list"][targetIndex - 1], userList["trade_list"][selfIndex - 1]]

        if any(waifu.get("pending_trade") != None for waifu in waifus):
            await self.bot.say("One or more of the specified waifus are currently pending a trade. Please wait until the trade is decided before trying again.")
            return

        tradeReq = {"user":author.id, "target_waifu": targetList["trade_list"][targetIndex - 1], "exchange_waifu": userList["trade_list"][selfIndex - 1]}

        pendingReqs = targetList.get("trade_reqs")
        if pendingReqs != None:
            if len(pendingReqs) >= self.MAXTRADEREQS:
                await self.bot.say("This user has reached the max number of trade requests.")
                return
            self.waifuLists[targetUser.id]["trade_reqs"].append(tradeReq)
        else:
            self.waifuLists[targetUser.id]["trade_reqs"] = [tradeReq]
        self.waifuLists[targetUser.id]["trade_list"][targetIndex - 1]["pending_trade"] = author.id
        self.waifuLists[author.id]["trade_list"][selfIndex - 1]["pending_trade"] = targetUser.id
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        dataIO.save_json("data/safebooru/WaifuList/" + str(targetUser.id) + ".json", self.waifuLists[targetUser.id])
        await self.bot.say("Request to trade " + userList["trade_list"][selfIndex - 1]["name"] + " for " + targetList["trade_list"][targetIndex - 1]["name"] + " was successfully sent.")
        await self.bot.send_message(targetUser, "You have received a new trade request from " + author.name + ". Use !tradereqs to see all pending requests.")
        return

    @commands.command(pass_context=True)
    async def tradereqs(self, ctx):
        """Displays a list of your pending trade requests."""
        author = ctx.message.author
        waifuList = self.waifuLists.get(author.id)

        if waifuList == None or waifuList.get("trade_reqs") == None:
            await self.bot.say("No trade requests found.")
            return

        pendingReqs = waifuList["trade_reqs"]
        fullString = "Here are you pending trade requests, " + author.mention + ":\n"
        i = 1
        for tradeReq in pendingReqs:
            user = await self.bot.get_user_info(tradeReq["user"])
            userName = user.name
            fullString += ("[" + str(i) + "] " + userName + " requests " + \
                           tradeReq["target_waifu"]["name"] + "( " + tradeReq["target_waifu"]["img"] + " ) for "+ \
                           tradeReq["exchange_waifu"]["name"] + "( " + tradeReq["exchange_waifu"]["img"] + " )\n"
                          )
            i += 1

        await self.bot.send_message(author, fullString)
        if not ctx.message.channel.is_private:
            await self.bot.say("I have PM'd you with a list of your pending trade requests.")

        return

    @commands.command(pass_context=True)
    async def accepttrade(self, ctx, tradeIndex: int):
        """Accepts a trade request in your trade requests list. Use !accepttrade <index of trade in your trade requests list>"""
        author = ctx.message.author
        authorList = self.waifuLists.get(author.id)
        if authorList == None or authorList.get("trade_reqs") == None:
            await self.bot.say("No trade requests found.")
            return

        if tradeIndex < 1 or tradeIndex > len(authorList["trade_reqs"]):
            await self.bot.say("Invalid index")
            return

        tradeReq = authorList["trade_reqs"][tradeIndex - 1]
        user = await self.bot.get_user_info(tradeReq["user"])
        targetWaifu = tradeReq["target_waifu"]
        exchangeWaifu = tradeReq["exchange_waifu"]


        await self.bot.say("Trading " + targetWaifu["name"] + "( " + targetWaifu["img"] + " ) with " + user.name + " for " + exchangeWaifu["name"] + "( <" + exchangeWaifu["img"].replace("_", "%5F") + "> ). Continue? (yes/no)")
        answer = await self.bot.wait_for_message(timeout=15, author=author)
        if answer == None or answer.content.lower().strip() != "yes":
            await self.bot.say("Trade postponed.")
            return

        userList = self.waifuLists[user.id]
        if userList == None or userList.get("trade_list") == None:
            await self.bot.say("Target trade list not found.")
            return

        targetIndex = None
        userIndex = None

        for i in range(len(authorList["trade_list"])):
            potentialWaifu = authorList["trade_list"][i]
            if potentialWaifu["img"] == targetWaifu["img"] and potentialWaifu.get("pending_trade") != None and potentialWaifu["pending_trade"] == user.id:
                targetIndex = i
                break

        for i in range(len(userList["trade_list"])):
            potentialWaifu = userList["trade_list"][i]
            if potentialWaifu["img"] == exchangeWaifu["img"] and potentialWaifu.get("pending_trade") != None and potentialWaifu["pending_trade"] == author.id:
                userIndex = i
                break

        if targetIndex == None or userIndex == None:
            await self.bot.say("One or more waifus not found. Cancelling trade...")
            if targetIndex != None:
                self.waifuLists[author.id]["trade_list"][targetIndex]["pending_trade"] = None
            if userIndex != None:
                self.waifuLists[user.id]["trade_list"][userIndex]["pending_trade"] = None
            self.waifuLists[author.id]["trade_reqs"].pop(tradeIndex - 1)
            await self.bot.say("Trade request successfully removed.")
            return

        self.waifuLists[author.id]["trade_list"][targetIndex]["pending_trade"] = None
        self.waifuLists[user.id]["trade_list"][userIndex]["pending_trade"] = None
        tempWaifu = self.waifuLists[author.id]["trade_list"].pop(targetIndex)
        self.waifuLists[author.id]["trade_list"].append(self.waifuLists[user.id]["trade_list"].pop(userIndex))
        self.waifuLists[user.id]["trade_list"].append(tempWaifu)
        self.waifuLists[author.id]["trade_reqs"].pop(tradeIndex - 1)
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        dataIO.save_json("data/safebooru/WaifuList/" + str(user.id) + ".json", self.waifuLists[user.id])
        await self.bot.say("Successfully traded " + targetWaifu["name"] + " for " + exchangeWaifu["name"] + ".")
        await self.bot.send_message(user, "Your trade request for " + targetWaifu["name"] + " in exchange for " + exchangeWaifu["name"] + " has been accepted.")
        return

    @commands.command(pass_context=True)
    async def rejecttrade(self, ctx, tradeIndex: int):
        """Rejects a trade request in your trade list. Use !rejecttrade <index of trade in your trade request list>"""
        author = ctx.message.author
        authorList = self.waifuLists.get(author.id)
        if authorList == None or authorList.get("trade_reqs") == None:
            await self.bot.say("No trade requests found.")
            return

        if tradeIndex < 1 or tradeIndex > len(authorList["trade_reqs"]):
            await self.bot.say("Invalid index")
            return

        tradeReq = authorList["trade_reqs"][tradeIndex - 1]
        exchangeWaifu = tradeReq["exchange_waifu"]
        targetWaifu = tradeReq["target_waifu"]
        user = await self.bot.get_user_info(tradeReq["user"])

        if user == None:
            await self.bot.say("User not found. Cancelling request...")
            for i in range(len(authorList["trade_list"])):
                waifu = waifuList["trade_list"][i]
                if waifu["img"] == tradeReq["target_waifu"]["img"] and waifu.get("pending_trade") != None and waifu.get("pending_trade") == tradeReq["user"]:
                    self.waifuLists[author.id]["trade_list"][i]["pending_trade"] = None
                    break

            self.waifuLists[author.id]["trade_reqs"].pop(tradeIndex - 1)
            dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
            await self.bot.say("Request succesfully cancelled.")
            return

        userList = self.waifuLists.get(user.id)
        await self.bot.say("Canceling trade request trading " + targetWaifu["name"] + "( <" + targetWaifu["img"].replace("_", "%5F") + "> ) with " + user.name + " for " + exchangeWaifu["name"] + "( <" + exchangeWaifu["img"].replace("_", "%5F") + "> ). Continue? (yes/no)")
        answer = await self.bot.wait_for_message(timeout=15, author=author)
        if answer == None or answer.content.lower().strip() != "yes":
            await self.bot.say("Trade postponed.")
            return

        for i in range(len(authorList["trade_list"])):
            potentialWaifu = authorList["trade_list"][i]
            if potentialWaifu["img"] == targetWaifu["img"] and potentialWaifu.get("pending_trade") != None and potentialWaifu["pending_trade"] == user.id:
                self.waifuLists[author.id]["trade_list"][i]["pending_trade"] = None
                break

        for i in range(len(userList["trade_list"])):
            potentialWaifu = userList["trade_list"][i]
            if potentialWaifu["img"] == exchangeWaifu["img"] and potentialWaifu.get("pending_trade") != None and potentialWaifu["pending_trade"] == author.id:
                self.waifuLists[user.id]["trade_list"][i]["pending_trade"] = None
                break

        self.waifuLists[author.id]["trade_reqs"].pop(tradeIndex - 1)
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        dataIO.save_json("data/safebooru/WaifuList/" + str(user.id) + ".json", self.waifuLists[user.id])
        await self.bot.say("Trade request successfully rejected.")
        await self.bot.send_message(user, "Your trade request for " + targetWaifu["name"] + " in exchange for " + exchangeWaifu["name"] + " has been rejected.")
        return

    @commands.command(pass_context=True)
    async def canceltrade(self, ctx, waifuIndex: int):
        """Cancel a trade request you made. Use !canceltrade <index of waifu in your trade list in the trade>"""
        author = ctx.message.author
        authorList = self.waifuLists.get(author.id)
        if authorList == None or authorList.get("trade_list") == None:
            await self.bot.say("No trade list found.")
            return

        if waifuIndex < 1 or waifuIndex > len(authorList["trade_list"]):
            await self.bot.say("Invalid index")
            return

        tradingWaifu = authorList["trade_list"][waifuIndex - 1]
        tradingWith = tradingWaifu.get("pending_trade")
        if tradingWith == None:
            await self.bot.say("Waifu specified is not pending a trade.")
            return

        authorTradeReqs = authorList.get("trade_reqs")
        if authorTradeReqs != None:
            for tradeReq in authorTradeReqs:
                if tradeReq["target_waifu"]["img"] == tradingWaifu["img"] and tradeReq["user"] == tradingWith:
                    await self.bot.say("You did not initiate the trade for this waifu; Please use !rejecttrade to reject the pending trade request.")
                    return

        targetList = self.waifuLists.get(tradingWith)
        if targetList == None or targetList.get("trade_reqs") == None:
            await self.bot.say("Partner's list not found; cancelling pending status.")
            self.waifuLists[author.id]["trade_list"][waifuIndex - 1]["pending_trade"] = None
            dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
            return

        targetWaifu = None

        for i in range(len(targetList["trade_reqs"])):
            waifu = targetList["trade_reqs"][i]["exchange_waifu"]
            if targetList["trade_reqs"][i]["user"] == author.id and waifu["img"] == tradingWaifu["img"]:
                targetWaifu = targetList["trade_reqs"][i]["target_waifu"]
                break

        if targetWaifu == None:
            await self.bot.say("Trade req not found; cancelling pending status.")
            self.waifuLists[author.id]["trade_list"][waifuIndex - 1]["pending_trade"] = None
            dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
            return

        for j in range(len(targetList["trade_list"])):
            waifu = targetList["trade_list"][j]
            if waifu.get("pending_trade") != None and waifu["pending_trade"] == author.id and waifu["img"] == targetWaifu["img"]:
                self.waifuLists[tradingWith]["trade_list"][j]["pending_trade"] = None

        target = await self.bot.get_user_info(tradingWith)

        self.waifuLists[tradingWith]["trade_reqs"].pop(i)
        self.waifuLists[author.id]["trade_list"][waifuIndex - 1]["pending_trade"] = None
        dataIO.save_json("data/safebooru/WaifuList/" + str(author.id) + ".json", self.waifuLists[author.id])
        dataIO.save_json("data/safebooru/WaifuList/" + str(tradingWith) + ".json", self.waifuLists[tradingWith])
        await self.bot.say("Trade successfully cancelled.")
        await self.bot.send_message(target, "Trade request for " + targetWaifu["name"] + " in exchange for " + tradingWaifu["name"] + " has been cancelled.")
        return


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


        self.lastWaifuRolled[user.id] = {"name": waifuName, "img": "https://safebooru.donmai.us" + fileUrl}     # save as a "roll" for the waifulist
        if "raikou" not in fileUrl:
            return waifuName + "\nhttps://safebooru.donmai.us" + fileUrl
        else:
            return waifuName + "\n" + fileUrl

    async def closeConnection():
        await self.session.close()

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

        # Use only first word of command if stat is command
        command = commandname
        if (stattype == "commands"):
            command = command.split(' ', 1)[0]

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


