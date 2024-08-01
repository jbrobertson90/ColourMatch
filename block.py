import random

import pygame

class Block:
	"""Class to represent the basic block in the game."""

	def __init__(self, cm_game):
		"""Initialise the blocks properties."""
		# Set attributes from rest of game that block needs to access.
		self.cm_game = cm_game
		self.settings = self.cm_game.settings
		self.screen = self.cm_game.screen
		self.screen_rect = self.screen.get_rect()
		self.screen_width, self.screen_height = self.screen_rect.size

		# Create the blocks image and get its rect.
		self.image = pygame.Surface((self.settings.block_width,
									 self.settings.block_height))
		self.rect = self.image.get_rect()

		# Random chance to create a "special" block,
		#	else give the block a standard colour.
		special_chance = random.uniform(0, 1)
		if special_chance > 0.9:
			self.special = True
			self._apply_special_block()
		else:
			self.special = False
			self.colour = random.choice(self.settings.colour_list)
			self.image.fill(self.colour)

		# Give block its starting position:
		#	 top of the screen, at a random horizonal position.
		self.rect.y = 0

		# Choose random position at discrete intervals based on block width
		# 	so blocks line up in columns correctly.
		#	(Block at self.settings.blocks_per_row would be just off right of
		#	screen so reduce range by 1 to avoid this)
		self.random_start_position = random.randint(
										0, (self.settings.blocks_per_row - 1))

		# Create float to track block's vertical position more accurately.
		self.y = float(self.rect.y)

		# Create hit boxes for detecting collisions between blocks.
		self._create_hit_boxes()

	def update(self):
		"""Update the blocks vertical position."""
		if self.rect.bottom < self.screen_rect.bottom:
			self.y += self.settings.block_speed
			self.rect.y = self.y
			self.align_hit_boxes()
			if self.special:
				self.label_image_rect.center = self.rect.center

	def move_block_right(self):
		"""Move the block right 1 space."""
		if self.rect.right < self.screen_rect.right:
			self.rect.x += self.settings.block_width
			self.align_hit_boxes()

	def move_block_left(self):
		"""Move the block left 1 space."""
		if self.rect.left > 0:
			self.rect.x -= self.settings.block_width
			self.align_hit_boxes()

	def draw_block(self):
		"""Draw the block to the screen."""
		self.screen.blit(self.image, self.rect)
		if self.special:
			self.screen.blit(self.label_image, self.label_image_rect)

	def _create_hit_boxes(self):
		"""Create hit boxes for the block to detect collisions."""
		# Create 1 pixel wide hit box at left of block.
		self.left_hit_box = pygame.Surface((1, self.settings.block_height))
		self.left_hit_box_rect = self.left_hit_box.get_rect()
		self.left_hit_box_rect.midright = self.rect.midleft

		# Create 1 pixel wide hit box at right of block.
		self.right_hit_box = pygame.Surface((1, self.settings.block_height))
		self.right_hit_box_rect = self.right_hit_box.get_rect()
		self.right_hit_box_rect.midleft = self.rect.midright

		# Create 1 pixel high hit box at bottom of block.
		self.bottom_hit_box = pygame.Surface((self.settings.block_width, 1))
		self.bottom_hit_box_rect = self.bottom_hit_box.get_rect()
		self.bottom_hit_box_rect.midtop = self.rect.midbottom

	def align_hit_boxes(self):
		"""
		Make sure hit boxes are lined up with block correctly after
		moving the block.
		"""
		self.left_hit_box_rect.midright = self.rect.midleft
		self.right_hit_box_rect.midleft = self.rect.midright
		self.bottom_hit_box_rect.midtop = self.rect.midbottom

	def _apply_special_block(self):
		"""Apply attributes for special blocks."""
		self.colour = (255, 255, 255)
		self.image.fill(self.colour)

		# Decide if type 1 or type 2 special block.
		type_chance = random.uniform(0, 1)
		if type_chance > 0.5:
			self.special_type = 1
		else:
			self.special_type = 2

		if self.special_type == 1:
			self.text = "D"
		elif self.special_type == 2:
			self.blast_radius = random.randint(2, 5)
			self.text = str(self.blast_radius)

		self.text_colour = (0, 0, 0)
		self.font = pygame.font.SysFont(None, 48)

		self.label_image = self.font.render(self.text, True, self.text_colour,
											self.colour)
		self.label_image_rect = self.label_image.get_rect()
		self.label_image_rect.center = self.rect.center