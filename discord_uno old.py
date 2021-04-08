"""A Discord Bot that makes it possible to play UNO over DMs."""
import discord

from game import Game
from game import Player
from game import NotYourTurnException
from game import WrongCardException
from cards import CardColour

bot = discord.Client()

game = None
users = []

async def show_player(player: Player):
	global game
	col: discord.Color = discord.Color.green() if player.turn else discord.Color.dark_gray()

	turn: str = game.players[game.turn].name.name

	emb = discord.Embed(
		colour=col,
		title=f"UNO-Game - It's {turn}s turn",
		description="Type 0 to draw a card or the card number to play that card."
	)

	emb.add_field(name="Draw", value=game.drawcache-1)
	emb.add_field(name="Discard", value=str(game.discard))
	emb.add_field(name="Cards Left", value="\n".join([f"{pl.name.name}: {len(pl.deck)}" for pl in game.players]))
	emb.add_field(name="Your Cards", value="    ".join([f"{i+1}.{str(card)}" for i, card in enumerate(player.deck)]))
	
	await player.name.send(embed=emb)

async def win_message(player: Player):
	global game
	emb = discord.Embed(
		colour=discord.Colour.red(),
		title=f"UNO-Game - {player.name.name} won!"
	)

	for p in game.players:
		await p.name.send(embed=emb)

@bot.event
async def on_message(msg: discord.Message):
	global game
	global users
	COLORS = {
		"r": CardColour.RED,
		"g": CardColour.GREEN,
		"b": CardColour.BLUE,
		"y": CardColour.YELLOW,
		"": None  # remove in refactor to ensure user specifies colour
	}
	if msg.author == bot.user:
		return
	
	if isinstance(msg.channel, discord.DMChannel):
		text = msg.content.split(" ")
		if len(text) < 2:
			text.append("")
		u_index = users.index(msg.author)

		success = False
		try:
			if text[0] == "0":
				success = game.draw_card(u_index)
			else:
				success = game.play_card(u_index, int(text[0])-1, COLORS[text[1].lower()])
		except (ValueError, IndexError):
			await msg.author.send("Invalid Card. Use number!")
		except KeyError:
			await msg.author.send("Invalid color: use r, g, b or y!")
		except WrongCardException as e:
			await msg.author.send(e.args[0])
		except NotYourTurnException as e:
			await msg.author.send(e.args[0])
		
		if success:
			if game.check_win():
				await win_message(game.check_win())
				game = None
			else:
				game.next_turn()
			for player in game.players:
				await show_player(player)
		
	elif msg.content.startswith("!start-uno"):
		users = []

		users.append(msg.author)
		users += msg.mentions

		invite = discord.Embed(
			colour=discord.Color.green(),
			description=f"You have been invited to a UNO game by {msg.author}.",
			title="UNO-Invite")
		
		for user in users:
			await user.send(embed=invite)
		
		game = Game([Player(p) for p in users])
		await show_player(game.players[0])

with open("discord_api.key") as f:
	KEY = f.readline()

bot.run(KEY)
