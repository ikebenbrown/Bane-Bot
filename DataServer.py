import mysql.connector
import discord
import emoji

class MySQLHandler():

    def __init__(self):
        self.mydb = mysql.connector.connect(
          host="localhost",
          user="max",
          password="Maxtucker1"
        )
        self.mydb.connect()
        self.cursor = self.mydb.cursor()
        self.cursor.execute("USE dangerousdata;")

    def createChannelTable(self, channel: discord.TextChannel):

        name = channel.name
        if str(name).startswith("school-work-sports"):
            name = "ssr"

        self.cursor.execute('SHOW TABLES')
        tables = self.cursor.fetchall()
        for table_name in tables:
            for item in table_name:
                if name == item:
                    return
        print("DIDN'T FIND TABLE FOR", name)
        self.cursor.execute(
            'CREATE TABLE `dangerousdata`.`' + name + "` ( `reactor` LONGTEXT NOT NULL, `reactee` LONGTEXT NOT NULL, "
                                                           "`reaction` LONGTEXT NOT NULL, `date` DATETIME NULL);"
        )

    async def addReaction(self, reaction: discord.Reaction):
        try:
            message: discord.Message
            message = reaction.message
            name = message.channel.name

            if str(name).startswith("school-work-sports"):
                name = "ssr"

            emoji_name = ""
            if reaction.custom_emoji:
                emoji_name = reaction.emoji.name
            else:
                emoji_name = str(emoji.demojize(reaction.emoji)).replace(":","")

            date = str(message.created_at).split(".")[0]

            user: discord.User
            async for user in reaction.users():
                #command = 'INSERT INTO `' + name + '` VALUES ("' + user.name + '","' + message.author.name + '","' + emoji_name + '","' + date + '")'
                command = f'INSERT INTO `{name}` VALUES ("{user.name}","{message.author.name}","{emoji_name}","{date}")'
                self.cursor.execute(command)
                self.mydb.commit()
        except:
            pass
