import time
import discord

import ImageProcessor as ip


async def send_message(channel, message):
    return await channel.send(message)


class EmojiListener:
    emojiPrefix = "!emoji"
    current_user = None
    in_use = True
    status = "Start"

    def __init__(self, message, a, guild):
        self.guild = guild
        self.ann_channel = a
        self.message = message
        self.current_user = message.author
        self.name = None
        self.image = None
        self.voter_message = None
        self.toBeReplaced = None
        print(message.guild)

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

    async def handle_image(self):
        attachment = self.message.attachments[0]
        self.name = self.message.content.replace(self.emojiPrefix + " ", "")
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
        original = ["oneMoreTest", "THUMB", "TOUNGE", "fats", "IKE1", "swarm", "DUNC", "LUKE", "DOG", "TOM3", "FROWN", "QUINN",
                    "BJ", "namejeff", "SPAGHETTI", "MM", "HOT3", "URK"]
        queue = []
        for e in original:
            for emoji in self.guild.emojis:
                if e == emoji.name:
                    queue.append(e)
        print("OLD EMOJIS = " + str(queue))
        return queue

    async def handle_replacement(self, response):
        if response.lower() == "yes":
            self.status = "confirm"
            print("name = " + self.name)
            for emoji in self.guild.emojis:
                if emoji.name == self.name:
                    print("Replacing emoji with same name")
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
                        print("Replacing " + emoji.name + " from replacement queue")
                        self.toBeReplaced = emoji
                        await self.message.channel.send(
                            "Creating this emoji will remove " + str(emoji) + ".  Are you sure you "
                                                                              "want to do this?  "
                                                                              "Respond with yes or "
                                                                              "no.")
                        return emoji.name
            return None
        else:
            await send_message(self.message.channel, "Understood.  Aborting operation.")
            self.deactivate()

    async def final_image_response(self, response):
        if response.lower() == "yes":

            posrep = None
            for emoji in self.guild.emojis:
                if emoji.name == "posrep":
                    posrep = emoji

            await send_message(self.message.channel, "Understood. Sending **:" + self.image.original_name
                               + ":** emoji to a vote now.")

            await self.ann_channel.send(file=discord.File(self.image.name + '.png'))
            if self.toBeReplaced is None:
                self.voter_message = await send_message(self.ann_channel,
                                                        "If this post receives 15 " + str(posrep) +
                                                        "s, the above image will be implemented as the **:" + self.name +
                                                        ":** emoji.")
            else:
                self.voter_message = await send_message(self.ann_channel,
                                                        "If this post receives 15 " + str(posrep) +
                                                        "s, the above image will be implemented as the **:" + self.name +
                                                        ":** emoji, thus removing " + str(self.toBeReplaced))
            self.deactivate()
        else:
            await send_message(self.message.channel, "Understood.  Aborting operation.")
            self.deactivate()

    def deactivate(self):
        print("[" + str(time.time()) + "] " + "Engagement with " + self.message.author.name + "Complete.  Destroying "
                                                                                              "EmojiListener Instance.")
        self.in_use = False
        self.current_user = None
        self.status = "done"
