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
	, "Спасибо за заполнение анкеты"
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
		await register(member)
	pass

async def register(member):
	
	#creating memberChannel
	memberChannel = await formsCategory.create_text_channel(member.name, sync_permissions=False)

	await memberChannel.set_permissions(member, read_messages = True)
	await memberChannel.set_permissions(lampartyGuild.default_role, read_messages = False)
	await memberChannel.send(helloPhrase)

	await waitReactionOnPhrase(memberChannel, reactionPhrase)
	await form(memberChannel)
	#sendAllAnswers()
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

async def clearForm(channel):
	messages = channel.history()
	async for message in messages:
		if (not message.content == helloPhrase):
			await message.delete()
	pass

async def waitReactionOnPhrase(channel, phrase):
	message = await channel.send(phrase)
	await message.add_reaction("\N{Llama}")

	def llamaEmojiCheck(reaction, user):
		return (user.name == channel.name) and (reaction.emoji == "\N{Llama}") and (message.content == phrase)

	reaction, user = await bot.wait_for("reaction_add", check = llamaEmojiCheck)
	pass

async def form(channel):
	def memberChannelCheck(m):
		return m.author.name == channel.name and m.guild
	
	await channel.set_permissions(lampartyGuild.default_role, send_messages = True)
	
	formFinished = False
	
	while (not formFinished):
		print("start cycle")
		await channel.send(questions[0])	
		for questionID in range(1, len(questions)):
			try:
				msg = await bot.wait_for('message', timeout = 20.0, check = memberChannelCheck)
			except asyncio.TimeoutError:
				await waitReactionOnPhrase(channel, "Повторить")
				print("jgak;waf")
				await clearForm(channel)
				break
			else:
				await channel.send(questions[questionID])
				if (questionID == len(questions) - 1):
					formFinished = True

		#await bot.wait_for("message", timeout = 120.0, check=check)
		
	await channel.set_permissions(lampartyGuild.default_role, send_messages = False)

bot.run("ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI")