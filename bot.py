import logging

import discord.ext.commands as commands

logger = logging.getLogger("uno")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%H:%M:%S"))
file_handler = logging.FileHandler("debug.log", encoding='utf-8', mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s\tin %(filename)s:%(funcName)s:%(lineno)d => %(message)s"))
logger.addHandler(file_handler)
logger.addHandler(console_handler)

bot = commands.Bot(command_prefix="!", case_insensitive=True)

@bot.event
async def on_ready():
	logger.info(f"Bot startet as {bot.user}")
	bot.load_extension("uno.Discord_Uno")

try:
	with open("discord_token.key") as f:
		TOKEN = f.readline()
except FileNotFoundError:
	logger.critical("Couldn't start bot. You have to create a discord_token.key file with your bots token in it.")
	exit()

bot.run(TOKEN)
