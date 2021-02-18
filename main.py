import discord
from EmojiListener import EmojiListener as Emoji
from Voting import VotingListener

key = "NzgyODUyNzE0MzkyMDU5OTU0.X8SOZw.zNT91hEfbyNKq9BpMtku4olamz8"

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
        self.voters = []
        self.guild = None

    async def on_ready(self):
        for n in self.guilds:
            if n.id == 782870393517768704:
                self.guild = n
            for a in self.guild.text_channels:
                if a.name == "server-announcements":
                    self.announcements_channel = a
                    print("found announcements channel")

    async def on_message(self, message):
        # Update status of Emoji object
        self.check_usage_status()

        # Determine if a user is already adding an emoji
        # try:
        #     print("message.author.name = ", str(message.author.name))
        #     print("self.current_user.name = ", str(self.current_user.name))
        #     print("Is In Use: ", self.in_use())
        #     print("Logic: ", self.in_use() and str(message.author.name) == str(self.current_user.name))
        # except:
        #     pass

        if self.in_use() and str(message.author.name) == str(self.current_user.name):
            print("Name Is The Same Idiot")
            if self.emoji.status == "done":
                self.emoji = None
                return
            elif self.emoji.status == "prompt":
                if await self.emoji.handle_replacement(message.content) is None:
                    await self.emoji.final_image_response(message.content)
                    self.voters.append(VotingListener(self.emoji))

            elif self.emoji.status == "confirm":
                await self.emoji.final_image_response(message.content)
                self.voters.append(VotingListener(self.emoji))

        # At this point we are free to engage with a new emoji addition
        elif message.content.startswith(self.emojiPrefix) and not message.author.bot:
            if not self.in_use():
                self.emoji = Emoji(message, self.announcements_channel, self.guild)
                await self.emoji.emoji_cycle()
                self.current_user = message.author
            else:
                await message.channel.send(get_user_name(self.current_user) + " is currently adding an emoji.  "
                                                                              "Please wait to use the bot.")

    async def on_raw_reaction_add(self, reaction):
        for voter in self.voters:
            if voter.get_message_id() == reaction.message_id:
                val, image, name = voter.add_vote(reaction)
                if val is True:
                    await self.guild.create_custom_emoji(name=name, image=image)

    async def on_raw_reaction_remove(self, reaction):
        for voter in self.voters:
            if voter.get_message_id() == reaction.message_id:
                voter.remove_vote(reaction)

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
