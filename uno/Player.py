"""The player object."""
from __future__ import annotations
from typing import Union

from discord import Member, User

from .Cards import Card

class Player:
	"""The player for the game."""
	def __init__(self, user: Union[Member, User]):
		self.user = user
		self.turn: bool = False
		self.deck: "list[Card]" = []

	def __str__(self) -> str:
		return f"Player {self.user.name}, turn: {self.turn}"

	def __eq__(self, o: Player) -> bool:
		return self.user.id == o.user.id
	
	def receive_card(self, card: Card) -> None:
		"""Add a card to the players deck."""
		self.deck.append(card)
		
		# Sorts the Deck by type and colour for aesthetic purposes
		"""self.deck.sort(key=lambda x: repr(x.type))
		self.deck.sort(key=lambda x: repr(x.colour))"""
