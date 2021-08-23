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
cancelPhrase = "Чтобы начать заполнять анкету заново напишите \"отмена\""
timeoutPhrase = "Время для ответа на вопрос закончилось. Для повторного заполнения анкеты нажмите на реакцию ниже."
endPhrase = "Ваша анкета отправлена на рассмотрение. Анкеты рассматриваются до 12 часов с момента подачи."
retryPhrase = "Чтобы заполнить анкету повторно, нажмите на реакцию ниже."
questions = [
	"Ваш ник Minecraft."
	#,"Сколько вам лет?"
	#, "Как вы нашли наш сервер?"
	#, "Чем планируете заниматься на сервере?"
	#, "Как давно вы играете в Minecraft?"
	#, "Был ли у вас ранее опыт игры на подобных серверах? (Если да, то почему ушли?)"
	#, "Ознакомились ли вы с правилами сервера?"
	#, "Кого нужно брать с собой на вечеринку?"

]

@bot.event
async def on_ready():
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
		def findFormCategory(guild):
			return discord.utils.get(guild.categories, name = "Анкеты")

		global formsCategory
		if findFormCategory(lampartyGuild):
			formsCategory = findFormCategory(lampartyGuild)
			for channel in formsCategory.channels:
				if (not channel.name == "все-анкеты"):
					await channel.delete()
		else:
			formsCategory = await lampartyGuild.create_category('Анкеты')

		await formsCategory.set_permissions(playerRole, read_messages = False)
		await formsCategory.set_permissions(bot.user, read_messages = True)
		await formsCategory.set_permissions(lampartyGuild.default_role, read_messages = True)
		pass
	
	async def createAllFormsChannel(category):
		def findAllFormsChannel(category):
			return discord.utils.get(category.channels, name = "все-анкеты")
		global allFormsChannel
		if (findAllFormsChannel(category)):
			allFormsChannel = findAllFormsChannel(category)
		else:
			allFormsChannel = await category.create_text_channel("все-анкеты")
		await allFormsChannel.set_permissions(lampartyGuild.default_role, read_messages = False)
		pass

	getGuildAndRole()
	await createFormCategory()
	await createAllFormsChannel(formsCategory)

	guests = getAllGuest(lampartyGuild)
	for user in guests:
		channel = await createMemberChannel(user)

	return print(f'{bot.user.name} ready on "{lampartyGuild}" guild.')

@bot.event
async def on_member_join(member):
	if (is_registred(member)):
		await member.add_roles(playerRole)
	else:
		await createMemberChannel(member)
	pass

@bot.event
async def on_reaction_add(reaction, user):
	async def register(member):
		async def getForm(channel):
			memberForm = []
			async for message in channel.history():
				if (message.content == cancelPhrase):
					memberForm.reverse()
					for answerID in range(len(memberForm)):
						memberForm[answerID] = f'"{questions[answerID]}": {memberForm[answerID]}'
						pass
					return "\n".join(memberForm)
				else:
					if (not message.author.bot):
						memberForm.append(message.content)
		
		async def clearForm(channel):
			await channel.set_permissions(member, send_messages = False, read_messages = True)
			
			async for message in channel.history():
				if (message.content == cancelPhrase): 
					await channel.set_permissions(member, send_messages = True, read_messages = True)
					return True
				else: await message.delete()
			pass
		
		async def waitReactionOnPhrase(channel, phrase):
			message = await channel.send(phrase)
			await message.add_reaction("\N{Llama}")

			def llamaEmojiCheck(reaction, user):
				return (user in reaction.message.channel.members) and (reaction.emoji == "\N{Llama}") and (message.content == phrase) and (not user.bot)

			reaction, user = await bot.wait_for("reaction_add", check = llamaEmojiCheck)
			pass
		
		async def form(channel):
			def memberChannelCheck(m):
				return (m.channel in formsCategory.channels) and (not m.author.bot)
			
			await memberChannel.set_permissions(member, send_messages = True, read_messages = True)
			
			for question in questions:
				try:
					if (not question == questions[0]):
						userMessage = await bot.wait_for('message', timeout = 120.0, check = memberChannelCheck)
				except asyncio.TimeoutError:
					await memberChannel.set_permissions(member, send_messages = False, read_messages = True)
					await waitReactionOnPhrase(channel, timeoutPhrase)
					await clearForm(channel)
					return False
				else:
					if (not question == questions[0]):
						if (userMessage.content.lower().replace(" ", "").replace("*", "").replace("_", "").replace("~", "").replace("`", "") == "отмена"):
							await clearForm(channel)
							return False
					botMessage = await channel.send(question)
			userMessage = await bot.wait_for('message', timeout = 120.0, check = memberChannelCheck)
			await channel.send(endPhrase)
			botMessage = await channel.send(retryPhrase)
			await botMessage.add_reaction("\N{Llama}")
			return True
		
		registred = False
		memberChannel = discord.utils.find(lambda c: member in c.members, formsCategory.channels)
		await memberChannel.send(cancelPhrase)
		
		while not registred:
			registred = await form(memberChannel)

		competedForm = await allFormsChannel.send(f"Анкета № number ({member.mention}) в канале {memberChannel.mention}:```\n{await getForm(memberChannel)}```")
		await competedForm.add_reaction("✔")
		await competedForm.add_reaction("❌")
		await competedForm.add_reaction("✏")

		await memberChannel.set_permissions(member, send_messages = False, read_messages = True)
		pass

	if (reaction.message.channel.category == formsCategory) and (not user.bot):
		if (reaction.emoji == "\N{Llama}") and (reaction.message.content in [reactionPhrase, retryPhrase]):
			await reaction.message.delete()
			await register(user)
			pass
		if (reaction.emoji == "✔"):
			#addToServer
			#"add role, delete channel, add to db, add to whitelist"
			async def addToServer(formMessage):
				def parseForm():
					userDiscordID = formMessage.content[formMessage.content.find("@") + 1:formMessage.content.find(">")]
					user = bot.get_user(int(userDiscordID))

					form = formMessage.content[formMessage.content.find("```") + 4:formMessage.content.rfind("```")].split("\n")
					nick = form[0] = form[0][form[0].find('"') + 1:]
					nick = nick[form[0].find(':') + 2:].lower().replace(" ","")
					
					return user, nick
				discordUser, minecraftNick = parseForm()
			await addToServer(reaction.message)
		elif (reaction.emoji == "❌"):
			#"send denied"
			pass
		elif (reaction.emoji == "✏"):
			#changeNickFromForm
			#"send user message for change nick"
			pass
	pass

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

async def createMemberChannel(member):
	channel = await formsCategory.create_text_channel(member.name, sync_permissions=True)

	await channel.set_permissions(member, send_messages = False, read_messages = True)
	await channel.set_permissions(lampartyGuild.default_role, read_messages = False)
	await channel.send(helloPhrase)

	message = await channel.send(reactionPhrase)
	await message.add_reaction("\N{Llama}")
	
	return channel

bot.run("ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI")