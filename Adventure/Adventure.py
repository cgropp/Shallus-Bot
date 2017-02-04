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
pathChosen = 0
currentPath = 0
isDead = False


	#Find nth occurence of word
def find_nth(haystack, needle, n):
	start = haystack.find(needle)
	while start >= 0 and n > 1:
		start = haystack.find(needle, start+len(needle))
		n -= 1
	return start
	#Returns text corresponding to path
async def checkPath(self,inputPath:int):
	if inputPath == 0:
		await self.bot.say("A split road is ahead of you, do you go left (1) or right (2)?")
	if inputPath == 1:
		await self.bot.say("You went left, you died.")
		await self.bot.say("Use !startover to start over")
	if inputPath == 2:
		await self.bot.say("You went right, you approach a house with 2 doors. Open door (1) or door (2)?")
	if inputPath == 11:
		await self.bot.say("You're dead already, go start over with the !startover command")
	if inputPath == 12:
		await self.bot.say("You're dead already, go start over with the !startover command")
		
	if inputPath == 21:
		await self.bot.say("You opened door 1, inside you die.")
		await self.bot.say("Use !startover to start over")
	if inputPath == 22:
		await self.bot.say("Inside the door you find a tumbleweed. You win.")
		await self.bot.say("Use !startover to start over")		
		return	
		
class Adventure:
	"""Text based adventure. Use !startover to start over, !check to check the last chosen path, and !choose <1 or 2> to choose a path. Made by Shallus."""

	

	def __init__(self, bot):
		self.bot = bot
	
	
	
	@commands.command()
	#DEBUG: displays message for current location
	async def check(self):
		global pathChosen
		global currentPath	
		#await self.bot.say("currentPath = " + str(currentPath))
		await checkPath(self,currentPath)
	
	@commands.command()
	#Starts game over
	async def startover(self):
		global pathChosen
		global currentPath
		pathChosen = 0
		currentPath = 0
		await self.bot.say("Resetting adventure back to starting point...")
		await checkPath(self,currentPath)
		
	
	@commands.command()
	#Allows user to make a choice
	async def choose(self, choice: int):
		global pathChosen
		global currentPath
		
		#await self.bot.say("Testing choose function")
		#server = author.server
		if choice != 1 and choice != 2:
			await self.bot.say("Only '1' and '2' are valid choices, please try again.")
		else: 
			#await self.bot.say("Before this choice , you were on path " + str(currentPath))
			#await self.bot.say("You chose choice " + str(choice))
			pathChosen = choice
			currentPath = (currentPath * 10) + pathChosen
			#await self.bot.say("You are now on path " + str(currentPath))
			await checkPath(self,currentPath)
			return choice
		
	@commands.command()
	async def adventure(self):
	
	
	
		#Displays intro to the game
		async def displayIntro():
			global pathChosen
			global currentPath		
			await self.bot.say("Welcome to the text based adventure! To progress throughout the story, use '!choose 1' or '!choose 2'")
			await checkPath(self,currentPath)
			#	await self.bot.say("Choose an option: 1 or 2")
			#	return
	



	
		#Runs the game
		async def gameStart():
			#Call methods that progress the game
			pathChosen = 0
			currentPath = 0
			await displayIntro()
			if pathChosen == 1 or pathChosen == 2:
				await checkPath(self,pathChosen)
			return			
		
	
		"""Provides a text based adventure (script by Isharu)."""
		await gameStart()
		
		

		
		#Bot print message
		#await self.bot.say("Reached end of file ")
  
...

def setup(bot):
	if soupAvailable:
		bot.add_cog(Adventure(bot))
	else:
		raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
