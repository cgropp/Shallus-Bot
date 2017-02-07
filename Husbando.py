try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import discord
import re
from discord.ext import commands
from random import randint
import random
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
        
class Husbando:
    """Posts husbandos from safebooru. Made by Shallus."""

    

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def husbando(self):
        """Posts husbandos from safebooru. Made by Shallus."""
        rando = randint(0,1231)
        rando = rando * 40
        #Store url of random male booru page
        url = "https://safebooru.org/index.php?page=post&s=list&tags=male+-1girl+-female+-2boys&pid=" + str(rando)
        html = urllib2.urlopen(url)
        soup = BeautifulSoup(html)
        imgs = soup.findAll("div", {"class":"thumb-pic"})
        
        list = []
        
        
        #Obtains all posts from page
        #links = soup.find_all('href')
        #await self.bot.say("url is " + url)
        for link in soup.findAll('a'):
            link = link["href"].split("href=")[-1]
            if 'safebooru' not in link and 'index' in link and 'safechibi' not in link and "tags" not in link and 'http' not in link and "id=" in link and "post" in link:
                           # await self.bot.say(link + " was added to list of links")
                            list.append("http://safebooru.org/" + link)
        
        #sets new URL to a random choice from page
       # await self.bot.say("Debug statement: about to determine url2")
        url2 = random.choice(list)
       # await self.bot.say("Debug statement: This is url2 " + url2)
        html = urllib2.urlopen(url2)
        soup = BeautifulSoup(html)
        imgs = soup.findAll("div", {"class":"thumb-pic"})
        
        #finds all images, picks a random one
        links2 = soup.find_all('img', src=True)
        for link2 in links2:
            link2 = link2["src"].split("src=")[-1]
            if 'safebooru' in link2:
                if 'safechibi' not in link2:
                    #await self.bot.say("Here is your husbando: http:" + link2)
                    #Retrieve post id
                    idindex = link2.index('?')
                    url3 = "https://safebooru.org/index.php?page=post&s=view&id=" + link2[idindex+1:]
                    #soup = class="tag-type-character"
                    #await self.bot.say("Debug statement, here is a link to the post related to your image: " + url3)
                    
                    #retrieve name of waifu
                    #Beautifulsoup stuff
                    html = urllib2.urlopen(url3)
                    soup = BeautifulSoup(html)
                    #charName = soup.find(id="tag-type-character")
                    #htmlText = soup.prettify()
                    #charIndex = htmlText.index('tag-type-character')
                   # htmlTextLim = htmlText[charIndex:charIndex+200]
                    #charIndex2 = (htmlTextLim.index("tags=")) + 5
                   # charIndexEnd = (
                   
                   #Punderful's suggestion
                    charName1 = soup.find("li", class_="tag-type-character")
                    if(charName1 is None):
                        await self.bot.say("Here is your husbando (name not provided): http:" + link2)
                    else:
                        charName2 = charName1.contents[0]
                        charName3 = str(charName2.contents)
                   # await self.bot.say("Debug statement, here is what is stored in charName list: " + str(charName))
                    
                        charNameCropped = charName3[1:len(charName3)-1]
                        await self.bot.say("Here is your husbando (name = " + charNameCropped + "): http:" + link2)
                    
                        #await self.bot.say("Here is your waifu: http:" + link2)
        #await self.bot.say("Here is your waifu: http:" + random.choice(list))
        
        
        #await self.bot.say("Here is your waifu: http:" + random.choice(list))
  
      
...

def setup(bot):
    if soupAvailable:
        bot.add_cog(Husbando(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
