import requests
import discord
from discord.ext import commands
import random
import json

class Safebooru:

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def waifu(self):
		params = {"tags": u'1girl solo' }
		linkName = await self.getSafebooruLink(params)
		await self.bot.say("Here is your waifu: " + linkName)
		return 


	async def getSafebooruLink(self, paramDict):
		reqLink = "https://safebooru.donmai.us/posts/random.json"
		reqReply = requests.get(reqLink, params=paramDict, auth=HTTPBasicAuth('Shallus', 'lGVqSuermFGo9ivh4zO3_vOqgC2Sr74CkUbed4QhsSA'))
		reqJson = reqReply.json()
		waifuName = ""
		if reqJson["tag_count_character"] != 0:
			waifuName = reqJson["tag_string_character"]
		return waifuName + "\nhttps://safebooru.donmai.us" + reqJson["large_file_url"]

def setup(bot):
	bot.add_cog(Safebooru(bot))
		
		
