import discord
import time

from Role import Role
from RoleMessage import RoleMessage


def getTimeStamp():
    return "[ROLE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


class RoleHandler:

    def __init__(self, guild, admin_channel, roles_channel):
        self.guild = guild
        self.admin_channel = admin_channel
        self.roles_channel = roles_channel

    async def handle_new_role(self, message):
        role = Role(message)
        await role.create_role()
        role_message = RoleMessage(role.role)
        await role_message.send_role_message("", self.roles_channel)
