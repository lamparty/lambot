import discord
import pymongo
import asyncio
import requests
from rcon import rcon
from discord.ext import commands
from discord.utils import get

#setup bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!",intents=intents)

#connection to db
mongoClient = pymongo.MongoClient("mongodb://toombez:yTcrf;e@3.143.215.30:27017/?authSource=admin")
lampartyDB = mongoClient.lamparty
registredUsersCollection = lampartyDB.registred_users

registredUsers = registredUsersCollection.find()

#rcon
class rconConnection():
	def __init__(self, host, port, passwd):
		self.host = host
		self.port = port
		self.passwd = passwd
	async def executeCommand(self, command):
		await rcon(command, host = self.host, port= self.port, passwd= self.passwd)
lamparty = rconConnection("95.216.92.76", 25861, "1O4CnTkm")
lampartyCreative = rconConnection("135.181.126.191", 25658, "bF52JuRi")

#phrases
helloPhrase = "Здравствуйсте, для игры на данном проекте необходимо заполнить заявку."
reactionPhrase =  "Нажмите на реакцию ниже для того, чтобы начать."
cancelPhrase = "Чтобы начать заполнять анкету заново напишите \"отмена\""
timeoutPhrase = "Время для ответа на вопрос закончилось. Для повторного заполнения анкеты нажмите на реакцию ниже."
endPhrase = "Ваша анкета отправлена на рассмотрение. Анкеты рассматриваются до 12 часов с момента подачи."
retryPhrase = "Чтобы заполнить анкету повторно, нажмите на реакцию ниже."
addedOnServerPhrase = "Вы добавлены на сервер, приятной игры!"
sendFormError = "При отправке анкеты произошла ошибка. Заполните анкету повторно."
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
	def getAllGuest(guild):
		guests = []
		for user in guild.members:
			if playerRole not in  user.roles and not user.bot:
				guests.append(user)
		return guests

	def getGuildAndRole():
		global lampartyGuild
		lampartyGuild = bot.get_guild(880870316870615100)
		global playerRole
		playerRole = discord.utils.get(lampartyGuild.roles, name = 'Игрок') # change on 'игрок'
		global adminRole
		adminRole = discord.utils.get(lampartyGuild.roles, name = 'Администратор')
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
		async def setMinecraftNick():
			mojangUUID = is_registred(member)["mojangUUID"]
			nicks = requests.get(
				f"https://api.mojang.com/user/profiles/{mojangUUID}/names").json()
			minecraftNick = nicks[len(nicks) - 1]["name"]
			await member.edit(nick = minecraftNick)

		await member.add_roles(playerRole)
		await setMinecraftNick()
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
						try:
							memberForm[answerID] = f'"{questions[answerID]}": {memberForm[answerID]}'
						except IndexError:
							await channel.send(sendFormError)
							return
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
			def llamaEmojiCheck(reaction, user):
				return (user in reaction.message.channel.members) and (reaction.emoji == "\N{Llama}") and (message.content == phrase) and (not user.bot)

			message = await channel.send(phrase)
			await message.add_reaction("\N{Llama}")

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
		if (memberChannel):
			await memberChannel.send(cancelPhrase)
			
			while not registred:
				registred = await form(memberChannel)

			await memberChannel.set_permissions(member, send_messages = False, read_messages = True)
			
			if (await getForm(memberChannel)):
				competedForm = await allFormsChannel.send(f"Анкета № number ({member.mention}) в канале {memberChannel.mention}:```\n{await getForm(memberChannel)}```")
				await competedForm.add_reaction("✔")
				await competedForm.add_reaction("❌")
				await competedForm.add_reaction("✏")
		pass
	
	async def parseForm(formMessage):
			userFormChannelID = formMessage.content[formMessage.content.find("#") + 1:formMessage.content.find(":") - 1]
			userFormChannel = lampartyGuild.get_channel(int(userFormChannelID))

			userDiscordID = formMessage.content[formMessage.content.find("@") + 1:formMessage.content.find(">")]
			user = lampartyGuild.get_member(int(userDiscordID))
			
			if (reaction.emoji in ["✔", "❌"]):
				form = formMessage.content[formMessage.content.find("```") + 4:formMessage.content.rfind("```")].split("\n")
				nick = form[0] = form[0][form[0].find('"') + 1:]
				nick = nick[form[0].find(':') + 2:].lower().replace(" ","")
			else:
				def nickCheck(message):
					return not message.author.bot
				await allFormsChannel.send("Напишите ник, на который нужно заменить")
				nickMessage = await bot.wait_for("message", check = nickCheck)
				nick = nickMessage.content.replace(" ", "")
			
			return user, userFormChannel, userDiscordID, nick
	
	async def addOnServer(formMessage):
		
		async def insertIntoDB(discordUserID, minecraftUUID, collection):
			data = {
				"discordID": discordUserID,
				"mojangUUID": minecraftUUID
			}
			registredUsers = registredUsersCollection.find()
			return collection.insert_one(data)	
		
		async def getMojangUUID(minecraftNick):
			mojangUUID = requests.get(
				f'https://api.mojang.com/users/profiles/minecraft/{minecraftNick}').json()['id']
			return mojangUUID

		discordUser, discordUserFormChannel, discordUserID, minecraftNick = await parseForm(formMessage)
		if not is_registred(discordUser):
			if discordUser:
				await discordUser.add_roles(playerRole)
				await discordUser.edit(nick = minecraftNick)
				await discordUser.send(addedOnServerPhrase)

			if discordUserFormChannel:
				await discordUserFormChannel.delete()
			await insertIntoDB(discordUserID, await getMojangUUID(minecraftNick), registredUsersCollection)

			await lamparty.executeCommand(f"whitelist add {minecraftNick}")
		pass

	async def rejectForm(formMessage):
		def reasonCheck(message):
			return not message.author.bot
		discordUser, discordUserFormChannel, discordUserID, minecraftNick = await parseForm(formMessage)
		await allFormsChannel.send("Напишите причину отклонения анкеты")
		reasonMessage = await bot.wait_for("message", check = reasonCheck)
		await discordUser.send(f"Ваша анкета на сервер lamparty не подходит по причине: {reasonMessage.content}.\nВы также можете повторно заполнить анкету.")
		pass
	
	if (reaction.message.channel.category == formsCategory) and (not user.bot):
		if (reaction.emoji == "\N{Llama}") and (reaction.message.content in [reactionPhrase, retryPhrase] and not playerRole in user.roles):
			await reaction.message.delete()
			await register(user)
			pass
		if (reaction.emoji == "✔"):
			await addOnServer(reaction.message)
		elif (reaction.emoji == "❌"):
			await rejectForm(reaction.message)
			pass
		elif (reaction.emoji == "✏"):
			await addOnServer(reaction.message)
			pass
	pass

@bot.event
async def on_member_remove(member):
	if (not is_registred(member)):
		memberChannel = discord.utils.get(formsCategory.text_channels, name = member.name)
		await memberChannel.delete()
	pass

def is_registred(discordUser):
	registredUsers = registredUsersCollection.find()
	for user in registredUsers:
		if (str(discordUser.id) == str(user["discordID"])):
			print("registred")
			return user
	return False

async def createMemberChannel(member):
	channel = await formsCategory.create_text_channel(member.name, sync_permissions=True)

	await channel.set_permissions(member, send_messages = False, read_messages = True)
	await channel.set_permissions(lampartyGuild.default_role, read_messages = False)
	await channel.send(helloPhrase)

	message = await channel.send(reactionPhrase)
	await message.add_reaction("\N{Llama}")
	
	return channel

@bot.command()
async def restartForm(ctx, mention):
	if ctx.message.channel == allFormsChannel:
		discordUserID = int(mention[mention.find("@") + 2: len(mention) - 1])
		user = lampartyGuild.get_member(int(discordUserID))
		channel = discord.utils.find(lambda channel: user in channel.members, formsCategory.channels)
		await channel.delete()
		await createMemberChannel(user)

@bot.command()
async def add(ctx, mention):
	async def insertIntoDB(discordUserID, minecraftUUID, collection):
			data = {
				"discordID": discordUserID,
				"mojangUUID": minecraftUUID
			}
			registredUsers = registredUsersCollection.find()
			return collection.insert_one(data)	
	
	async def getMojangUUID(minecraftNick):
		return requests.get(f'https://api.mojang.com/users/profiles/minecraft/{minecraftNick}').json()['id']


	if ctx.message.channel == allFormsChannel:
		await allFormsChannel.send("Напишите ник игрока")
		nickMessage = await bot.wait_for("message")
		nick = nickMessage.content
		discordUserID = int(mention[mention.find("@") + 2: len(mention) - 1])
		user = lampartyGuild.get_member(int(discordUserID))
		channel = discord.utils.find(lambda channel: user in channel.members, formsCategory.channels)
		await channel.delete()
		await user.add_roles(playerRole)
		await user.edit(nick = nick)
		await user.send(addedOnServerPhrase)
		await insertIntoDB(user.id, await getMojangUUID(nick), registredUsersCollection)
		await lamparty.executeCommand(f"whitelist add {nick}")
		pass

@bot.command()
async def updateNicks(ctx):
	if ctx.message.channel == allFormsChannel:
		registredUsers = registredUsersCollection.find()
		for user in registredUsers:
			member = lampartyGuild.get_member(user["discordID"])
			if(member):
				print(member)#not adminRole in member.roles)
				if (not adminRole in member.roles):
					mojangUUID = user["mojangUUID"]
					nicks = requests.get(f"https://api.mojang.com/user/profiles/{mojangUUID}/names").json()
					await member.edit(nick = nicks[len(nicks) - 1]["name"])
			

bot.run("ODY4NjIxMDg2NjEzNDU5MDEz.YPyUbQ._KAVTEqDSJ7l0Mtm1delxSZI4bI")