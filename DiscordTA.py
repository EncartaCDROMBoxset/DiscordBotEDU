#Tutorial https://www.youtube.com/watch?v=u6tBvQSXJ7I
#Add to server link: https://discordapp.com/oauth2/authorize?client_id=your_client_id_goes_here&scope=bot&permissions=0
#Python wrapper https://pypi.python.org/pypi/discord.py/
#Note that in Python 3.4 you use `@asyncio.coroutine` instead of `async def` and `yield from` instead of `await`.
#Python 3.5+ use `async def`
#Another tutorial that MIGHT be useful https://www.youtube.com/watch?v=aFI1SItR8tg
#Awesome writeup on Decorators https://realpython.com/blog/python/primer-on-python-decorators/
#For helper functions, you have to await coroutine calls to make sure a result is returned. See https://docs.python.org/3/library/asyncio-task.html
#Using global variable in Python is slightly weird: https://stackoverflow.com/questions/423379/using-global-variables-in-a-function-other-than-the-one-that-created-them
#Shoutout to https://www.idiotinside.com/2015/03/01/python-lists-as-fifo-lifo-queues-using-deque-collections/

#TODO:
#-Make getChannels organize by server. Probs use a dictionary here.
#-Make the bot post only to a specific channel.
#--If the context is outside of the specified channel, tag the author.
#-MAYBE refactor all these "gets" to helpers, make the current ones "say" functions
#-Make getRoles build a list and return it in sorted alphabetical
#Make creating roles only allowable by roles that can manage roles
#Creating roles needs exception handling
#Refactor roleNames helper to have a general default parameter
#Might be a good idea to have role stuff as subcommands. See the discord.py docs
#Maybe replace string concatenations with {}.format's or f-strings
#Implement banned words, check those words in emoji strings too
#Implement strikes, spam counts towards strikes
#Make on_member_join and assignRoleOnJoin server agnostic or make commands for default role on per server basis
#Set up a default talk channel in on_ready, clean up the check in assingRoleOnJoin
#Figure out why the hell the error checking in massDM doesn't work. It's most likely because doing async checks within if statements and blocking calls but IDK HOMIE
#Change the logic in massDM to do the check within the main loop. Else, change the delimiter

#Dictionary
# ServerName : ([Roles], [Channels])

import discord
import asyncio
from discord.ext import commands
from collections import deque #For Q&A queue


botToken = "NTMxMjExNzE5NjgzMzQyMzM2.Dyphjw.vvIAgvVwccLAABuAlFfDSyNsHjs"
Client = discord.Client() #Do I need this?
bot_prefix="!"
bot = commands.Bot(command_prefix = bot_prefix)
#Server = "server goes here"
talkChannel = "Channel goes here"

@bot.event
async def on_ready():
	print("Bot online.")
	print("Name: {}".format(bot.user.name))
	print("ID: {}".format(bot.user.id))
	print(list(bot.guilds))

###### EDU: Q&A Commands ######
qa = deque([]) # Manages the questions being asked, FIFO
qRoleTracker = {} # Used for managing the "question" role

@bot.command()
async def q(ctx):
	global qa
	global qRoleTracker
	author = ctx.message.author
	question = ctx.message.content.split("!q")
	print("question:\n{}".format(question))
	qa.append((author, question[1].lstrip()))
	if (author in qRoleTracker):
		qRoleTracker[author] += 1
	else:
		qRoleTracker[author] = 1
	await ctx.send("Added your question to the queue.")

@bot.command()
async def a(ctx):
	#TODO: Check role of author
	global qa
	global qRoleTracker
	nextQuestion = qa.popleft()
	author = nextQuestion[0]
	qRoleTracker[author] -= 1
	if (qRoleTracker[author] == 0):
		del qRoleTracker[author]
	await ctx.send(str(author) + " asks:\n" + nextQuestion[1])

@bot.command()
async def sq(ctx):
	global qa
	global qRoleTracker
	if len(qa) == 0:
		await ctx.send("The Q&A queue is empty.")
		return
	responseString = ""
	for question in qa:
		responseString += str(question[0]) + ": " + question[1] + "\n"
	print("qRoleTracker:")
	for key, value in qRoleTracker.items():
		print(key, value)
	await ctx.send("The Q&A queue is as follows:\n" + responseString)


###### Events ######

# @bot.async_event
# @asyncio.coroutine
# async def on_member_join(newMember):
# 	await assignRoleOnJoin(newMember)

#Helper for on_member_join
# async def assignRoleOnJoin(user):
# 	currentRoles = user.server.roles
# 	for role in currentRoles:
# 		if role.name == "Guests": #Generalize this here and on the send_message
# 			await bot.add_roles(user, role)
# 			if talkChannel != "Channel goes here":
# 				await bot.send_message(bot.get_channel(talkChannel.id), "{} has joined, added to {}".format(user.name, "Guests"))
# 			break

###### Channels ######

@bot.command()
async def getChannelsRaw(ctx):
	await ctx.send("I can see the following channels: ")
	channelList = list(bot.get_all_channels())
	for c in channelList:
		await ctx.send(c)

@bot.command()
async def getChannels(ctx):
	await ctx.send("I can see the following channels: ")
	channelList = list(bot.get_all_channels())
	channelString = ""
	for c in channelList:
		channelString += str(c.name) + " in server, " + str(c.guild.name) + "\n"
	await ctx.send(channelString)

@bot.command()
async def getChannelIDs(ctx):
	await ctx.send("I can see the following channels: ")
	channelList = list(bot.get_all_channels())
	channelString = ""
	for c in channelList:
		channelString += str(c.name) + ", " + str(c.id) + "\n"
	await ctx.send(channelString)

@bot.command()
async def setTalkChannel(ctx):
	global talkChannel 
	talkChannel = ctx.message.channel
	await ctx.send("I will post messages here.")

###### Roles ######

@bot.command()
async def createRole(ctx):
	currentRoles = await getRoles(ctx.message.server)
	rolesToAdd = str(ctx.message.content).split(" ")
	rolesToAdd.remove("!createRole")
	await ctx.send("You want me to add the following roles: \n" + " | ".join(rolesToAdd))
	responseString = ""
	for role in rolesToAdd:
		lowRole = role.lower()
		if lowRole in currentRoles:
			if currentRoles[lowRole].name == role:
				responseString += role + " already exists.\n"
			else:
				responseString += "There's only a case difference between your request: {} \nand the existing role: {}\n".format(role, currentRoles[lowRole].name)
		else:
			responseString += role + " doesn't exist yet, so I can create that role.\n"
	responseString = responseString[:-2]
	await ctx.send(responseString)

@bot.command()
async def getRolesAllServers(ctx):
	await ctx.send("I can see the following roles: ")
	responseString = ""
	serverList = list(bot.guilds)
	for s in serverList:
		responseString += str(s.name) + "\n"
		for role in s.roles:
			if role.is_everyone is not True:
				responseString += "- " + str(role.name) + "\n"
		responseString += "\n"
	await ctx.send(responseString)

@bot.command()
async def getRolesThisServer(ctx):
	await ctx.send("I can see the following roles: ")
	responseString = ""
	for role in ctx.message.server.roles:
		if role.is_everyone is not True:
			responseString += "- " + str(role.name) + "\n"
	await ctx.send(responseString)

###### Servers ######

@bot.command()
async def getServersRaw(ctx):
	await ctx.send("I can see the following servers: ")
	await ctx.send(list(bot.guilds))

@bot.command()
async def getServers(ctx):
	await ctx.send("I can see the following servers: ")
	serverList = list(bot.guilds)
	serverString = ""
	for s in serverList:
		serverString += "- " + str(s.name) + "\n"
	await ctx.send(serverString)

###### Messages ######

#format is !massDM [names] | [message]
@bot.command()
async def massDM(ctx):
	firstHalf, text = str(ctx.message.content).split("|")
	firstHalf = firstHalf[8:-1]
	text = text[1:]
	names = firstHalf.split(" ")
	# print("Names:")
	# print(names)
	#Fixes usernames with spaces
	#This is gross. See if you can do it in the below loop
	for i, name in enumerate(names):
		while "#" not in names[i]:
			names[i] += " " + names[i+1]
			del names[i+1]

	for name in names:
		print(name)
		user = ctx.message.server.get_member_named(name)
		# if user == None:
		# 	print (name, "does not exist on this server.")
		# 	await ctx.send("user '{}' does not exist.".format(name))
		# else:
		# 	print(user, "exists on this server.")
		# 	#await bot.send_message(ctx.message.channel, "User {} was messaged.".format(name))
		# 	await bot.send_message(user, text)
		await ctx.send(ctx.message.channel, "User {} was messaged.".format(name))
		await bot.send_message(user, text)
	#await ctx.send(text)
	

###### Helpers ######

#Returns role names of the server from which context originated as list of Strings
async def getRoleNameStrings(ctx):
	roles = ctx.message.server.roles
	roleNames = []
	for role in roles:
		roleNames.append(role.name)
	return roleNames

#Returns a Dictionary with key: lowercase role name | value: Role object
#Key is lowercase to make the comparison operation for createRole easier
async def getRoles(server):
	roles = server.roles
	roleDict = {}
	for role in roles:
		roleDict[role.name.lower()] = role
	return roleDict

###### Dev ######

@bot.command()
async def test(ctx):
	await ctx.send("Hello World!")

@bot.command()
async def checkContext(ctx):
	await ctx.send(str(ctx.message.author) + " messaged me from the channel, " 
				+ str(ctx.message.channel) + ", in the server, " 
				+ str(ctx.message.server))
	await ctx.send("They said: \n" + str(ctx.message.content))

@bot.command()
async def checkStatus(ctx):
	# await ctx.send("is_logged_in: " + str(bot.is_logged_in)) # Deprecated
	await ctx.send("is_closed: " + str(bot.is_closed))

@bot.command()
async def tryLogin():
	await bot.login(botToken)

bot.run(botToken)
