import io
import time

import aiohttp
import discord

def getTimeStamp():
    return "[PINS] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


class PinHandler:

    def __init__(self, channel, guild):
        self.pin_channel = channel
        self.guild = guild
        self.managedPins = []

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
              "  |  " + "**Channel:** " + message.channel.mention + "\n" + message.content

        await self.pin_channel.send(out, files=files)

