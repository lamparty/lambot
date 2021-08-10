import discord
import pymongo
from rcon import rcon
from discord.ext import commands
from discord.utils import get

#setup bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!',intents=intents)

#connection to db
mongoClient = pymongo.MongoClient('localhost', 27017)
lampartyDB = mongoClient.lamparty
registredUsersCollection = lampartyDB.registred_users

registredUsers = registredUsersCollection.find()

@bot.event
async def on_ready():
	#getting guild
	global lampartyGuild
	lampartyGuild = bot.get_guild(727245965345685514)

	#getting roles
	global guestRole
	global playerRole
	guestRole = discord.utils.get(lampartyGuild.roles, name = 'гость')
	playerRole = discord.utils.get(lampartyGuild.roles, name = 'йухный ауфер') # change on 'игрок'

	#create categoryChannel for guests only
	global questionnairesCategory
	questionnairesCategory = await lampartyGuild.create_category('Анкеты')

	await questionnairesCategory.set_permissions(guestRole, read_messages = True)
	await questionnairesCategory.set_permissions(bot.user, read_messages = True)
	await questionnairesCategory.set_permissions(lampartyGuild.default_role, read_messages = False)

	return print(f'{bot.user.name} ready on "{lampartyGuild}" guild.')

@bot.event
async def on_member_join(member):
	if (is_registred(member.id)):
		await member.add_roles(playerRole)
	else:
		#creating memberChannel
		memberChannel = await questionnairesCategory.create_text_channel(member.name, sync_permissions=False)

		await memberChannel.set_permissions(guestRole, read_messages = False)
		await memberChannel.set_permissions(member, read_messages = True)
		await memberChannel.send('Hello')

		await member.add_roles(guestRole)
	pass

@bot.event
async def on_member_remove(member):
	if (not is_registred(member)):
		memberChannel = discord.utils.get(questionnairesCategory.text_channels, name = member.name)
		await memberChannel.delete()
	pass

@bot.command()
async def deleteQ(ctx):
	for channel in questionnairesCategory.channels:
		await channel.delete()
	await questionnairesCategory.delete()
	pass

def insertIntoDB(discordUser, collection):
	data = {
		'discordID': f'{discordUser.id}'
	}
	global registredUsers
	registredUsers = registredUsersCollection.find()
	return collection.insert_one(data)

def is_registred(discordUser):
	for user in registredUsers:
		if (str(discordUser.id) == str(user['discordID'])):
			return True
	return False

async def add_to_server(discordUser):
	#inserting into DB, add to whitelist on two servers, change role, nick and delete memberChannel
	insertIntoDB(discordUser)
	lampartyCreativeResponce = await rcon(f'whitelist add {discordUser.nick}', host='135.181.126.191', port=25658, passwd='bF52JuRi')
	lampartyResonce = await rcon(f'whitelist add {discordUser.nick}', host='95.216.92.76', port=25861, passwd='1O4CnTkm')


bot.run('ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI' )