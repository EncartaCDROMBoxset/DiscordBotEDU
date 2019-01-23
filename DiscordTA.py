#Tutorial https://www.youtube.com/watch?v=u6tBvQSXJ7I
#Add to server link: https://discordapp.com/oauth2/authorize?client_id=your_client_id_goes_here&scope=bot&permissions=0
#Python wrapper https://pypi.python.org/pypi/discord.py/
#Note that in Python 3.4 you use `@asyncio.coroutine` instead of `async def` and `yield from` instead of `await`.
#Python 3.5+ use `async def`
#Another tutorial that MIGHT be useful https://www.youtube.com/watch?v=aFI1SItR8tg
#Awesome writeup on Decorators https://realpython.com/blog/python/primer-on-python-decorators/
#For helper functions, you have to await coroutine calls to make sure a result is returned. See https://docs.python.org/3/library/asyncio-task.html
#Using global variable in Python is slightly weird: https://stackoverflow.com/questions/423379/using-global-variables-in-a-function-other-than-the-one-that-created-them

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
from discord.ext import commands
from collections import deque #For Q&A queue


botToken = "LOL DANGIT"
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
    print(list(bot.servers))

###### EDU: Q&A ######
qa = deque([])

@bot.command(pass_context = True)
async def q(ctx):
	global qa
	question = ctx.message.content.split("!q")
	print("question:")
	print(question)
	qa.append((ctx.message.author, question[1]))
	await bot.say("Added your question to the queue")

@bot.command(pass_context = True)
async def a(ctx):
	#TODO: Check role of author
	global qa
	nextQuestion = qa.popleft()
	await bot.say(str(nextQuestion[0]) + " asks:\n" + nextQuestion[1])

@bot.command(pass_context = True)
async def sq(ctx):
	#TODO: if the queue is empty, say a short response
	responseString = ""
	global qa
	for question in qa:
		responseString += str(question[0]) + ": " + question[1] + "\n"
	await bot.say("The QA queue is as follows:\n" + responseString)


###### Events ######

@bot.async_event
async def on_member_join(newMember):
	await assignRoleOnJoin(newMember)

#Helper for on_member_join
async def assignRoleOnJoin(user):
	currentRoles = user.server.roles
	for role in currentRoles:
		if role.name == "Guests": #Generalize this here and on the send_message
			await bot.add_roles(user, role)
			if talkChannel != "Channel goes here":
				await bot.send_message(bot.get_channel(talkChannel.id), "{} has joined, added to {}".format(user.name, "Guests"))
			break

###### Channels ######

@bot.command()
async def getChannelsRaw():
    await bot.say("I can see the following channels: ")
    await bot.say(list(bot.get_all_channels()))

@bot.command()
async def getChannels():
    await bot.say("I can see the following channels: ")
    channelList = list(bot.get_all_channels())
    channelString = ""
    for c in channelList:
    	channelString += str(c.name) + " in server, " + str(c.server.name) + "\n"
    await bot.say(channelString)

@bot.command(pass_context = True)
async def setTalkChannel(ctx):
	global talkChannel 
	talkChannel = ctx.message.channel
	await bot.send_message(bot.get_channel(talkChannel.id), "I will post messages here.")

###### Roles ######

@bot.command(pass_context = True)
async def createRole(ctx):
	currentRoles = await getRoles(ctx.message.server)
	rolesToAdd = str(ctx.message.content).split(" ")
	rolesToAdd.remove("!createRole")
	await bot.say("You want me to add the following roles: \n" + " | ".join(rolesToAdd))
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
	await bot.say(responseString)

@bot.command()
async def getRolesAllServers():
	await bot.say("I can see the following roles: ")
	responseString = ""
	serverList = list(bot.servers)
	for s in serverList:
		responseString += str(s.name) + "\n"
		for role in s.roles:
			if role.is_everyone is not True:
				responseString += "- " + str(role.name) + "\n"
		responseString += "\n"
	await bot.say(responseString)

@bot.command(pass_context = True)
async def getRolesThisServer(ctx):
	await bot.say("I can see the following roles: ")
	responseString = ""
	for role in ctx.message.server.roles:
		if role.is_everyone is not True:
			responseString += "- " + str(role.name) + "\n"
	await bot.say(responseString)

###### Servers ######

@bot.command()
async def getServersRaw():
    await bot.say("I can see the following servers: ")
    await bot.say(list(bot.servers))

@bot.command()
async def getServers():
    await bot.say("I can see the following servers: ")
    serverList = list(bot.servers)
    serverString = ""
    for s in serverList:
        serverString += "- " + str(s.name) + "\n"
    await bot.say(serverString)

###### Messages ######

#format is !massDM [names] | [message]
@bot.command(pass_context = True)
async def massDM(ctx):
	firstHalf, text = str(ctx.message.content).split("|")
	firstHalf = firstHalf[8:-1]
	text = text[1:]
	names = firstHalf.split(" ")
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
		# 	await bot.say("user '{}' does not exist.".format(name))
		# else:
		# 	print(user, "exists on this server.")
		# 	#await bot.send_message(ctx.message.channel, "User {} was messaged.".format(name))
		# 	await bot.send_message(user, text)
		await bot.send_message(ctx.message.channel, "User {} was messaged.".format(name))
		await bot.send_message(user, text)
	#await bot.say(text)
	

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
async def test():
    await bot.say("Hello World!")

@bot.command(pass_context = True)
async def checkContext(ctx):
    await bot.say(str(ctx.message.author) + " messaged me from the channel, " 
                + str(ctx.message.channel) + ", in the server, " 
                + str(ctx.message.server))
    await bot.say("They said: \n" + str(ctx.message.content))

@bot.command()
async def checkStatus():
    await bot.say("is_logged_in: " + str(bot.is_logged_in))
    await bot.say("is_closed: " + str(bot.is_closed))

@bot.command()
async def tryLogin():
    await bot.login(botToken)

bot.run(botToken)
