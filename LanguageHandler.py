from googletrans import Translator
import time
import discord

translator = Translator()

# Message cache contains messages in the format of ID
messageCache = []


async def determine_language(message):
    try:
        lang = translator.detect(message.content)
        # print("[LANGUAGE] ", lang)
        if lang.lang == "es" or lang.lang == "de":
            if determinePermissions(message, lang.lang):
                print("[LANGUAGE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]", message.author.name + " to ", lang.lang)
                translation = translator.translate(message.content).text
                if str(translation).lower().replace(" ", "") != message.content and \
                        str(translation).lower() != message.content:
                    messageCache.append([])
                    await message.reply("**Translation:  **" + str(translation).replace("things", "stuff"), mention_author=False)
            else:
                print("[LANGUAGE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]", "Denied", message.author.name, "translation to", lang.lang)
    except Exception as e:
        print("[ERROR] [LANGUAGE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]" + str(e))


def determinePermissions(message, language):
    roleName = None
    if language == "es":
        roleName = "Spanish Speakers"
    elif language == "de":
        roleName = "German Speakers"
    else:
        return False

    for r in message.author.roles:
        if r.name == roleName:
            return True
    return False

