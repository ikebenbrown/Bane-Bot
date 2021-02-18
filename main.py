import asyncio
import datetime
import time

import discord
from EmojiListener import EmojiListener as Emoji
from Voting import VotingListener
from PinHandler import PinHandler
import LanguageHandler

pin_threshold = 15
debugMode = False

f = open("key.txt", "r")
key = f.read()


def getTimeStamp(stamp):
    return "["+stamp+"] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


def get_user_name(user):
    if user.nick is None:
        return user.name
    return user.nick


class Client(discord.Client):
    emojiPrefix = "!"
    current_user = None
    emoji = None

    def __init__(self, *, loop=None, **options):
        super().__init__()
        self.announcements_channel = None
        self.emojiVoters = []
        self.guild = None
        self.pinHandler = None

    async def on_ready(self):

        await client.change_presence(activity=discord.Activity(name='Eat The Rich', type=discord.ActivityType.playing,
                                                               timestamps={'start': time.time()-100, 'end': time.time()},
                                                               state="Pissing on Margret Thatcher's Grave", application_id="0"))
        for n in self.guilds:
            # if n.id == 782870393517768704:
            if n.id == 375753471812435968:
                self.guild = n
                break
        for a in self.guild.text_channels:
            if a.name == "server-announcements":
                self.announcements_channel = a
                print(getTimeStamp("SERVER"), "Found Announcements Channel")
            if a.name == "pins":
                print(getTimeStamp("SERVER"), "Found Pins Channel")
                self.pinHandler = PinHandler(a, self.guild)

    async def on_message(self, message):
        # Update status of Emoji object
        self.check_usage_status()

        if self.in_use() and str(message.author.name) == str(self.current_user.name):
            if self.emoji.status == "done":
                self.emoji = None
                return
            elif self.emoji.status == "prompt":
                if await self.emoji.handle_replacement(message.content) is None:
                    await self.emoji.final_image_response(message.content)
                    self.emojiVoters.append(VotingListener(self.emoji))

            elif self.emoji.status == "confirm":
                await self.emoji.final_image_response(message.content)
                self.emojiVoters.append(VotingListener(self.emoji))

        # At this point we are free to engage with a new emoji addition
        elif message.content.startswith(self.emojiPrefix) and not message.author.bot:
            if not self.in_use():
                self.emoji = Emoji(message, self.announcements_channel, self.guild)
                await self.emoji.emoji_cycle()
                self.current_user = message.author
            else:
                await message.channel.send(get_user_name(self.current_user) + " is currently adding an emoji.  "
                                                                              "Please wait to use the bot.")
        elif not message.author.bot:
            await LanguageHandler.determine_language(message)

    async def on_raw_reaction_add(self, reaction):
        await self.handleEmojiVoters(reaction)
        await self.handlePinVoters(reaction)

    async def on_raw_reaction_remove(self, reaction):
        for voter in self.emojiVoters:
            if voter.get_message_id() == reaction.message_id:
                voter.remove_vote(reaction)

    async def handlePinVoters(self, reaction):
        channel = client.get_channel(reaction.channel_id)
        message = await channel.fetch_message(reaction.message_id)
        for reaction in message.reactions:
            if reaction.emoji == "📌":
                if reaction.count == pin_threshold:
                    await self.pinHandler.pin(message)

    async def handleEmojiVoters(self, reaction):
        for voter in self.emojiVoters:
            if voter.get_message_id() == reaction.message_id:
                val, image, name, replacement = voter.add_vote(reaction)
                if val is True:
                    if replacement is not None:
                        print(getTimeStamp("EMOJI"), "Replacing ", replacement.name, "with", name)
                        for emoji in self.guild.emojis:
                            if emoji.name == replacement.name:
                                print(getTimeStamp("EMOJI"), "Deleting " + emoji.name)
                                await emoji.delete()
                                time.sleep(1)
                    else:
                        print("[ERROR] ",getTimeStamp("EMOJI"), "NO REPLACEMENT FOUND!")
                    newEmoji = None
                    await self.guild.create_custom_emoji(name=name, image=image)
                    for emoji in self.guild.emojis:
                        if emoji.name == name:
                            newEmoji = emoji
                    await self.announcements_channel.send("**[EMOJI ALERT]**\n" + str(
                        newEmoji) + " has been added under the name **:" + newEmoji.name + ":**")
                    voter.destroy()
                    self.emojiVoters.remove(voter)

    def check_usage_status(self):
        if self.emoji is not None:
            self.current_user = self.emoji.current_user
        else:
            self.current_user = None
            self.emoji = None

    def in_use(self):
        if self.emoji is None:
            return False
        return self.emoji.in_use


client = Client()
client.run(key)
