"""The Uno Bot Cog."""
from typing import Union, Any
import logging

import discord
import discord.ext.commands as commands

from . import Game

log = logging.getLogger(__name__)

DC_Clients = Union[discord.Member, discord.User]

class Uno(commands.Cog):
	"""The UNO game cog."""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.games: "dict[int, Game.Game]" = {}
		self.users: "dict[int, int]" = {}  # {user_id: game_id}

	@commands.Cog.listener()
	async def on_message(self, msg: discord.Message) -> None:
		"""Handle the game process over DMs."""
		author = msg.author
		if (author == self.bot.user or
		not isinstance(msg.channel, discord.DMChannel)):
			return

		COLORS = {
			"r": Game.Cards.CardColour.RED,
			"g": Game.Cards.CardColour.GREEN,
			"b": Game.Cards.CardColour.BLUE,
			"y": Game.Cards.CardColour.YELLOW,
			"": None
		}
		try:
			user_pos = self.users[author.id]
			game = self.games[user_pos]
			player_pos = [p.user for p in game.players].index(author)
		except KeyError:
			await author.send("You have to be in a game to play. "
			"Start a game with `!start-game` and "
			"@mention the people you want to play with.")
			return

		text = msg.content.split(" ")
		if len(text) < 2:
			text.append("")

		success = False
		try:
			if text[0] == "0":
				success = game.draw_card(player_pos)
			else:
				success = game.play_card(
					player_pos,
					int(text[0])-1,
					COLORS[text[1].lower()])
		except (ValueError, IndexError):
			await author.send("Invalid Card. Use number!")
		except KeyError:
			await author.send("Invalid color: use r, g, b or y!")
		except (
			Game.WrongCardException,
			Game.NotYourTurnException,
			Game.MissingColourException) as e:
			await author.send(e.args[0])

		if not success:
			return
		
		if winner := game.check_win():
			await Uno.show_win(game, winner)
			self._end_uno(game)
			return
		else:
			game.next_turn()
		for p in game.players:
			await Uno.show_status(game, p)

	@commands.command("start-uno")
	async def start_uno(self, ctx: commands.Context) -> None:
		"""Start a uno game with the @mentioned users."""
		# Get Discord Users
		users: "list[DC_Clients]" = [ctx.author]
		users += [u for u in ctx.message.mentions if
			isinstance(u, (discord.Member, discord.User))] 

		# Check if Users are already in a game
		if unavailable := [int(u.id) for u in users if u.id in self.users.keys()]:
			log.debug(f"Unavailable players are {unavailable}")
			unavailable = ', '.join([f"<@{str(id)}>" for id in unavailable])
			await ctx.send(
				f"Can't start game, because {unavailable} are already in a game.")
			return
		
		# Create Game and add users to list
		game_id = Uno._find_first_unused_key(self.games)
		game = Game.Game([Game.Player(p) for p in users], game_id)
		self.games[game_id] = game
		for i, user in enumerate(users):
			self.users[user.id] = game_id
			await Uno.show_status(game, game.players[i])
		
		log.info(f"Started game {game_id} with users {[u.name + f':{u.discriminator}' for u in users]}")
	
	@commands.command("leave")
	async def leave(self, ctx: commands.Context):
		await self._leave_uno(ctx.author.id)

	async def _leave_uno(self, uid: int):
		"""Remove a player from their game."""
		game_id = self.users.pop(uid)
		game = self.games[game_id]
		game.players = (
			[u for u in game.players if u.user.id != uid])

		if len(game.players) == 0:
			self._end_uno(game)
			return
		
		for p in game.players:
			await Uno.show_status(game, p)

	def _end_uno(self, game: Game.Game) -> None:
		"""Stop a game and remove the users."""
		# Remove Players from users
		for u in game.players:
			self.users.pop(u.user.id)

		# Remove game from games
		self.games.pop(game.id)

		log.info(
			f"Ended game {game.id} with users"
			f" {[u.user.name for u in game.players]}")

	@staticmethod
	def _find_first_unused_key(dic: "dict[int, Any]") -> int:
		"""Find the first unused integer key of a dictionary."""
		key = 0
		while key in dic.keys():
			key += 1
		return key
	
	@staticmethod
	async def show_status(game: Game.Game, player: Game.Player) -> None:
		"""Show the current status of the game to the player."""
		colour = discord.Color.green() if player.turn else discord.Color.dark_gray()
		turn = game.players[game.turn].user.name

		emb = discord.Embed(
			color=colour,
			title=f"UNO-Game - It's {turn}s turn",
			description="Type 0 to draw a card or the card number to play that card."
		)

		players = [f"{pl.user.name}: {len(pl.deck)}" for pl in game.players]
		cards = [f"{i+1}.{str(card)}" for i, card in enumerate(player.deck)]

		emb.add_field(name="Draw", value=str(game.drawcache-1))
		emb.add_field(name="Discard", value=str(game.discard))
		emb.add_field(name="Cards Left", value="\n".join(players))
		emb.add_field(name="Your Cards", value=" ".join(cards))

		await player.user.send(embed=emb)
		log.debug(f"Showed game status of game {game.id} to {player.user}")

	@staticmethod
	async def show_win(game: Game.Game, winplayer: Game.Player) -> None:
		"""Show a win message to all players of a game."""
		emb = discord.Embed(
			color=discord.Color.red(),
			title=f"UNO-Game - {winplayer.user.name} won!"
		)

		for p in game.players:
			if p == winplayer:
				emb.color = discord.Color.green()
			else:
				emb.color = discord.Color.red()
			await p.user.send(embed=emb)

def setup(bot: commands.Bot):
	bot.add_cog(Uno(bot))
	log.info("Loaded Uno-Cog")
