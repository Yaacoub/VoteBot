from datetime import *
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from keep_alive import keep_alive
from pytz import timezone

import asyncio
import discord
import os



# Variables

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents = intents)
channel_official_id = 000000000000000000 # put your announcement channel ID here
choices = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
guild_id_petropolis = 000000000000000000 # put your server ID here
slash = SlashCommand(client, sync_commands = True)



# Variables - Messages

message_invalid_duration = "*Oops!* The chosen duration is not valid."
message_no_permission = "*Oops!* You don't have the necessary rights to send an official vote."
message_official_sent = "The official vote was sent!"
message_vote_duration = "⏰ This vote ends at {} EET."



# Variables - Options

option_choice = create_option(name = "choice", description = "The number of choices, between 2 and 10 included.", option_type = 4, required = False, choices = [2, 3, 4, 5, 6, 7, 8, 9, 10])
option_duration = create_option(name = "duration", description = "The number of hours before the vote expires.", option_type = 4, required = False)
option_question = create_option(name = "question", description = "The poll question.", option_type = 3, required = True)
option_status = create_option(name = "status", description = "The vote's importance.", option_type = 3, required = False, choices = ["normal", "official"])



# Defined Method - On Raw Reaction Add

@client.event
async def on_raw_reaction_add(payload):

	if payload.user_id == client.user.id: return
	channel = client.get_channel(payload.channel_id)
	message = await channel.fetch_message(payload.message_id)

	if message.author == client.user and message.content.startswith("📢"):

		for r in message.reactions:
			if await r.users().find(lambda x: x == client.user) == None:
				await message.remove_reaction(r.emoji, payload.member)
				return

		for r in message.reactions:
			from_user = await r.users().find(lambda x: x.id == payload.user_id)
			r_emoji_name = r.emoji.name if r.emoji is discord.Emoji else r.emoji
			if from_user and r_emoji_name != payload.emoji.name:
				await message.remove_reaction(r.emoji, payload.member)
				return



# Defined Method - On Ready

@client.event
async def on_ready():
	print("We have logged in as {0.user}".format(client))



# Definded Method - Slash Command

@slash.slash(
	name = "vote",
	description = "Create and send a new poll.",
	guild_ids = [guild_id_petropolis],
	options = [option_question, option_choice, option_duration, option_status],
	connector = {"question": "question", "choice": "choice", "duration": "duration", "status": "status"}
)
async def vote(context, question, choice = None, duration = None, status = None):

	channel_official = client.get_channel(channel_official_id)
	is_official = False
	is_valid_duration = (duration and duration > 0) or (duration == None)
	sent = None



	# Check permission

	if status == "official" and context.author == context.guild.owner:
		if channel_official.permissions_for(context.author).send_messages:
			is_official = True
	elif status == "official":
		await context.send(message_no_permission, hidden = True)
		return



	# Send message

	if is_official and is_valid_duration:
		sent = await channel_official.send("📢 **" + question + "**")
		await context.send(message_official_sent, hidden = True)
	elif is_valid_duration:
		sent = await context.send("📢 **" + question + "**")
	else:
		await context.send(message_invalid_duration, hidden = True)
		return



	# Add reactions

	if choice:
		for i in range(0, choice):
			await sent.add_reaction(choices[i])
	else:
		await sent.add_reaction("👍")
		await sent.add_reaction("👎")



	# Delay results

	if duration:
		tz = timezone("Asia/Beirut")
		now = datetime.now().replace(second = 0, microsecond = 0)
		delay = now + timedelta(hours = duration) - datetime.now()
		date_format = "__%d/%m/%Y à %H:%M__"
		date_string = (datetime.now(tz) + delay).strftime(date_format)
		appending = message_vote_duration.format(date_string)
		await sent.edit(content = sent.content + "\n" + appending)
		await asyncio.sleep(delay.total_seconds())
		results = await results_string(client, sent.id)
		await sent.delete()
		if is_official:
			await channel_official.send("🗳 **" + question + "**" + results)
		else:
			await context.channel.send("🗳 **" + question + "**" + results)



# Defined Method

async def results_string(client: discord.Client, message_id: int):
	await asyncio.sleep(5)
	message = next(x for x in client.cached_messages if x.id == message_id)
	string = ""
	for reaction in message.reactions:
		emoji = reaction.emoji
		if reaction.emoji is discord.Emoji: emoji = emoji.name
		vote_count = len(await reaction.users().flatten()) - 1
		string += emoji + " : " + str(vote_count) + "\n\n"
	return "\n\nRésultats\n==========\n\n" + string



# Called Methods

keep_alive()
client.run(os.environ["TOKEN"])
