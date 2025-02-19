import datetime
import time
import discord

import ImageProcessor as ip


def getTimeStamp():
    return "[EMOJI] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "] "


async def send_message(channel, message):
    return await channel.send(message)


class EmojiListener:
    emojiPrefix = "!emoji"
    current_user = None
    in_use = True
    status = "Start"

    def __init__(self, message, a, guild, voter_message):
        self.in_use = True
        self.desc = ""
        self.guild = guild
        self.ann_channel = a
        self.message = message
        self.current_user = message.author
        self.name = None
        self.image = None
        self.voter_message = voter_message
        self.toBeReplaced = None
        self.time = message.created_at

    async def createArchivedEmojiListener(self):
        await self.handle_image()

    def get_voter_message(self):
        return self.voter_message

    async def emoji_cycle(self):
        if len(self.message.attachments) == 0:
            await send_message(self.message.channel, "Incorrect format: Emoji image must be attached to !emoji message"
                                                     " with the emoji name.")
            await send_message(self.message.channel, "Example: !emoji posrep (with image file attached)")
            self.deactivate()
        elif len(self.message.attachments) == 1:
            await self.handle_image()
        else:
            await send_message(self.message.channel, "Please only attach one emoji at a time.")
            self.deactivate()

    # This is only for the recreation of votes after a bot restart
    async def handle_image_silent(self):
        attachment = self.message.attachments[0]
        message = str(self.message.content).split(" ")
        self.name = message[1].lower()
        self.image = ip.ImageProcessor(attachment, self.name)

        if self.image.image_state == "bad":
            await self.image.downscale_skew()
        elif self.image.image_state == "square":
            await self.image.downscale()
        else:
            await self.image.download_image()

    async def handle_image(self):
        attachment = self.message.attachments[0]
        message = str(self.message.content).split(" ")

        if len(message) <= 2:
            await send_message(self.message.channel, "What the fuck does **" + str(message[1]) + "** even mean?  Next time, write the description after the name of the emoji.")
            self.deactivate()
            return
        else:

            i = 0
            for word in message:
                if i >= 2:
                    self.desc += word + " "
                i += 1

            self.name = message[1].lower()
            self.image = ip.ImageProcessor(attachment, self.name)
            if self.image.image_state == "bad":
                await self.handle_bad_image()
            elif self.image.image_state == "square":
                await self.square_image_prompt()
            else:
                await self.ideal_image_prompt()

    async def handle_bad_image(self):
        await send_message(self.message.channel, "**Warning:** The submitted emoji is not square, therefore it is not "
                                                 "the maximum size.  Regardless, I've automatically downscaled the "
                                                 "emoji and have posted the result below.  Would you like to submit "
                                                 "the result as the **:" + self.image.original_name +
                           ":** emoji?  Please respond with 'yes' or 'no'.")
        self.status = "prompt"
        await self.image.downscale_skew()
        await self.message.channel.send(file=discord.File(self.image.name + '.png'))

    async def square_image_prompt(self):
        await send_message(self.message.channel, "I've automatically downscaled the emoji and have posted the result "
                                                 "below.  Would you like to submit the result as the **:" +
                           self.image.original_name + ":** emoji?  Please respond with 'yes' or 'no'.")
        self.status = "prompt"
        await self.image.downscale()
        await self.message.channel.send(file=discord.File(self.image.name + '.png'))

    async def ideal_image_prompt(self):
        await send_message(self.message.channel, "**Confirmation**: Would you like to submit the following image as "
                                                 "the **:" + self.image.original_name + ":** emoji? Please respond "
                                                                                        "with 'yes' or 'no'.")
        self.status = "prompt"
        await self.image.download_image()
        await self.message.channel.send(file=discord.File(self.image.name + '.png'))

    def create_replacement_queue(self):
        original = ['COLE', 'Cringe', 'sadizzy', 'grill', 'FUNNY', 'whisk', 'bootlicker']
        queue = []
        for e in original:
            for emoji in self.guild.emojis:
                if e == emoji.name:
                    queue.append(e)
        print(getTimeStamp() + "Created Replacement Queue: " + str(queue))
        return queue

    async def handle_replacement(self, response):
        if response.lower() == "yes":
            self.status = "confirm"
            for emoji in self.guild.emojis:
                if emoji.name == self.name:
                    print(getTimeStamp() + "Replacing emoji with same name")
                    self.toBeReplaced = emoji
                    await self.message.channel.send(
                        "Creating this emoji will overwrite " + str(emoji) + ".  Are you sure you "
                                                                             "want to do this?  "
                                                                             "Respond with yes or "
                                                                             "no.")
                    return emoji.name
            for old in self.create_replacement_queue():
                for emoji in self.guild.emojis:
                    if emoji.name == old:
                        print(getTimeStamp() + "Replacing " + emoji.name + " from replacement queue")
                        self.toBeReplaced = emoji
                        await self.message.channel.send(
                            "Creating this emoji will remove " + str(emoji) + ".  Are you sure you "
                                                                              "want to do this?  "
                                                                              "Respond with yes or "
                                                                              "no.")
                        return emoji.name
            return None
        else:
            await send_message(self.message.channel, "Understood and ignored.")
            self.deactivate()

    async def final_image_response(self, response):
        if response.lower() == "yes":

            posrep = None
            for emoji in self.guild.emojis:
                if emoji.name == "posrep":
                    posrep = emoji

            await send_message(self.message.channel, "Understood. Sending **:" + self.image.original_name
                               + ":** emoji to a vote now.")

            vote_end = str(self.message.created_at +
                           datetime.timedelta(days=4) + datetime.timedelta(hours=6)).split(".")[0]

            await self.ann_channel.send(file=discord.File(self.image.name + '.png'))
            if self.toBeReplaced is None:
                self.voter_message = await send_message(self.ann_channel,"**[Emoji Vote]**\n"
                                                        "**Name:** :" + self.name + ":\n" +
                                                        "**Description:** " + self.desc + "\n" +
                                                        "**Author:** " + self.message.author.mention + "\n" +
                                                        "**Voting Threshold: ** 15 " + str(posrep) + "s" + "\n" +
                                                        "**Vote End** (CST): " + vote_end)
            else:
                self.voter_message = await send_message(self.ann_channel,"**[Emoji Vote]**\n"
                                                        "**Name:** :" + self.name + ":\n" +
                                                        "**Description:** " + self.desc + "\n" +
                                                        "**Author:** " + self.message.author.mention + "\n" +
                                                        "**Voting Threshold: ** 15 " + str(posrep) + "s\n" +
                                                        "**Replaced Emoji:** " + str(self.toBeReplaced) + "\n" +
                                                        "**Vote End** (CST): " + vote_end)
            self.deactivate()
        else:
            # await send_message(self.message.channel, "Understood.  Aborting operation.")
            self.deactivate()

    def deactivate(self):
        print(getTimeStamp() + "Engagement with " + self.message.author.name + "Complete.  Destroying "
                                                                                              "EmojiListener Instance.")
        self.in_use = False
        self.current_user = None
        self.status = "done"
