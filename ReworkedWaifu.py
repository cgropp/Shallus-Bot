import requests
import discord
import random
import json

class ReworkedWaifu:

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ReworkedWaifu(self):
		pageNum = random.randint(0, 500)
		sbUrl = "http://safebooru.donmai.us/posts.json?tags=1girl+solo&limit=50&page="
		sbUrl += str(pageNum)	
		pageJson = (requests.get(sbUrl)).json()
		postNum = random.randint(0, len(pageJson) - 1)
		waifuUrl = "https://safebooru.donmai.us"
		waifuUrl += pageJson[postNum]["large_file_url"]
		waifuName = ""
		if pageJson[postNum][tag_count_character] != 0:
			waifuName = pageJson[postNum]["tag_string_character"]	
		await bot.say("Here is your waifu: "  + waifuName + "\n" + waifuUrl)

def setup(bot):
	bot.add_cog(ReworkedWaifu(bot))
		
		
