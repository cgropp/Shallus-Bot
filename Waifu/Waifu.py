try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import discord
import re
from discord.ext import commands
from random import randint
import random
import time
        
try: # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False
import aiohttp

...

from discord.ext import commands

...

try: # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False

...
    #Find nth occurence of word
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
        
    #Gets page
async def getPage():
    rando = randint(0,16040)
    rando = rando * 40
    #Store url of random female booru page
    url = "https://safebooru.org/index.php?page=post&s=list&tags=1girl+-1boy+-male+-2boys+-2girls+-cameltoe&pid=" + str(rando)
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html)

    return soup
                
#Gets page
#async def getPostLinks(haystack, needle, n): 
   # return imgs
                
        
class Waifu:
    """Posts waifus from safebooru. Made by Shallus."""

    

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def waifu(self):
        """Posts waifus from safebooru.  Made by Shallus."""
        #await self.bot.say("Debug statement 0")

        start_time = time.time() #Debug timer
        soup = await getPage();
        #await self.bot.say(" Debug statement: runtime of getPage() is--- %s seconds ---" % (time.time() - start_time))
       # await self.bot.say("Debug statement 1")
        list = []
        
        
        #Obtains all posts from page
        #links = soup.find_all('href')
        #await self.bot.say("url is " + url)
        for link in soup.findAll('a'):
            link = link["href"].split("href=")[-1]
            if 'safebooru' not in link and 'index' in link and 'safechibi' not in link and "tags" not in link and 'http' not in link and "id=" in link and "post" in link:
                           # await self.bot.say(link + " was added to list of links")
                            list.append("http://safebooru.org/" + link)
                            #await self.bot.say("Debug statement 2")
        
        #sets new URL to a random choice from page
        #await self.bot.say("Debug statement: about to determine url2")
        url2 = random.choice(list)
        html = urllib2.urlopen(url2)
        soup = BeautifulSoup(html)
        #await self.bot.say("Debug statement 3")
        #finds all images, picks a random one
        links2 = soup.find_all('img', src=True)
        for link2 in links2:
            link2 = link2["src"].split("src=")[-1]
            if 'safebooru' in link2:
                if 'safechibi' not in link2:
                    
                    
                    
                    #Retrieve post id
                    idindex = link2.index('?')
                    url3 = "https://safebooru.org/index.php?page=post&s=view&id=" + link2[idindex+1:]
                    #soup = class="tag-type-character"
                    #await self.bot.say("Debug statement, here is a link to the post related to your image: " + url3)
                    
                    #retrieve name of waifu
                    #Beautifulsoup stuff
                    html = urllib2.urlopen(url3)
                    soup = BeautifulSoup(html)
                   
                   #Punderful's suggestion
                    charName1 = soup.find("li", class_="tag-type-character")
                    if(charName1 is None):
                        await self.bot.say("Here is your waifu (name not provided): http:" + link2)
                    else:
                        charName2 = charName1.contents[0]
                        charName3 = str(charName2.contents)
                   # await self.bot.say("Debug statement, here is what is stored in charName list: " + str(charName))
                    
                        charNameCropped = charName3[1:len(charName3)-1]
                        await self.bot.say("Here is your waifu (name = " + charNameCropped + "): http:" + link2)
                    

  
        #await self.bot.say(" Debug statement: total runtime is--- %s seconds ---" % (time.time() - start_time))
...

def setup(bot):
    if soupAvailable:
        bot.add_cog(Waifu(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
