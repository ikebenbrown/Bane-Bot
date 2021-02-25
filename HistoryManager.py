import datetime
import time
from operator import itemgetter

import discord


def getTimeStamp():
    return "[HISTORY] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


# This file has some comments.  Don't get used to it.
class HistoryManager:
    guild: discord.Guild

    def __init__(self, guild):
        self.guild = guild
        self.reactions = []
        self.message_count = 0

    async def analyze_history(self):
        server_announcements = None
        for channel in self.guild.text_channels:

            # Iterate through all channels.  If we can't read a channel, ignore it.
            try:
                await self.analyze_channel_history(channel)
            except discord.errors.Forbidden:
                print("[ERROR]", getTimeStamp(), "No access to read " + channel.name)

            # If the channel we're reading is server-announcements, save it for later
            if channel.name == "server-announcements":
                server_announcements = channel

        print("MESSAGE COUNT: ", self.message_count)
        # self.sort_reactions()
        # self.print_reaction_data()
        # await self.send_reaction_data(server_announcements)

    async def analyze_channel_history(self, channel: discord.TextChannel):
        message: discord.Message
        one_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        async for message in channel.history(limit=None, after=one_month_ago):
            self.message_count += 1
            for reaction in message.reactions:
                self.update_reaction(reaction)
        print(getTimeStamp(), "Successfully analyzed", channel.name)

    def update_reaction(self, react: discord.Reaction):
        if react.custom_emoji:
            for reaction in self.reactions:
                if reaction[0] == str(react.emoji):
                    reaction[1] = react.count + reaction[1]
                    return
            self.reactions.append([str(react.emoji), react.count])
            return
        return

    def sort_reactions(self):
        sorted_reactions = sorted(self.reactions, key=itemgetter(1), reverse=True)
        self.reactions = sorted_reactions

    def print_reaction_data(self):
        for reaction in self.reactions:
            print(reaction[0] + "," + str(reaction[1]))

    async def send_reaction_data(self, channel: discord.TextChannel):
        out = "**[Monthly Emoji Usage]**\n"
        for reaction in self.reactions:

            # Parse the reaction's ID out of the string
            id = str(reaction[0].split(">")[0]).split(":")[2]

            # Check if the emoji is still in the server
            for emoji in self.guild.emojis:
                # If the emoji is found, append it to the message
                if str(emoji.id) == str(id):
                    out += reaction[0] + ": " + str(reaction[1]) + "\n"
                    break

        # Send the Monthly Emoji Usage data message to the desired channel
        await channel.send(out)
