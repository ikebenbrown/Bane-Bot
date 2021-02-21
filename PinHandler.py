import io
import time
import aiohttp
import discord


def getTimeStamp():
    return "[PINS] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


class PinHandler:

    def __init__(self, channel, guild):
        self.pin_threshold = 1
        self.pin_channel = channel
        self.guild = guild

        print(getTimeStamp(), "Created Pin Handler")

    async def pin(self, message):
        print(getTimeStamp(), "Pinning Message From: " + message.author.name)

        files = []
        for attachment in message.attachments:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status != 200:
                        print(getTimeStamp(), "[ERROR] Couldn't download file")
                    data = io.BytesIO(await resp.read())
                    files.append(discord.File(data, attachment.filename))

        out = str(message.jump_url) + "\n" + "**Author:** " + message.author.mention + \
              "  |  " + "**Channel:** " + message.channel.mention + "\n" + message.clean_content

        await self.pin_channel.send(out, files=files)

    async def handlePinReaction(self, reaction, client):
        channel = client.get_channel(reaction.channel_id)
        message = await channel.fetch_message(reaction.message_id)
        for reaction in message.reactions:
            if reaction.emoji == "📌":
                if reaction.count == self.pin_threshold:
                    await self.pin(message)

