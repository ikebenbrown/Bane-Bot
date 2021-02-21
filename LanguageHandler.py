from googletrans import Translator
import time
import discord

translator = Translator()

# Message cache contains messages in the format of ID
messageCache = []


def getTimeStamp():
    return "[LANGUAGE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "] "


async def determine_language(message):
    try:
        lang = translator.detect(message.content)
        if lang.lang == "es" or lang.lang == "de":
            if determinePermissions(message, lang.lang):
                print(getTimeStamp() + message.author.name + " to ", lang.lang)
                translation = translator.translate(message.content).text
                if str(translation).lower().replace(" ", "") != message.content and \
                        str(translation).lower() != message.content:
                    messageCache.append([])
                    await message.reply("**Translation:  **" + str(translation).replace("things", "stuff"), mention_author=False)
            else:
                print(getTimeStamp() + "Denied", message.author.name, "translation to", lang.lang)
    except TypeError:
        return
    except Exception as e:
        print("[ERROR] " + getTimeStamp() + str(e))


def determinePermissions(message, language):
    role_name = None
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

