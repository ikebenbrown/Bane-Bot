import discord
import time


def getTimeStamp():
    return "[ROLE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"


class RoleHandler:

    def __init__(self, guild, admin_channel):
        self.guild = guild
        self.admin_channel = admin_channel
