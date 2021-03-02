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
        if kwargs is None:
            for role in roles:
                self.roles.append(Role(role=role))
                self.guild = role.guild
        else:
            try:
                self.guild = kwargs.get("guild")
                self.read_roles_from_file(kwargs.get("legacy"))
            except Exception:
                print(getTimeStamp(), "Failed to read RoleMessage from file")

    async def read_roles_from_file(self, legacy: str):
        roles = legacy.split("\n")
        guild_roles = await self.guild.fetch_roles()
        for role in roles:
            r = role.split(",")
            guild_role: discord.Role
            for guild_role in guild_roles:
                if r[0].lower().replace(" ", "") == str(guild_role.name).lower().replace(" ", ""):
                    self.roles.append(Role(role=guild_role))

    async def send_role_message(self, category, channel: discord.TextChannel):
        out = "**[" + category + "]**" + "\n"
        for role in self.roles:
            out += role.emoji + ": " + role.name + "\n"
        await channel.send(out)