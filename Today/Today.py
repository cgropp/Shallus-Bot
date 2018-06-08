import discord
from discord.ext import commands
import os
from datetime import datetime
import calendar
import random

import os
from cogs.utils.dataIO import dataIO


class Today:
    """Displays a random meme depending on the day of the week."""
    def __init__(self, bot):
        self.bot = bot
        
        self.lastCalled = datetime(1, 1, 1)
        self.links = None
        self.timesDefaultCalled = 0
        
        # Display each meme only once a week, then default to text output
        # TODO: Make meme restriction server-specific
        self.tuesday = ["https://68.media.tumblr.com/2a5dfe0947bd3ef3f92cb9c64553b346/tumblr_ose2osWwgB1sjq4u4o2_540.png",
        "https://68.media.tumblr.com/7dc8700395ea0124dbb193ad76c6395c/tumblr_nhydna79D21qevzlao1_500.png",
        "https://68.media.tumblr.com/ae8e46479efbd74e883213a1bffd16bc/tumblr_nh272xCXUk1qcfm5vo1_500.png",
        "https://68.media.tumblr.com/91420fd355a91e4340ea5f309be9c05a/tumblr_nlqhmy7o2P1qfe7z2o1_500.png",
        "http://i0.kym-cdn.com/photos/images/original/001/170/089/f81.jpg",
        "http://i2.kym-cdn.com/photos/images/newsfeed/001/170/096/2fb.png",
        "http://68.media.tumblr.com/206ad1c4a28f0f1d416849e47000dd04/tumblr_nghq1plfl61r3rdh2o1_500.png",
        "http://68.media.tumblr.com/6d4ab030a524a393f4037677bddc1b03/tumblr_ni8tqjgJ0q1tjvla5o1_500.jpg",
        "http://68.media.tumblr.com/a29b659dab07650460f903ad496c2473/tumblr_ndxbpeH5WI1to864no1_500.png",
        "http://68.media.tumblr.com/a1f286af2051f75091bc7e137946b718/tumblr_neoyccsGSF1qc7kjzo1_1280.jpg",
        "http://68.media.tumblr.com/2a02153aa00d515e4c5a4a04e09360dc/tumblr_ndfyvuBUfY1qj69tto1_250.jpg",
        "https://68.media.tumblr.com/15394ac95e3c74956efad9d1116f370b/tumblr_ose2osWwgB1sjq4u4o4_1280.png",
        "https://68.media.tumblr.com/5fe5cd7e5b3075d9fc53eadfa1efc1c0/tumblr_ose2osWwgB1sjq4u4o5_1280.png",
        "https://68.media.tumblr.com/b2401a650e5b1f50b7f873bb558af120/tumblr_ose2osWwgB1sjq4u4o6_1280.png",
        "https://68.media.tumblr.com/fb1b3d30ed3be46f32708d6c680906d0/tumblr_ose2osWwgB1sjq4u4o7_540.jpg",
        "http://68.media.tumblr.com/ffb71c98924901b95161e31e9703a4d1/tumblr_ose8nquL7w1sjq4u4o1_1280.png",
        "https://68.media.tumblr.com/53f283d312eaf6d89ac6b5fecf53d2fa/tumblr_nfa0u9e9er1qcwuqfo1_1280.png",
        "http://kcgreendotcom.com/littlecomis/002/comis2/guts-21.jpg",
        "https://www.youtube.com/watch?v=G8Vf5xbtGN8",
        "https://i.redd.it/169cmovuz8dz.jpg",
        "https://i.redd.it/7yk85eiqh8dz.jpg"]
        
        self.wednesday = ["http://68.media.tumblr.com/500002c984aa2093eb79995e0bd27777/tumblr_ngdcgxRkT91tdpzi3o1_1280.jpg",
        "http://68.media.tumblr.com/8d64a724e409c17a8a7c5dfab91a3f19/tumblr_o5yqv7Z2aq1rf77lbo1_1280.jpg",
        "http://i2.kym-cdn.com/photos/images/newsfeed/001/091/404/70e.jpg",
        "http://i3.kym-cdn.com/photos/images/original/001/092/074/428.png",
        "http://i2.kym-cdn.com/photos/images/original/001/094/132/180.png",
        "http://i1.kym-cdn.com/photos/images/original/001/094/131/aef.png",
        "http://i1.kym-cdn.com/photos/images/newsfeed/001/091/647/32c.png",
        "http://i2.kym-cdn.com/photos/images/newsfeed/001/179/901/bab.png",
        "https://68.media.tumblr.com/179995a5e9b26b23a5f03f0f37240327/tumblr_ose9k15lIs1sjq4u4o1_540.png",
        "https://i.redd.it/4ns1uw7c09dz.jpg",
        "https://i.imgur.com/YfktTOP.png",
        "https://i.redd.it/gh7nu1kiy8dz.png",
        "https://i.redd.it/1k4tdbjkibdz.jpg",
        "https://i.imgur.com/UPEzhnb.jpg",
        "https://i.redd.it/nlmonp6cp8dz.jpg",
        "https://i.redd.it/9xrd2odz46yz.jpg"]
        
        self.thursday = ["http://i0.kym-cdn.com/photos/images/newsfeed/001/091/402/9d6.jpg",
        "https://68.media.tumblr.com/ae1d7123d7ff24cb06bf658663b80e43/tumblr_ose2osWwgB1sjq4u4o1_540.png",
        "https://i.redd.it/6co99kbnkddz.png",
        "https://i.redd.it/h3s9mvgbacyz.jpg",
        "https://78.media.tumblr.com/cd85fe2605c950c02058af35701537e5/tumblr_p99jnqNWGA1rvzucio1_1280.jpg"]
        
        self.friday = ["https://68.media.tumblr.com/3f1d45c99115c357f0ca3a890701cfea/tumblr_ose2osWwgB1sjq4u4o3_1280.png",
        "https://twitter.com/nintendoamerica/status/698267084367785986",
        "http://i3.kym-cdn.com/photos/images/newsfeed/000/734/437/c40.png",
        "http://i3.kym-cdn.com/photos/images/newsfeed/000/960/065/2a9.png",
        "https://collegecourier.files.wordpress.com/2011/03/today-it-is-friday.jpg"]
        
        self.saturday = ["https://68.media.tumblr.com/6e6b294e90f61410728b2ff7ade7e50d/tumblr_otgepffHyb1sjq4u4o1_540.png"]
        

    
    @commands.command(pass_context=True)
    async def today(self, ctx):
        """Display a random meme depending on the day of the week. Please send new memes using !contact."""
        
        day = calendar.day_name[datetime.today().weekday()]
        current = datetime.now()
        
        # Load a fresh batch of memes if today is a new day
        currentDate = datetime(current.year, current.month, current.day)
        if self.lastCalled < currentDate:
            self.timesDefaultCalled = 0
        
            if(day == "Tuesday"):
                self.links = self.tuesday
            elif(day == "Wednesday"):
                self.links = self.wednesday
            elif(day == "Thursday"):
                self.links = self.thursday
                
                if current.hour == 21:
                    self.links.append("https://68.media.tumblr.com/a7a6f87acef8ede26749d473d9e7d263/tumblr_ose6t3Xi1U1sjq4u4o1_400.png")
            elif(day == "Friday"):
                self.links = self.friday
            else:
                self.links = []
            
            
        self.lastCalled = currentDate
        

        
        # Print default message with a 5% chance, or if there are no memes left for today
        if not self.links or random.randint(0, 19) == 0:
            output = current.strftime("Today is %A. The date is %B %d, %Y, and the time is currently %X.%f")[:-3] + "."
            
            self.timesDefaultCalled += 1
            if(self.timesDefaultCalled >= 4):
                output += "\nThis bot is in need of more today memes. Please send some using !contact :money_with_wings:"
            
            await self.bot.say(output)
        else:
            # Select random link and remove from list for this week
            elementNum = random.randrange(len(self.links))
            await self.bot.say(self.links.pop(elementNum))
        
        await StatsTracker.updateStat(self, ctx, "today")
        
        return

        
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
        
        
def setup(bot):
    bot.add_cog(Today(bot))

