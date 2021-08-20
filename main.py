import discord
import pymongo
import asyncio
import time
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
	def findFormCategory(guild):
		return discord.utils.get(guild.categories, name = "Анкеты")

	def getGuildAndRole():
		global lampartyGuild
		lampartyGuild = bot.get_guild(727245965345685514)
		global playerRole
		playerRole = discord.utils.get(lampartyGuild.roles, name = 'йухный ауфер') # change on 'игрок'
		pass
	
	async def createFormCategory():
		global formsCategory
		
		if findFormCategory(lampartyGuild):
			#delete if exist
			formsCategory = findFormCategory(lampartyGuild)
			for channel in formsCategory.channels:
				await channel.delete()
			await formsCategory.delete()
		
		formsCategory = await lampartyGuild.create_category('Анкеты')
		
		await formsCategory.set_permissions(playerRole, read_messages = False)
		await formsCategory.set_permissions(bot.user, read_messages = True)
		await formsCategory.set_permissions(lampartyGuild.default_role, read_messages = True)
		
		pass


	getGuildAndRole()
	await createFormCategory()
	
	guests = getAllGuest(lampartyGuild)
	for user in guests:
		await createMemberChannel(user)

	return print(f'{bot.user.name} ready on "{lampartyGuild}" guild.')

@bot.event
async def on_member_join(member):
	if (is_registred(member)):
		await member.add_roles(playerRole)
	else:
		#creating memberChannel
		await createMemberChannel(member)
	pass

@bot.event
async def on_reaction_add(reaction, user):
	print(reaction, user)
	pass

async def register(member):
	#sendAllAnswers()
	pass

@bot.command()
async def delForms(ctx):
	for channel in formsCategory.channels:
		await channel.delete()
	await formsCategory.delete()
	pass

# def insertIntoDB(discordUser, collection):
# 	data = {
# 		'discordID': discordUser.id
# 	}
# 	return collection.insert_one(data)

def is_registred(discordUser):
	global registredUsers
	registredUsers = registredUsersCollection.find()
	for user in registredUsers:
		if (discordUser.id == user["discordID"]):
			return True
	return False

# async def add_to_server(discordUser):
# 	#inserting into DB, add to whitelist on two servers, change role, nick and delete memberChannel
# 	insertIntoDB(discordUser)
# 	#lampartyCreativeResponce = await rcon(f'whitelist add {discordUser.nick}', host='135.181.126.191', port=25658, passwd='bF52JuRi')
# 	#lampartyResonce = await rcon(f'whitelist add {discordUser.nick}', host='95.216.92.76', port=25861, passwd='1O4CnTkm')

# async def clearForm(channel):
# 	messages = channel.history()
# 	async for message in messages:
# 		#if (not message.content == helloPhrase):
# 		await message.delete()
# 	pass

async def waitReactionOnPhrase(channel, phrase):
	message = await channel.send(phrase)
	await message.add_reaction("\N{Llama}")

	def llamaEmojiCheck(reaction, user):
		return (user.name == channel.name) and (reaction.emoji == "\N{Llama}") and (message.content == phrase)

	reaction, user = await bot.wait_for("reaction_add", check = llamaEmojiCheck)
	pass

async def createMemberChannel(member):
	channel = await formsCategory.create_text_channel(member.name, sync_permissions=True)

	await channel.set_permissions(member, send_messages = False, read_messages = True)
	await channel.set_permissions(lampartyGuild.default_role, read_messages = False)
	await channel.send(helloPhrase)

	message = await channel.send(reactionPhrase)
	await message.add_reaction("\N{Llama}")
	
	print(member in message.channel.members)
	return channel
# async def form(channel):
# 	def memberChannelCheck(m):
# 		return m.author.name == channel.name and m.guild
	
# 	await channel.set_permissions(lampartyGuild.default_role, send_messages = True)
	
# 	time.sleep(10)
# 	formFinished = False
	
# 	while (not formFinished):
# 		await channel.send(questions[0])	
# 		for questionID in range(1, len(questions)):
# 			try:
# 				msg = await bot.wait_for('message', timeout = 20.0, check = memberChannelCheck)
# 			except asyncio.TimeoutError:
# 				await waitReactionOnPhrase(channel, "Повторить")
# 				print("jgak;waf")
# 				await clearForm(channel)
# 				break
# 			else:
# 				#check about cancel function
# 				await channel.send(questions[questionID])
# 				if (questionID == len(questions) - 1):
# 					formFinished = True

# 		#await bot.wait_for("message", timeout = 120.0, check=check)
		
# 	await channel.set_permissions(lampartyGuild.default_role, send_messages = False)

def getAllGuest(guild):
	guests = []
	for user in guild.members:
		if playerRole not in  user.roles and not user.bot:
			guests.append(user)
	return guests

@bot.event
async def on_member_remove(member):
	if (not is_registred(member)):
		memberChannel = discord.utils.get(formsCategory.text_channels, name = member.name)
		await memberChannel.delete()
	pass

bot.run("ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI")