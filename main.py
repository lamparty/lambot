import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
	global lampartyGuild 
	lampartyGuild = bot.get_guild(727245965345685514)
	print(f'ready on "{lampartyGuild}" guild.')
	#create channels for guest members
	wc = await lampartyGuild.create_category('for lambot')
	print(wc.name)
	pass

@bot.event
async def on_member_join(member):
	#creating
    pass

bot.run('ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI')