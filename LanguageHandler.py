import langdetect
from googletrans import Translator
import time

translator = Translator()

# Message cache contains messages in the format of ID
messageCache = []

async def determine_language(message):
    try:
        lang = translator.detect(message.content)
        # print("[LANGUAGE] ", lang)
        if lang.lang == "es" or lang.lang == "de":
            print("[LANGUAGE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]", message.author.name + " to ", lang.lang)
            translation = translator.translate(message.content).text
            if str(translation).lower().replace(" ", "") != message.content and \
                    str(translation).lower() != message.content:
                messageCache.append([])
                await message.reply("**Translation:  **" + str(translation).replace("things", "stuff"), mention_author=False)
    except Exception as e:
        print("[ERROR] [LANGUAGE] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]" + str(e))
