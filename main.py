import time
import discord
from EmojiHandler import EmojiHandler
from PinHandler import PinHandler
from HistoryManager import HistoryManager
import Voting
import LanguageHandler

# DONE separate Emoji stuff into its own class
# DONE clean up timestamps across codebase
# DONE wipe mentions from pins
# DONE record pinned messages in a file and read them on boot
# DONE record emoji votes in a file and read them on boot
# DONE implement server-wide cooldown of emoji submission
# DONE implement system to collect emoji usage from the last month
# DONE implement 20 day block after submitting an emoji
# TODO role manager
# TODO cancel emoji votes after 4 days
# ---------------- History Manager ---------------------
# TODO give HistoryManager its own thread to avoid blocking responses while parsing server data
# TODO automatically collect and report emoji usage on the 1st day of every month
# TODO automatically update "chopping block" based on emoji usage data


f = open("data/key.txt", "r")
key = f.read()

g = open("data/guild.max", "r")
active_guild = g.read()

# Dangerous Men
# active_guild = 375753471812435968

# Test Server
# noinspection PyRedeclaration
active_guild = 782870393517768704


def getTimeStamp(stamp):
    return "[" + stamp + "] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


class Client(discord.Client):

    def __init__(self):
        super().__init__()
        self.announcements_channel = None
        self.guild = None
        self.pinHandler = None
        self.emojiHandler = None

    async def on_ready(self):

        await client.change_presence(activity=discord.Activity(name='Eat The Rich', type=discord.ActivityType.playing))

        for n in self.guilds:
            # if n.id ==
            if n.id == active_guild:
                self.guild = n
                print(getTimeStamp("SERVER"), "Found GUILD: " + self.guild.name)

        for a in self.guild.text_channels:
            if a.name == "emoji-voting":
                self.announcements_channel = a
                print(getTimeStamp("SERVER"), "Found Announcements Channel: ", str(self.announcements_channel.id))
                self.emojiHandler = EmojiHandler(self.guild, self.announcements_channel, self)

            if a.name == "pins":
                print(getTimeStamp("SERVER"), "Found Pins Channel")
                self.pinHandler = PinHandler(a, self.guild)

        self.emojiHandler.addVoters(await Voting.create_archived_votes(self))

        # history = HistoryManager(self.guild)
        # await history.analyze_history()

    async def on_message(self, message: discord.Message):
        if message.guild.id == active_guild:
            await LanguageHandler.determine_language(message)
            if self.emojiHandler is not None:
                await self.emojiHandler.handleEmojiMessage(message)

    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
        if reaction.guild_id == active_guild:
            await self.pinHandler.handlePinReaction(reaction, self)
            if self.emojiHandler is not None:
                await self.emojiHandler.handleEmojiVoters(reaction)

    async def send_message(self, channel_name, message):
        channels = await self.guild.fetch_channels()
        for channel in channels:
            if channel.name == channel_name:
                await channel.send(message)

    async def join_vc(self, channel_name):
        channels = await self.guild.fetch_channels()
        for channel in channels:
            if channel.name == channel_name:
                await channel.connect()


client = Client()
client.run(key)