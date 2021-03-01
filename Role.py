import time
import discord
import emoji


def getTimeStamp():
    return "[ROLE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


class Role:
    """
    This class represents an abstraction of a role itself.  It is intended to be passed into RoleHandler for multi-role
    messages.  For its constructor, either pass its instantiation message from an admin chat, or a discord Role.  Then, it
    can be addressed to easily add and remove people from said role.
    """
    guild: discord.Guild
    message: discord.Message

    def __init__(self, message: discord.Message = None, role: discord.Role = None):
        self.emoji = None

        if message is not None:
            self.message = message
            self.guild = message.guild
            self.name = None
            self.role = None
        elif role is not None:
            self.name = role.name
            self.guild = role.guild
            self.role = role

        # Prepare to read from roles file to make sure it exists/create it if needed
        self.role_file = "data/" + str(self.guild.id) + "_roles.max"
        # file = open(self.role_file, "a")
        # file.close()

    async def create_role(self):
        valid = await self.interpret_role_message()
        if not valid:
            return

        # If the role already exists, this will return the existing role
        result = await self.is_role_valid()
        if result == "True":
            print(getTimeStamp(), "Creating Role: " + self.name)

            # Create a role with the Gamer Color by default (since that will be most cases)
            self.role = await self.guild.create_role(name=self.name, mentionable=True,
                                                     color=discord.Colour.from_rgb(149, 165, 166))
            await self.message.reply(str(self.role.mention) + " successfully created!")
            self.write_role_to_file()
        else:
            await self.message.reply("Invalid Role!  " + result.mention + " already exists!")

    def write_role_to_file(self):
        role_data = open(self.role_file, "a")
        role_data.write(str(self.role.id) + "," + str(self.emoji)+"\n")
        role_data.close()

    async def add_role_to_user(self, member: discord.Member):
        role: discord.Role
        for role in member.roles:
            if role.id == self.role.id:
                print(getTimeStamp(), "Rejected duplicate role of " + self.name + " to " + member.nick)
                return
        await member.add_roles(self.role)
        print(getTimeStamp(), "Gave " + self.name + " to " + member.nick)

    async def remove_role_from_user(self, member: discord.Member):
        for role in member.roles:
            if role.id == self.role.id:
                await member.remove_roles(role)
                print(getTimeStamp(), "Removed role " + self.name + " from " + member.nick)

    async def interpret_role_message(self):
        try:
            parts = str(self.message.clean_content).split(" ")
            self.name = parts[1]
            try:
                self.emoji = emoji.demojize(parts[2])
                print(self.emoji)
            except:
                await self.message.reply("Invalid emoji!  Please try again")
                return False
            return True
        except Exception:
            await self.message.reply("Incorrect format.  Please use: !role <role> <emoji>")
            return False

    async def is_role_valid(self):
        for role in await self.guild.fetch_roles():
            if str(role.name).replace(" ", "").lower() == self.name.replace(" ", "").lower():
                return role
        return "True"