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
	, "Ваша анкета отправлена на рассмотрение. Анкеты рассматриваются до 12 часов с момента подачи."
]

@bot.event
async def on_ready():
	def findFormCategory(guild):
		return discord.utils.get(guild.categories, name = "Анкеты")

	def getAllGuest(guild):
		guests = []
		for user in guild.members:
			if playerRole not in  user.roles and not user.bot:
				guests.append(user)
		return guests

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
		channel = await createMemberChannel(user)

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
	#print(reaction, user)
	if (reaction.emoji == "\N{Llama}") and (reaction.message.channel.category == formsCategory) and (not user.bot) and (reaction.message.content == reactionPhrase):
		await reaction.message.remove_reaction("\N{Llama}", bot.user)
		await reaction.message.delete()
		await register(user)
	pass

async def register(member):
	async def clearForm(channel):
		async for message in channel.history():
			if (not message.content == helloPhrase):
				await message.delete()
		pass
	
	async def form(channel):
		def memberChannelCheck(m):
			print(m.channel in formsCategory.channels)
			#change check
			return (m.channel in formsCategory.channels) and (not m.author.bot)
		async def deleteReactionFromPrevMessage(channel):
			async for message in channel.history():
				if message.author.bot:
					return await message.clear_reaction("\N{Llama}")

		#asking questions
		botMessage = await channel.send(questions[0])
		await botMessage.add_reaction("\N{Llama}")
		await memberChannel.set_permissions(member, send_messages = True, read_messages = True)
		for questionID in range(1, len(questions)):
			try:
				userMessage = await bot.wait_for('message', timeout = 120.0, check = memberChannelCheck)
			except asyncio.TimeoutError:
				await memberChannel.set_permissions(member, send_messages = False, read_messages = True)
				await deleteReactionFromPrevMessage(channel)
				await waitReactionOnPhrase(channel, "Время для ответа на вопрос закончилось. Для заполнения анкеты нажмите на реакцию ниже.")
				#await clearForm(channel)
				return False
			else:
				await deleteReactionFromPrevMessage(channel)
				botMessage = await channel.send(questions[questionID])
				await botMessage.add_reaction("\N{Llama}")
				if (questionID == len(questions) - 1):
					return True

	registred = False
	memberChannel = discord.utils.find(lambda c: member in c.members, formsCategory.channels)
	
	while not registred:
		registred = await form(memberChannel)
	
	await memberChannel.set_permissions(member, send_messages = False, read_messages = True)
	pass

async def waitReactionOnPhrase(channel, phrase):
	message = await channel.send(phrase)
	await message.add_reaction("\N{Llama}")

	def llamaEmojiCheck(reaction, user):
		return (user in reaction.message.channel.members) and (reaction.emoji == "\N{Llama}") and (message.content == phrase) and (not user.bot)

	reaction, user = await bot.wait_for("reaction_add", check = llamaEmojiCheck)
	pass

async def createMemberChannel(member):
	channel = await formsCategory.create_text_channel(member.name, sync_permissions=True)

	await channel.set_permissions(member, send_messages = False, read_messages = True)
	await channel.set_permissions(lampartyGuild.default_role, read_messages = False)
	await channel.send(helloPhrase)

	message = await channel.send(reactionPhrase)
	await message.add_reaction("\N{Llama}")
	
	return channel

@bot.event
async def on_member_remove(member):
	if (not is_registred(member)):
		memberChannel = discord.utils.get(formsCategory.text_channels, name = member.name)
		await memberChannel.delete()
	pass

def is_registred(discordUser):
	global registredUsers
	registredUsers = registredUsersCollection.find()
	for user in registredUsers:
		if (discordUser.id == user["discordID"]):
			return True
	return False

bot.run("ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI")