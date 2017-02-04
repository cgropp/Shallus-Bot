import requests
import discord
from discord.ext import commands
import random
import json

class Safebooru:

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def Waifu(self):
		params = {"tags": u'1girl solo' }
		linkName = await self.getSafebooruLink(params)
		await self.bot.say("Here is your waifu: " + linkName)
		return 


	async def getSafebooruLink(self, paramDict):
		reqLink = "https://safebooru.donmai.us/posts/random.json"
		reqReply = requests.get(reqLink, params=paramDict)
		reqJson = reqReply.json()
		waifuName = ""
		if randJson["tag_count_character"] != 0:
			waifuName = randJson["tag_string_character"]
		return waifuName + "\nhttps://safebooru.donmai.us" + randJson["large_file_url"]

def setup(bot):
	bot.add_cog(Safebooru(bot))
		
		
