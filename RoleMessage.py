import time
import discord
from Role import Role


def getTimeStamp():
    return "[ROLE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


class RoleMessage:
    guild: discord.Guild

    # Yeah so this is kinda messy.  Either one can pass in multiple DISCORD roles for creation, or pass in the two kwargs
    # legacy=<legacy_content>, message being a pointer to the content of the message that the roles got announced in and
    # guild=<guild> since we won't get that otherwise
    def __init__(self, *roles: discord.Role, **kwargs):
        self.roles = []
        self.guild = None
        if kwargs.get("guild") is None:
            for role in roles:
                self.roles.append(Role(role=role))
                self.guild = role.guild
        else:
            try:
                self.guild = kwargs.get("guild")
                self.legacy = kwargs.get("legacy")
            except Exception:
                print(getTimeStamp(), "Failed to read RoleMessage from file")

    async def read_roles_from_file(self):
        roles = self.legacy.split("\n")
        guild_roles = await self.guild.fetch_roles()
        for role in roles:
            r = role.split(",")
            guild_role: discord.Role
            for guild_role in guild_roles:
                if r[0].lower().replace(" ", "") == str(guild_role.name).lower().replace(" ", ""):
                    self.roles.append(Role(role=guild_role))

    async def send_role_message(self, category, channel: discord.TextChannel):
        out = "**[" + category + "]**" + "\n"
        if category == "":
            out = "**React with the emoji to recieve the role**\n"
        for role in self.roles:
            out += role.emoji + ": " + role.role.mention + "\n"
        await channel.send(out)

    async def handle_reaction_add(self, reaction: discord.RawReactionActionEvent):
        sender = await self.guild.fetch_member(reaction.user_id)
        for role in self.roles:
            if reaction.emoji == role.emoji:
                await role.add_role_to_user(sender)

    async def handle_reaction_remove(self, reaction: discord.RawReactionActionEvent):
        sender = await self.guild.fetch_member(reaction.user_id)
        for role in self.roles:
            if reaction.emoji == role.emoji:
                await role.remove_role_from_user(sender)