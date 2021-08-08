import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!',intents=intents)

class user:
	def __init__(self, discordID):
		self.id = discordID
		pass
	
	def insertIntoBD(self, collection):  # using with "import pymongo" | put inside user class
		data = {
			f'{self.discordID}': f'{self.discordID}',
			f'{self.mojangUUID}': f'{self.mojangUUID}'
		}
		return collection.insert_one(data)

@bot.event
async def on_ready():
	global lampartyGuild 
	lampartyGuild = bot.get_guild(727245965345685514)
	print(f'ready on "{lampartyGuild}" guild.')
	#create channels for guest members
	global workCategory
	workCategory = await lampartyGuild.create_category('for lambot')
	#get users from db and create guest member channels
	pass

@bot.event
async def on_member_join(member):
	#check user is guest or not
	#await member.add_roles('гость')
	await workCategory.create_text_channel(member.name)
	#creating guest channel on join and adding user to db
	pass

@bot.command()
async def turn_off(ctx):
	for channel in workCategory.channels:
		await channel.delete()
	await workCategory.delete()
	pass

bot.run('ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI' )