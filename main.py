import discord
from discord.ext import commands
from discord.utils import get

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
	workCategory = await lampartyGuild.create_category('Анкеты')
	
	global guestRole 
	guestRole = discord.utils.get(lampartyGuild.roles, name = "гость")
	await workCategory.set_permissions(guestRole, read_messages = True)
	await workCategory.set_permissions(bot.user, read_messages = True)
	await workCategory.set_permissions(lampartyGuild.default_role, read_messages = False)
	#get users from db and create guest member channels
	pass

@bot.event
async def on_member_join(member):
	#check user is guest or not
	await member.add_roles(guestRole)
	memberChannel = await workCategory.create_text_channel(member.name, sync_permissions=False)
	await memberChannel.set_permissions(guestRole, read_messages = False)
	await memberChannel.set_permissions(member, read_messages = True)
	await memberChannel.send('Hello')
	#creating guest channel on join and adding user to db
	pass

@bot.command()
async def turnOff(ctx):
	for channel in workCategory.channels:
		await channel.delete()
	await workCategory.delete()
	pass

bot.run('ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI' )