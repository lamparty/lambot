import discord
import pymongo
import asyncio
from rcon import rcon
from discord.ext import commands
from discord.utils import get

#setup bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!",intents=intents)

#connection to db
mongoClient = pymongo.MongoClient("localhost", 27017)
lampartyDB = mongoClient.lamparty
registredUsersCollection = lampartyDB.registred_users

registredUsers = registredUsersCollection.find()

#phrases
helloPhrase = "Здравствуйсте, для игры на данном проекте необходимо заполнить заявку."
reactionPhrase =  "Нажмите на реакцию ниже для того, чтобы начать."

questions = [
	"Ваш ник Minecraft."
	,"Сколько вам лет?"
	, "Как вы нашли наш сервер?"
	, "Чем планируете заниматься на сервере?"
	, "Как давно вы играете в Minecraft?"
	, "Был ли у вас ранее опыт игры на подобных серверах? (Если да, то почему ушли?)"
	, "Ознакомились ли вы с правилами сервера?"
	, "Кого нужно брать с собой на вечеринку?"
]

@bot.event
async def on_ready():
	#getting guild and player role
	global lampartyGuild
	lampartyGuild = bot.get_guild(727245965345685514)
	global playerRole
	playerRole = discord.utils.get(lampartyGuild.roles, name = 'йухный ауфер') # change on 'игрок'

	#create categoryChannel for guests only
	global formsCategory
	formsCategory = await lampartyGuild.create_category('Анкеты')

	await formsCategory.set_permissions(playerRole, read_messages = False)
	await formsCategory.set_permissions(bot.user, read_messages = True)
	await formsCategory.set_permissions(lampartyGuild.default_role, read_messages = True)

	#creating text channels for every guest

	return print(f'{bot.user.name} ready on "{lampartyGuild}" guild.')

@bot.event
async def on_member_join(member):
	if (is_registred(member)):
		await member.add_roles(playerRole)
	else:
		#creating memberChannel
		memberChannel = await formsCategory.create_text_channel(member.name, sync_permissions=False)

		await memberChannel.set_permissions(member, read_messages = True)
		await memberChannel.set_permissions(lampartyGuild.default_role, read_messages = False)
		
		await waitReactionOnPhrase(memberChannel, helloPhrase)
		finishedForm = False
		while (not finishedForm):
			await form(memberChannel)
		#sendAllAnswers()
	pass

async def form(channel):
	
	await channel.send(questions[0])
	
	def check(m):
		return m.author.name == channel.name and m.guild
	for questionID in range(1, len(questions)):
		try:
			msg = await bot.wait_for('message', timeout = 120.0, check = check)
		except asyncio.TimeoutError:
			await waitReactionOnPhrase(channel, "Повторить")
			return
		else:
			await channel.send(questions[questionID])
	pass

async def waitReactionOnPhrase(channel, phrase):
	message = await channel.send(phrase)
	await message.add_reaction("\N{Llama}")
	def check(reaction, user):
		return user.name == channel.name and reaction.message.content == message.content and reaction.emoji == "\N{Llama}"
	reaction, user = await bot.wait_for("reaction_add", check = check)
	pass

async def startingForm(channel):
	def check(reaction, user):
		return user.name == channel.name and reaction.message.content == helloPhrase and reaction.emoji == "\N{Llama}"
	reaction, user = await bot.wait_for("reaction_add", check = check)
	pass
@bot.event
async def on_member_remove(member):
	if (not is_registred(member)):
		memberChannel = discord.utils.get(formsCategory.text_channels, name = member.name)
		await memberChannel.delete()
	pass

@bot.command()
async def delForms(ctx):
	for channel in formsCategory.channels:
		await channel.delete()
	await formsCategory.delete()
	pass

# @bot.command()
# async def giveRole(ctx):
# 	insertIntoDB(ctx.message.author, registredUsersCollection)
# 	pass

def insertIntoDB(discordUser, collection):
	data = {
		'discordID': discordUser.id
	}
	return collection.insert_one(data)

def is_registred(discordUser):
	global registredUsers
	registredUsers = registredUsersCollection.find()
	for user in registredUsers:
		if (discordUser.id == user["discordID"]):
			return True
	return False

async def add_to_server(discordUser):
	#inserting into DB, add to whitelist on two servers, change role, nick and delete memberChannel
	insertIntoDB(discordUser)
	#lampartyCreativeResponce = await rcon(f'whitelist add {discordUser.nick}', host='135.181.126.191', port=25658, passwd='bF52JuRi')
	#lampartyResonce = await rcon(f'whitelist add {discordUser.nick}', host='95.216.92.76', port=25861, passwd='1O4CnTkm')

bot.run("ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI")