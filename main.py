import time

import discord
from EmojiHandler import EmojiHandler
from PinHandler import PinHandler
from RoleHandler import RoleHandler
from HistoryManager import HistoryManager
import Voting
import LanguageHandler

# TODO role manager
# TODO cancel emoji votes after 4 days
# ---------------- History Manager ---------------------
# TODO give HistoryManager its own thread to avoid blocking responses while parsing server data
# TODO automatically collect and report emoji usage on the 1st day of every month
# TODO automatically update "chopping block" based on emoji usage data


f = open("data/key.txt", "r")
key = f.read()

# g = open("data/guild.max", "r")
# active_guild = int(g.read())

# Dangerous Men
active_guild = 375753471812435968

# Test Server
# noinspection PyRedeclaration
# active_guild = 782870393517768704


def getTimeStamp(stamp):
    return "[" + stamp + "] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


class Client(discord.Client):

    guild: discord.Guild

    def __init__(self):
        super().__init__()
        self.announcements_channel = None
        self.guild = None
        self.pinHandler = None
        self.roleHandler = None
        self.emojiHandler = None
        self.admin_channel = None
        self.roles_channel = None
        self.ant_zone = None
        self.fuck = None
        self.misc = None
        self.database = None

    async def on_ready(self):

        # self.database = MySQLHandler()

        await self.change_presence(activity=discord.Activity(name='Eat The Rich', type=discord.ActivityType.playing))
        for n in self.guilds:
            # if n.id ==
            if n.id == active_guild:
                self.guild = n
                print(getTimeStamp("SERVER"), "Found GUILD: " + self.guild.name)

        for a in self.guild.text_channels:

            if a.name == "server-announcements":
                self.announcements_channel = a
                print(getTimeStamp("SERVER"), "Found Announcements Channel: ", str(self.announcements_channel.id))
                self.emojiHandler = EmojiHandler(self.guild, self.announcements_channel, self)

            if a.name == "shit-takes":
                self.misc = a
                print(getTimeStamp("SERVER"), "Found Misc Channel: ", str(self.misc.id))

            if a.name == "pins":
                print(getTimeStamp("SERVER"), "Found Pins Channel")
                self.pinHandler = PinHandler(a, self.guild)

            if a.name == "admin-chat":
                print(getTimeStamp("SERVER"), "Found Admin Channel")
                self.admin_channel = a

            if a.name == "roles":
                print(getTimeStamp("SERVER"), "Found Roles Channel")
                self.roles_channel = a

            if a.name == "emotions-and-serious-stuff":
                print(getTimeStamp("SERVER"), "Found Ant Zone Channel")
                self.ant_zone = a

            if a.name == "server-announcements":
                self.fuck = a

        self.emojiHandler.addVoters(await Voting.create_archived_votes(self))
        self.roleHandler = RoleHandler(self.guild, self.admin_channel, self.roles_channel)

        # Emergency Manual Pin
        # mes = await self.misc.fetch_message("846947559762427924")
        # await self.pinHandler.pin(mes)

        # history = HistoryManager(self.guild, self.database)
        # await history.analyze_history()

    async def on_message(self, message: discord.Message):
        if message.guild.id == active_guild and not message.author.bot:
            await LanguageHandler.determine_language(message)
            if self.emojiHandler is not None:
                await self.emojiHandler.handleEmojiMessage(message)
            if str(message.content).startswith("!role") and message.channel.id == self.admin_channel.id and not message.author.bot:
                self.roleHandler.handle_new_role(message)

    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
        if reaction.guild_id == active_guild:
            await self.pinHandler.handlePinReaction(reaction, self)
            if self.emojiHandler is not None:
                await self.emojiHandler.handleEmojiVoters(reaction)

    # async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        # await self.database.addReaction(reaction)

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

    async def get_members(self):
        out = "["
        bruh = await self.guild.fetch_members()
        member: discord.Member
        for member in bruh:
            out += member.display_name + ","
        return bruh + "]"

client = Client()
client.run(key)
print("MADE IT HERE")