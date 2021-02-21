import time
import discord
from EmojiHandler import EmojiHandler
from PinHandler import PinHandler
import LanguageHandler

# DONE separate Emoji stuff into its own class
# DONE clean up timestamps across codebase
# DONE wipe mentions from pins
# DONE record pinned messages in a file and read them on boot
# TODO record emoji votes in a file and read them on boot
# TODO cancel emoji votes after 4 days
# TODO implement 20 day block after submitting an emoji
# TODO implement server-wide cooldown of emoji submission

f = open("key.txt", "r")
key = f.read()


def getTimeStamp(stamp):
    return "[" + stamp + "] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


class Client(discord.Client):

    def __init__(self, *, loop=None, **options):
        super().__init__()
        self.announcements_channel = None
        self.guild = None
        self.pinHandler = None
        self.emojiHandler = None

    async def on_ready(self):

        await client.change_presence(activity=discord.Activity(name='Eat The Rich', type=discord.ActivityType.playing))

        for n in self.guilds:
            # if n.id == 375753471812435968:
            if n.id == 782870393517768704:
                self.guild = n
                print(getTimeStamp("SERVER"), "Found GUILD: " + self.guild.name)

        for a in self.guild.text_channels:
            if a.name == "emoji-voting":
                self.announcements_channel = a
                print(getTimeStamp("SERVER"), "Found Announcements Channel: ", str(self.announcements_channel.id))
                self.emojiHandler = EmojiHandler(self.guild, self.announcements_channel)

            if a.name == "pins":
                print(getTimeStamp("SERVER"), "Found Pins Channel")
                self.pinHandler = PinHandler(a, self.guild)

    async def on_message(self, message):
        await LanguageHandler.determine_language(message)
        await self.emojiHandler.handleEmojiMessage(message)

    async def on_raw_reaction_add(self, reaction):
        await self.emojiHandler.handleEmojiVoters(reaction)
        await self.pinHandler.handlePinReaction(reaction, self)

    async def on_raw_reaction_remove(self, reaction):
        await self.emojiHandler.handleReactionRemoval(reaction)


client = Client()
client.run(key)
