import asyncio
import datetime
import time

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

    async def handleEmojiMessage(self, message):
        self.check_usage_status()
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
                if self.canAddEmoji(message) == "True":
                    self.emoji = Emoji(message, self.announcements_channel, self.guild, None)
                    await self.emoji.emoji_cycle()
                    self.current_user = message.author
                else:
                    await message.channel.send("You must wait " + self.canAddEmoji(message) + " to add an emoji")
                    print(self.canAddEmoji(message))
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

    def canAddEmoji(self, message):
        for voter in self.emojiVoters:
            delta = (message.created_at - voter.emoji.time).seconds
            if delta < 24 * 60 * 60:
                timeDelta = voter.emoji.time + datetime.timedelta(hours=24) - datetime.datetime.utcnow()
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

        return "True"