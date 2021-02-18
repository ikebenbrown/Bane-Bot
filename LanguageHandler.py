import langdetect
from googletrans import Translator
import time
translator = Translator()

async def determine_language(message):
    try:
        lang = translator.detect(message.content)
        # print("[LANGUAGE] ", lang)
        if lang.lang == "es" or lang.lang == "de":
            print("[LANGUAGE] ["+time.strftime('%Y-%m-%d %H:%M:%S')+"]", message.author.name+":", lang.lang)
            translation = translator.translate(message.content)
            await message.reply("**Translation:  **"+translation.text, mention_author=False)
    except Exception as e:
        print("[LANGUAGE] Failed:", e)
