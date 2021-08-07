import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

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
	#creating guest channel on join and adding user to db
    pass

bot.run('ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI' )