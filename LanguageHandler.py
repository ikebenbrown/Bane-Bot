from googletrans import Translator
import time
import discord
import re

translator = Translator()

def getTimeStamp():
    return "[LANGUAGE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "] "


async def determine_language(message):
    try:

        content = cleanse_emojis(message)

        lang = translator.detect(content)
        if lang.lang == "es" or lang.lang == "de":

            if determinePermissions(message, lang.lang):
                print(getTimeStamp() + message.author.name + " to ", lang.lang, ":", content)
                translation = translator.translate(content).text

                # Check if translation is the same
                if str(translation).lower().replace(" ", "") != content and \
                        str(translation).lower() != content:
                    emojied_translation = replenesh_emojis(message, translation)
                    await message.reply("**Translation:  **" + str(emojied_translation).replace("things", "stuff"),
                                        mention_author=False)
            else:
                print(getTimeStamp() + "Denied", message.author.name, "translation to", lang.lang)
    except TypeError:
        return
    except Exception as e:
        print("[ERROR] " + getTimeStamp() + str(e))


def cleanse_emojis(message: discord.Message):
    out: str
    out = message.content
    match: re.Match
    for match in re.findall("(?<=<)(.*?)(?=>)", out):
        out = out.replace(match, re.findall("(?:[^:]*:s*){2}(.*)", match)[0])
    return out


def replenesh_emojis(message: discord.Message, content):
    match: re.Match
    guild: discord.Guild
    guild = message.guild

    print(content)
    i = 0
    for match in re.findall("(?<=<)(.*?)(?=>)", content):
        match = "<" + match + ">"
        i+=1
        emoji: discord.Emoji
        for emoji in guild.emojis:
            if emoji.id == int(match.replace("<", "").replace(">", "")):
                content = content.replace(match, str(emoji), 1)

    return content

def determinePermissions(message, language):
    if language == "es":
        role_name = "Spanish Speakers"
    elif language == "de":
        role_name = "German Speakers"
    else:
        return False

    for r in message.author.roles:
        if r.name == role_name:
            return True
    return False

