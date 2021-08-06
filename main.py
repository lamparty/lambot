import discord
from discord.ext import commands

lampartyBot = commands.Bot(command_prefix='!')

@lampartyBot.event
async def on_ready():
	print('lamparty-bot ready')
	pass

lampartyBot.run('ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI')