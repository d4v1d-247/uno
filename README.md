# UNO-Bot for Discord
This is a Discord bot, which allows you to play uno with your friends over DMs.
The actual bot is in uno/ and can be imported as a Cog using ```bot.load_extension("uno.Discord_Uno")```. bot.py is a basic bot that can be used to run the cog.

## Installation
1. install discord.py using ```python3 -m pip3 install discord.py```
2. get yourself a bot token from <https://discord.com/developers/applications/> and save it into discord_token.key
3. run the bot using ```python3 bot.py```
4. add the bot to your server

## Usage
When the bot is running you can now type ```!start-uno``` and @mention the people you want to play with. The bot will send you a message with your current cards and the top card of the discard stack. Reply to the message with the number of the card, you want to play or send 0 to draw a card. If you want to play a Wild or +4 Card you have to write the card number and then the first letter of the colour you want seperated by a space (like ```5 y```).
