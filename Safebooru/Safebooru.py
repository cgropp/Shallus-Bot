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
		pageNum = random.randint(0, 500)
		params = {"tags": u'1girl solo', "limit": "50", "page": str(pageNum) }
		linkName = await self.getSafebooruLink(params)
		await self.bot.say("Here is your waifu: " + linkName)
		return 


	async def getSafebooruLink(self, paramDict):
		reqLink = "https://safebooru.donmai.us/posts.json"
		reqReply = requests.get(reqLink, params=paramDict)
		print(reqReply.url)
		reqJson = reqReply.json()
		print(len(reqJson))
		randPost = reqJson[random.randint(0, len(reqJson) - 1)]
		waifuName = ""
		if randPost["tag_count_character"] != 0:
			waifuName = randPost["tag_string_character"]
		return waifuName + "\nhttps://safebooru.donmai.us" + randPost["large_file_url"]

def setup(bot):
	bot.add_cog(Safebooru(bot))
		
		
