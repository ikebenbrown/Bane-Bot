import io
import time
import aiohttp
import discord


def getTimeStamp():
    return "[PINS] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "] "


def readPins():
    out = []
    file = open("data/pins.max", "r")
    contents = file.read().split(",")
    for m_id in contents:
        try:
            out.append(int(m_id))
        except ValueError:
            print("[ERROR] " + getTimeStamp() + "Invalid message ID: " + m_id)

    return out


async def writePinToFile(message_id):
    file = open("data/pins.max", "a")
    file.write(str(message_id) + ",")
    file.close()


class PinHandler:

    def __init__(self, channel, guild):
        self.pin_threshold = 12
        self.pin_channel = channel
        self.guild = guild
        self.pinned_messages = readPins()

        print(getTimeStamp(), "Created Pin Handler")

    async def pin(self, message):
        print(getTimeStamp(), "Pinning Message From: " + message.author.name)
        self.pinned_messages.append(message.id)
        await writePinToFile(message.id)

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
        if not self.pinned_messages.__contains__(message.id):
            for reaction in message.reactions:
                if reaction.emoji == "📌":
                    if reaction.count == self.pin_threshold:
                        await self.pin(message)
