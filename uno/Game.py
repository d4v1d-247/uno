"""The UNO game class."""
from typing import Union, Sequence
import random
import logging

from . import Cards
from .Player import Player

log = logging.getLogger(__name__)

class NotYourTurnException(Exception):
	pass
class WrongCardException(Exception):
	pass
class MissingColourException(Exception):
	pass

class Game:
	"""The UNO game."""
	def __init__(self, players: Sequence[Player], id: int, starter_cards: int = 7):
		self.id = id
		self.players = list(players)
		self.discard: Cards.Card = Cards.Card(  # The current Card on the discard
			random.choice(list(Cards.CardType)[:10]),  # Only use number cards
			random.choice(list(Cards.CardColour))
		)
		self.drawstack: "list[Cards.Card]" = []

		self.turn = 0  # Whose turn it is
		self.direction = 1  # 1 or -1
		self.drawcache: int = 1  # How many cards have to be drawn
		self.skip: bool = False  # Wether the next Person gets skipped

		# Give the players the starter cards
		for _ in range(starter_cards):
			for player in self.players:
				player.receive_card(self._random_card())
		
		self.players[0].turn = True
		log.debug(f"Players: {self.players}")

	def _random_card(self) -> Cards.Card:
		"""Return a random card from the drawstack.

		If the drawstack is empty, it will be regenerated
		using the following cards:
		two of each number from 1-9, reverse, skip and draw2 for each colour,
		a 0 for every colour,
		four Wild and four Wild Draw cards
		"""
		if len(self.drawstack) < 1:
			for col in list(Cards.CardColour):
				# Numbers 1-9 + Skip, Reverse, Draw2
				for typ in list(Cards.CardType)[1:13]:
					self.drawstack.append(Cards.Card(typ, col))
					self.drawstack.append(Cards.Card(typ, col))
				self.drawstack.append(Cards.Card(Cards.CardType.NUMBER0, col))
			for _ in range(4):
				self.drawstack.append(Cards.Card(Cards.CardType.WILD))
				self.drawstack.append(Cards.Card(Cards.CardType.WILD_DRAW))
			random.shuffle(self.drawstack)

		return self.drawstack.pop()

	def check_win(self) -> Union[Player, None]:
		"""Check wether a Player won the game."""
		for player in self.players:
			if len(player.deck) == 0:
				return player
		
		return None
	
	def next_turn(self) -> int:
		"""Continues to the next turn and returns the current player."""
		old = self.turn
		if self.skip:
			self.skip = False
			self.next_turn()
		self.players[self.turn].turn = False
		self.turn = (self.turn + self.direction) % len(self.players)
		self.players[self.turn].turn = True

		log.debug(f"Continued from turn {old} to {self.turn}")
		return self.turn

	def play_card(
		self,
		player_n: int,
		card_n: int,
		colour: Union[Cards.CardColour, None] = None
	) -> Union[bool, None]:
		"""Play a card from a player.
		
		Returns True on success.
		"""
		log.debug(f"Turn: {self.turn}, Player: {player_n}, card: {card_n}")
		if self.turn != player_n:
			raise NotYourTurnException(f"It wasn't Player {player_n}s turn.")
		
		player = self.players[player_n]
		card = player.deck[card_n]
		if card.type in {Cards.CardType.WILD, Cards.CardType.WILD_DRAW}:
			if colour == None:
				raise MissingColourException(
					f"You need to specify a colour, when playing a {card.type}")
			card.colour = colour
			log.debug(f"Set colour to {repr(card.colour)}")
		
		if not card.playable(self.discard, self.drawcache > 1):
			raise WrongCardException(
				f"{player.deck[card_n]} can't be played onto {self.discard}"
			)
		
		if card.type == Cards.CardType.DRAW:
			self.drawcache += 2
		elif card.type == Cards.CardType.WILD_DRAW:
			self.drawcache += 4
		elif card.type == Cards.CardType.SKIP:
			self.skip = True
		elif card.type == Cards.CardType.REVERSE:
			self.direction *= -1

		self.discard = player.deck.pop(card_n)
		return True

	def draw_card(self, player_n: int) -> Union[bool, None]:
		"""Draw a card from the drawstack for a player.
		
		Returns True on success.
		"""
		if self.turn != player_n:
			raise NotYourTurnException(f"It wasn't Player {player_n}s turn.")

		if self.drawcache > 1:
			self.drawcache -= 1
		
		for _ in range(self.drawcache):
			self.players[player_n].receive_card(self.drawstack.pop())
		self.drawcache = 1
		
		return True
