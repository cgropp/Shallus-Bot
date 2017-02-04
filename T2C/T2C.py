import discord
from discord.ext import commands
import random
import time

...

from discord.ext import commands

...



try: # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False

...

#Variables



    #Find nth occurence of word
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
    #Returns text corresponding to path

        
class T2C:
    """Translates normal text to Cirion-speak. Use !t2c <text>."""

    

    def __init__(self, bot):
        self.bot = bot

    

    
    @commands.command()
    async def t2c(self, *, message):
        """Translates normal text to Cirion-speak. Use !t2c <text>. Made by Shallus."""
        text = message
        def xd(inputString):
            if random.randint(0,100) < 50:
                return (inputString + ' xd')
            else: return inputString;
        def similar(inp):
            inpCopy = (inp)
            for x in range (0, (len(inpCopy)-1)): 
                if random.randint(0,100) < 8:
                    if (inpCopy[x] == 'n'):
                        inpCopy = (inpCopy [:(x)] + 'm' + inpCopy [(x+1):])
                    elif (inpCopy[x] == 'm'):
                        inpCopy = (inpCopy [:(x)] + 'n' + inpCopy [(x+1):])
                    elif (inpCopy[x] == 'y'):
                        inpCopy = (inpCopy [:(x)] + 'u' + inpCopy [(x+1):])
                    elif (inpCopy[x] == 'u'):
                        inpCopy = (inpCopy [:(x)] + 'y' + inpCopy [(x+1):])
                    elif (inpCopy[x] == 's'):
                        inpCopy = (inpCopy [:(x)] + 'd' + inpCopy [(x+1):])
                    elif (inpCopy[x] == 'd'):
                        inpCopy = (inpCopy [:(x)] + 's' + inpCopy [(x+1):])    
                    elif (inpCopy[x] == 'v'):
                        inpCopy = (inpCopy [:(x)] + 'c' + inpCopy [(x+1):])
                    elif (inpCopy[x] == 'o'):
                        inpCopy = (inpCopy [:(x)] + 'p' + inpCopy [(x+1):])    
                    elif (inpCopy[x] == 'p'):
                        inpCopy = (inpCopy [:(x)] + 'o' + inpCopy [(x+1):])    
                    elif (inpCopy[x] == 'e'):
                        inpCopy = (inpCopy [:(x)] + 'r' + inpCopy [(x+1):])
                    elif (inpCopy[x] == 'r'):
                        inpCopy = (inpCopy [:(x)] + 't' + inpCopy [(x+1):])    
                    elif (inpCopy[x] == 'i'):
                        inpCopy = (inpCopy [:(x)] + 'u' + inpCopy [(x+1):])    
            return inpCopy;
        
        def jumble(inp):
            newInp = (inp)
            for x in range (0, (len(newInp)-1)): 
                if(newInp[x] != ' '):
                    if(random.randint(0,100) < 10):
                        newInp = (newInp[0:(x)] + newInp[x+1]+ newInp[x] + newInp[(2+x):])
            return newInp;        
        
        def lowerCase(inp):
            return (inp.lower());
       
        msg = text
       
        #if len(msg) > 2:
        #    msg = msg[4:] # removes !t2c
        
        await self.bot.say((lowerCase(xd(jumble(similar(msg))))))

        
        #Bot print message
        #await self.bot.say("Reached end of file ")
  
...

def setup(bot):
    if soupAvailable:
        bot.add_cog(T2C(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
