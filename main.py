import discord
import pymongo
from discord.ext import commands
from discord.utils import get

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!',intents=intents)

mongoClient = pymongo.MongoClient('localhost', 27017)
lampartyDB = mongoClient.lamparty
registredUsersCollection = lampartyDB.registred_users
registredUsers = registredUsersCollection.find()

@bot.event
async def on_ready():
	global lampartyGuild 
	lampartyGuild = bot.get_guild(727245965345685514)
	
	global workCategory
	workCategory = await lampartyGuild.create_category('Анкеты')
	
	global guestRole 
	guestRole = discord.utils.get(lampartyGuild.roles, name = 'гость')
	
	print(f'ready on "{lampartyGuild}" guild.')
	#create channels for guest members
	await workCategory.set_permissions(guestRole, read_messages = True)
	await workCategory.set_permissions(bot.user, read_messages = True)
	await workCategory.set_permissions(lampartyGuild.default_role, read_messages = False)
	#get users from db and create guest member channels
	pass

@bot.event
async def on_member_join(member):
	#check user is guest or not
	if (createQuestionnaire(member.id)):
		await member.add_roles(guestRole)
		#creating guest channel on join and adding user to db
		memberChannel = await workCategory.create_text_channel(member.name, sync_permissions=False)
		await memberChannel.set_permissions(guestRole, read_messages = False)
		await memberChannel.set_permissions(member, read_messages = True)
		await memberChannel.send('Hello')
		insertIntoDB(member.id, registredUsersCollection) # move into 'add_on_server' function
	else:
		userRole = discord.utils.get(lampartyGuild.roles, name = 'йухный ауфер') # change on 'игрок'
		await member.add_roles(userRole)
	pass

@bot.command()
async def deleteQuestionnaires(ctx):
	for channel in workCategory.channels:
		await channel.delete()
	await workCategory.delete()
	pass

def insertIntoDB(discordID, collection):
	data = {
		'discordID': f'{discordID}'
	}
	global registredUsers
	registredUsers = registredUsersCollection.find()
	return collection.insert_one(data)

def createQuestionnaire(id):
	for user in registredUsers:
		print(str(id) == user['discordID'])
		if (user['discordID'] == str(id)):
			return False
	return True

bot.run('ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI' )