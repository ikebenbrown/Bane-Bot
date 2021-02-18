import langdetect
from googletrans import Translator
translator = Translator()

async def determine_language(message):
    # try:
    lang = translator.detect(message.content)
    print(lang)
    if lang.lang == "es" or lang.lang == "de":
        print(message.author.name, ":", lang)
        translation = translator.translate(message.content)
        await message.reply("**Translation:  **"+translation.text, mention_author=False)
# except Exception as e:
