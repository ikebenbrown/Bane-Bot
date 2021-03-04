import asyncio
import datetime
import time
from operator import itemgetter

import discord

from Voting import VotingListener
from EmojiListener import EmojiListener as Emoji


def getTimeStamp(stamp):
    return "[" + stamp + "] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


def get_user_name(user):
    if user.nick is None:
        return user.name
    return user.nick


class EmojiHandler:

    def __init__(self, guild, announcements_channel, client):
        self.client = client
        self.emojiPrefix = "!emoji"
        self.guild = guild
        self.announcements_channel = announcements_channel
        self.emojiVoters = []
        self.emoji = None
        self.current_user = None

        # Define and create file if it isn't present
        self.guild_file = "data/" + str(self.guild.id) + "_emojivotes.max"
        f = open(self.guild_file, "a")
        f.close()

    async def handleEmojiMessage(self, message):
        self.check_usage_status()

        if str(message.content).startswith("!timecheck"):
            emoji_response = await self.canAddEmoji(message)
            if emoji_response == "True":
                await message.reply("**[Emoji Voting Cooldown]**\n" + message.author.mention +
                                    "'s Cooldown: *None*\n" + "Server Cooldown: *None*")
            else:
                await message.reply("**[Emoji Voting Cooldown]**\n" + emoji_response)

        if self.in_use() and str(message.author.name) == str(self.current_user.name):
            if self.emoji.status == "done":
                self.emoji = None
                return

            elif self.emoji.status == "prompt":
                if await self.emoji.handle_replacement(message.content) is None:
                    await self.emoji.final_image_response(message.content)
                    self.emojiVoters.append(VotingListener(self.emoji, 15, self.client, True))
                    return
                return

            elif self.emoji.status == "confirm":
                await self.emoji.final_image_response(message.content)
                self.emojiVoters.append(VotingListener(self.emoji, 15, self.client, True))
                return

        # At this point we are free to engage with a new emoji addition
        elif not message.author.bot and str(message.content).startswith(self.emojiPrefix):
            if not self.in_use():
                emoji_response = await self.canAddEmoji(message)
                if emoji_response == "True":
                    self.emoji = Emoji(message, self.announcements_channel, self.guild, None)
                    await self.emoji.emoji_cycle()
                    self.current_user = message.author
                else:
                    await message.channel.send("**[Emoji Voting Cooldown]**\n" + emoji_response)
            else:
                await message.channel.send(get_user_name(self.current_user) + " is currently adding an emoji.  "
                                                                              "Please wait to use the bot.")

    async def handleEmojiVoters(self, reaction):

        for voter in self.emojiVoters:

            try:
                if voter.get_message_id() == reaction.message_id:
                    val, image, name, replacement = await voter.add_vote(reaction)
                    if val is True:
                        if replacement is not None:
                            print(getTimeStamp("EMOJI"), "Replacing ", replacement.name, "with", name)
                            for emoji in self.guild.emojis:
                                if emoji.name == replacement.name:
                                    print(getTimeStamp("EMOJI"), "Deleting " + emoji.name)
                                    await emoji.delete()
                        else:
                            print("[ERROR] ", getTimeStamp("EMOJI"), "NO REPLACEMENT FOUND!")

                        newEmoji = None
                        await self.guild.create_custom_emoji(name=name, image=image)
                        for emoji in self.guild.emojis:
                            if emoji.name == name:
                                newEmoji = emoji

                        await asyncio.sleep(.25)
                        await self.announcements_channel.send("**[EMOJI ALERT]**\n" + str(
                            newEmoji) + " has been added under the name **:" + newEmoji.name + ":**")

                        voter.destroy()
                        self.emojiVoters.remove(voter)
            except AttributeError:
                self.emojiVoters.remove(voter)

    def in_use(self):
        if self.emoji is None:
            return False
        return self.emoji.in_use

    def check_usage_status(self):
        if self.emoji is not None:
            self.current_user = self.emoji.current_user
        else:
            self.current_user = None
            self.emoji = None

    def addVoters(self, voters):
        for voter in voters:
            self.emojiVoters.append(voter)

    async def canAddEmoji(self, message):
        # This is the most malformed bullshit I've ever written.  Good luck future Max.

        user_next_allowed = await self.get_user_allowed_submission_time(message)

        # Check for server cooldown
        if self.server_cooldown(message) is not None:

            # User and Server cooldown
            if user_next_allowed >= datetime.datetime.utcnow():
                print(getTimeStamp("EMOJI") + "USER AND SERVER COOLDOWN")
                timeDelta = user_next_allowed - datetime.datetime.utcnow()
                return message.author.mention + "'s Cooldown: *" + self.get_formatted_time(timeDelta) + "*\n" \
                                    "Server Cooldown: *" + self.get_formatted_time(self.server_cooldown(message)) + "*"

            # Server cooldown
            else:
                print(getTimeStamp("EMOJI") + "SERVER COOLDOWN")
                timeDelta = self.server_cooldown(message)
                return "Server Cooldown: *" + self.get_formatted_time(timeDelta) + "*"

        # User cooldown
        if user_next_allowed >= datetime.datetime.utcnow():
            print(getTimeStamp("EMOJI") + "USER COOLDOWN")
            timeDelta = user_next_allowed - datetime.datetime.utcnow()
            return message.author.mention + "'s Cooldown: *" + self.get_formatted_time(timeDelta) + "*"

        return "True"

    def server_cooldown(self, message):
        voter_times = []
        # Put all voter_times into an array
        for voter in self.emojiVoters:
            # delta is the amount of time since the last voter passed
            delta: datetime.timedelta = (message.created_at - voter.emoji.time)
            if delta.total_seconds() < 24 * 60 * 60:
                voter_times.append(delta)
        if len(voter_times) == 0:
            return None
        lowest_time = voter_times[0]
        for voter_time in voter_times:
            if voter_time.seconds < lowest_time.seconds:
                lowest_time = voter_time
        return datetime.timedelta(days=1) - lowest_time

    def get_formatted_time(self, timeDelta):
        hms = str(timeDelta).split(".")[0]
        hours = hms.split(":")[0]
        minutes = hms.split(":")[1]
        seconds = hms.split(":")[2]
        if hours != "00":
            return hours + " hours, " + minutes + " minutes, and " + seconds + " seconds"
        else:
            if minutes != "00":
                return minutes + " minutes, and " + seconds + " seconds"
            else:
                return seconds + " seconds"

    async def get_user_allowed_submission_time(self, message):
        user_messages = []
        file = str(open(self.guild_file, "r").read()).split("\n")
        for entry in file:
            if entry != "":
                try:
                    # 0: message ID, 1: channel ID of message
                    entry = entry.split(",")
                    channel: discord.TextChannel = await self.client.fetch_channel(int(entry[1]))
                    original_message = await channel.fetch_message(int(entry[0]))
                    if original_message.author.id == int(message.author.id):
                        user_messages.append([original_message, original_message.created_at.timestamp()])

                except IndexError:
                    print("Malformed File")

        if len(user_messages) != 0:
            user_messages = sorted(user_messages, key=itemgetter(1), reverse=True)
            original_time = user_messages[0][0].created_at
            return original_time + datetime.timedelta(days=20)

        print("Found No Value for", message.author.id)
        # No emoji found, return the datetime from 1 minute ago
        return datetime.datetime.now() - datetime.timedelta(minutes=1)