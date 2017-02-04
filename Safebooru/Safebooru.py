import requests
import discord
from discord.ext import commands
import random
import json
from requests.auth import HTTPBasicAuth

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
		fileUrl = reqJson.get("large_file_url")
		if fileUrl == None:
			fileUrl = reqJson.get("file_url")
		return waifuName + "\nhttps://safebooru.donmai.us" + fileUrl]

def setup(bot):
	bot.add_cog(Safebooru(bot))
		
		
