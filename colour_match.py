import sys
import random

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from block import Block
from button import Button
from instruction_card import InstructionCard

class ColourMatch:
	"""Class to define the game 'Colour Match'"""

	def __init__(self):
		"""Initialise the game and create game resources."""
		pygame.init()

		self.settings = Settings()
		self.stats = GameStats(self)

		self.screen = pygame.display.set_mode((self.settings.screen_width,
											   self.settings.screen_height))
		self.screen_rect = self.screen.get_rect()
		pygame.display.set_caption("Colour Match")

		self.sb = Scoreboard(self)

		# Initialise the variable used to check for new high scores.
		#	Starting place one lower than lowest place that will be recorded.
		#	Score will start at 0.
		self.new_high_score = [self.settings.max_high_scores + 1,
															 self.stats.score]

		# Initialise the grid that holds the blocks during the game.
		self.grid = self._create_grid()

		# Initialise the timer for adding new rows to the pile.
		self.new_row_timer = 0

		# Flag to control setup actions that are only
		# executed once at the start of a new game.
		self.setup_completed = False

		# Initialise a dictionary to hold blocks scheduled for deletion.
		self.scheduled_for_deletion = {}

		# Initialise a buffer to hold the next few blocks the player will get.
		self.buffer = []

		# Initialise dictionary to hold blocks that are 
		# no longer supported by blocks below.
		self.unsupported_blocks = {}

		# Initialise list for storing the rects of all blocks in the pile.
		self.pile_block_rects = []

		# Create all the buttons used to display text in the game.
		self._create_buttons()

		# Create an instruction card for the game.
		self.instruction_card = InstructionCard(self)

	def run_game(self):
		"""Start the main loop for the game."""
		while True:
			self._check_events()

			if (self.settings.game_active 
				and self.settings.difficulty_selected 
				and not self.settings.game_paused):

				# Do this setup section only once when game begins:
				if not self.setup_completed:
					self.settings.set_difficulty()

					# Create an initial pile and buffer of blocks.
					self._create_starting_blocks()
					self._create_buffer_blocks()

					# Start the first block falling to begin the game
					#	and apply its random starting position.
					self.current_block = self.buffer[0]
					self.current_block.rect.x = (self.settings.block_width *
						self.current_block.random_start_position)

					self._update_buffer_blocks()

					self.setup_completed = True

				self._update_current_block()
				self._check_blocks_for_match()
				self._delete_blocks()

				self._apply_grid_positions()
				self._get_pile_block_rects()

				self._check_for_unsupported_blocks()
				self._update_unsupported_blocks()				

				self._check_end_conditions()

				# Check if time to add new row to pile.
				self.new_row_timer += 1
				if self.new_row_timer >= self.settings.new_row_time_limit:
					self._add_new_row()
					self.new_row_timer = 0

			self._update_screen()

	def _check_events(self):
		"""Respond to keypresses and mouse events."""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self._save_high_score()
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				self._check_keydown_events(event)
			elif event.type == pygame.KEYUP:
				self._check_keyup_events(event)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = pygame.mouse.get_pos()
				if (not self.settings.game_active 
				   	and not self.settings.difficulty_selected
				   	and not self.settings.display_instructions
				   	and not self.settings.display_high_scores):
					self._check_title_screen_buttons(mouse_pos)
				elif (not self.settings.game_active 
					  and not self.settings.difficulty_selected 
					  and (self.settings.display_instructions 
					  	   or self.settings.display_high_scores)):
					self._check_close_button(mouse_pos)
				elif (self.settings.game_active 
					  and not self.settings.difficulty_selected):
					self._check_difficulty_buttons(mouse_pos)
				elif self.settings.game_over or self.settings.game_won:
					self._check_replay_button(mouse_pos)
					
	def _check_keydown_events(self, event):
		"""Respond to keypresses."""
		if event.key == pygame.K_RIGHT:
			if (self.current_block.right_hit_box_rect\
				.collidelist(self.pile_block_rects) == -1
				and self.settings.game_active):
				self.current_block.move_block_right()
		elif event.key == pygame.K_LEFT:
			if (self.current_block.left_hit_box_rect\
				.collidelist(self.pile_block_rects) == -1
				and self.settings.game_active):
				self.current_block.move_block_left()
		elif event.key == pygame.K_DOWN:
			self.settings.block_speed *= 2
		elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
			self._save_high_score()
			sys.exit()
		elif event.key == pygame.K_p:
			if (self.settings.game_active
				and self.settings.difficulty_selected):
				self.settings.game_paused = not self.settings.game_paused

	def _check_keyup_events(self, event):
		"""Respond to key releases."""
		if event.key == pygame.K_DOWN:
			self.settings.block_speed /= 2

	def _check_speed_up_criteria(self):
		"""Check if player has scored enough points to speed up game."""
		if self.stats.score > self.settings.points_to_increase_speed:
			self.settings.speed_up_game()
			self.settings.points_to_increase_speed\
							 += self.settings.point_intervals_to_increase_speed

	def _check_end_conditions(self):
		"""Check the "game over" and "game won" conditions for the game."""
		# If all blocks deleted = game won
		if all(value == None for value in self.grid.values()):
			self.settings.game_active = False
			self.settings.game_won = True

		# If a pile block reaches top of screen = game over
		for position, block in self.grid.items():
			if block:
				if position[1] == (self.settings.blocks_per_column - 1):
					self.settings.game_active = False
					self.settings.game_over = True

	# Score methods

	def _update_score(self):
		"""Add to score and update."""
		self.stats.score += 1
		self.sb.prep_score()
		self._check_high_score()
		self._check_speed_up_criteria()

	def _check_high_score(self):
		"""Check to see if there's a new high score."""
		for place, high_score in enumerate(self.stats.high_scores):
			if high_score:
				if self.stats.score > high_score:
					# If score puts player in a higher place 
					# update place and score.
					if (place + 1) < self.new_high_score[0]:
						self.new_high_score = [place + 1, self.stats.score]
					# If score is higher but not in a new place
					# just update score.
					else:
						self.new_high_score[1] = self.stats.score

			# This section needed in case no high score for this place
			# recorded yet.
			else:
				if (place + 1) < self.new_high_score[0]:
					self.new_high_score = [place + 1, self.stats.score]
				else:
					self.new_high_score[1] = self.stats.score

	def _save_high_score(self):
		"""Write high scores to a file when exiting the game."""

		# Update high scores list with the current player high score.
		new_place = self.new_high_score[0]
		new_high_score = self.new_high_score[1]

		# Insert the score at the correct position in list.
		self.stats.high_scores.insert(new_place - 1, new_high_score)
		# Delete the lowest previous high score from end of list.
		del self.stats.high_scores[-1]
		# Prep updated high scores for display.
		self.sb.prep_high_score()

		# Create a list of score strings to write to a file.
		lines = []
		for high_score in self.stats.high_scores:
			high_score_string = str(high_score)
			lines.append(high_score_string)

		filename = 'high_score.txt'
		with open(filename, 'w') as file_object:
			for line in lines:
				file_object.write(line)
				file_object.write("\n")

	# Create + check buttons

	def _create_buttons(self):
		"""Create all the buttons required for displaying text in the game."""

		# Create the title screen for the start of the game.
		self.title = Button(
			self, ["Colour Match"], y_position = 200, button_width = 300)
		self.play_button = Button(
			self, ["Click to Play"], y_position = 400, button_width = 300)
		self.display_instructions = Button(
		   self, ["Display Instructions"], y_position = 500, button_width = 300)
		self.display_high_scores = Button(
			self, ["Display high scores"], y_position = 600, button_width = 300)

		# Create the screen for player to select a difficulty.
		self.select_difficulty = Button(
			self, ["Select Difficulty"], y_position = 200, button_width = 300)
		self.easy_button = Button(
			self, ["Easy"], y_position = 300, button_width = 300)
		self.medium_button = Button(
			self, ["Medium"], y_position = 400, button_width = 300)
		self.hard_button = Button(
			self, ["Hard"], y_position = 500, button_width = 300)

		# Create a button for the 'next blocks' display.
		self.next_blocks = Button(
			self, ["Next Blocks:"], y_position = 1,\
									 x_position = self.screen_rect.right - 200)

		# Create the end game screen for when the game is won or lost.
		self.game_won = Button(
			self, ["You win!"], y_position = 200, button_width = 300)
		self.game_over = Button(
			self, ["Game over"], y_position = 200, button_width = 300)
		self.replay_button = Button(
			self, ["Click to restart"], y_position = 400, button_width = 300)

		# Create a button to display when game is paused.
		self.paused = Button(self, ["Paused"])

		# Create a close button.
		self.close = Button(self, ["Close"], y_position = 600)

	def _check_title_screen_buttons(self, mouse_pos):
		"""Check if the player has clicked a button on the title screen."""
		play_button_clicked = self.play_button.rect.collidepoint(mouse_pos)
		display_instructions_button_clicked = (
						self.display_instructions.rect.collidepoint(mouse_pos))
		display_high_scores_button_clicked = (
						self.display_high_scores.rect.collidepoint(mouse_pos))

		if play_button_clicked and not self.settings.game_active:
			self.settings.game_active = True
		if (display_instructions_button_clicked 
			and not self.settings.game_active):
			self.settings.display_instructions = True
		if display_high_scores_button_clicked and not self.settings.game_active:
			self.settings.display_high_scores = True

	def _check_difficulty_buttons(self, mouse_pos):
		"""Select difficulty for the game."""
		easy_button_clicked = self.easy_button.rect.collidepoint(mouse_pos)
		medium_button_clicked = self.medium_button.rect.collidepoint(mouse_pos)
		hard_button_clicked = self.hard_button.rect.collidepoint(mouse_pos)

		if easy_button_clicked and not self.settings.difficulty_selected:
			self.settings.difficulty = "easy"
			self.settings.difficulty_selected = True
		elif medium_button_clicked and not self.settings.difficulty_selected:
			self.settings.difficulty = "medium"
			self.settings.difficulty_selected = True
		elif hard_button_clicked and not self.settings.difficulty_selected:
			self.settings.difficulty = "hard"
			self.settings.difficulty_selected = True

	def _check_replay_button(self, mouse_pos):
		"""Check if the player has clicked the replay button."""
		replay_button_clicked = self.replay_button.rect.collidepoint(mouse_pos)
		if replay_button_clicked and not self.settings.game_active:
			self._restart_game()

	def _check_close_button(self, mouse_pos):
		"""Check if the player has clicked to close the instructions."""
		close_button_clicked = self.close.rect.collidepoint(mouse_pos)
		if close_button_clicked and self.settings.display_instructions:
			self.settings.display_instructions = False
		if close_button_clicked and self.settings.display_high_scores:
			self.settings.display_high_scores = False

	# Core methods of gameplay:

	def _restart_game(self):
		"""Restart the game after a game over/game won."""
		# Reset all flags to start on difficulty select menu.
		self.settings.game_over = False
		self.settings.game_won = False
		self.settings.game_active = True
		self.settings.difficulty_selected = False

		# Reset game speed to starting speed.
		self.settings.set_initial_speed()

		# Clear all existing blocks from game.
		self.grid.clear()
		self.buffer.clear()
		self.current_block = None

		# Clear the list of pile block rects used for collision detection.
		self.pile_block_rects.clear()

		# Reset the score.
		self.stats.score = 0
		self.sb.prep_score()

		# Reset new row timer.
		self.new_row_timer = 0

		# Reset setup flag so game setup runs correctly.
		self.setup_completed = False

	def _create_grid(self):
		"""Create an empty grid for blocks to be placed into."""
		grid = {}

		for y in range(self.settings.blocks_per_column):
			for x in range(self.settings.blocks_per_row):
				position = (x, y)
				grid[position] = None

		return grid

	def _create_starting_blocks(self):
		"""Create the blocks that are in the pile at the start of the game."""
		for row_number in range(self.settings.starting_rows):
			for block_number in range(self.settings.blocks_per_row):

				# Make sure that no special blocks are in starting pile.
				special_block = True
				while special_block:
					starting_block = Block(self)
					if starting_block.special:
						special_block = True
					else:
						special_block = False

				# Give the starting block its position and add it to the grid.
				starting_block_position = (block_number, row_number)
				self.grid[starting_block_position] = starting_block

				# Make sure there are no pregame matches that will cause gaps
				#	in the starting blocks.
				reduced_colours = self.settings.colour_list.copy()

				try:
					# Find the blocks in the positions below the starting block.
					block_below = self.grid[(starting_block_position[0],
											 starting_block_position[1] - 1)]
					block_2_below = self.grid[(starting_block_position[0],
											   starting_block_position[1] - 2)]

					# If all 3 blocks are a colour match pick a new colour for
					#	starting block.
					if (block_2_below.colour == block_below.colour
						== starting_block.colour):
						# Remove the current colour from the list of colours.
						reduced_colours.remove(starting_block.colour)
						# Select new colour from reduced list and apply colour.
						starting_block.colour = random.choice(reduced_colours)
						starting_block.image.fill(starting_block.colour)

					# This check is required as do not want the second
					# 	horizontal match check to change the colour to one
					# 	that will cause a vertical match that will then be
					# 	missed as this was checked first.
					if (block_2_below.colour == block_below.colour):
						if block_below.colour in reduced_colours:
							reduced_colours.remove(block_below.colour)

				# If block_below and/or block_2_below positions don't exist
				#	move on to the next check.			
				except KeyError:
					pass

				try:
					# Find the blocks in the positions to the left 
					#	of the starting block.
					# 	(check to the left as blocks created from left to right)
					block_left = self.grid[(starting_block_position[0] - 1,
											starting_block_position[1])]
					block_2_left = self.grid[(starting_block_position[0] - 2,
											  starting_block_position[1])]

					# If all 3 blocks are a colour match pick a new colour for
					#	starting block.
					if (block_2_left.colour == block_left.colour
						== starting_block.colour):
						reduced_colours.remove(starting_block.colour)
						starting_block.colour = random.choice(reduced_colours)
						starting_block.image.fill(starting_block.colour)

				# If block_left and/or block_2_left positions don't exist
				#	move on to the next starting block.
				except KeyError:
					pass

	def _create_buffer_blocks(self):
		"""
		Create a buffer of blocks so player can see what blocks will be next.
		"""
		for space in range(self.settings.buffer_size):
			block = Block(self)
			self.buffer.append(block)

	def _update_buffer_blocks(self):
		"""Update the buffer with each new block."""
		del self.buffer[0] # Remove first block that has just been used.
		new_block = Block(self)
		self.buffer.append(new_block) # Add new block to end of buffer.

	def _display_buffer_blocks(self):
		"""Show blocks in buffer at top right of the screen."""
		for number, block in enumerate(self.buffer):
			block.rect.right = self.screen_rect.right
			block.rect.top = (number + 1) * self.settings.block_height
			if block.special:
				block.label_image_rect.center = block.rect.center
			block.draw_block()

	def _apply_grid_positions(self):
		"""
		Give all blocks in the pile a rect position based on their grid 
		position so they can be displayed on screen correctly.
		"""
		for position, block in self.grid.items():
			if block:
				if block not in self.unsupported_blocks.values():
					block.rect.bottom = (self.screen_rect.bottom 
								- (position[1] * self.settings.block_height))
					block.rect.left = (self.screen_rect.left 
								+ (position[0] * self.settings.block_width))
					block.y = block.rect.y

	def _get_pile_block_rects(self):
		"""Create a list of the rects of all blocks currently in the pile."""
		self.pile_block_rects.clear()
		for block in self.grid.values():
			if block:
				self.pile_block_rects.append(block.rect)

	def _update_current_block(self):
		"""Update the currently active block."""
		self.current_block.update()

		# If the current block hits a pile block or the bottom of the screen
		#	then add it to the pile blocks.
		if (self.current_block.bottom_hit_box_rect\
			.collidelist(self.pile_block_rects) != -1
			or self.current_block.rect.bottom >= self.screen_rect.bottom):

			# Assign grid position to current block based on where it landed.
			x_position = (self.current_block.rect.x
						  // self.settings.block_width)
			y_position = ((self.screen_rect.bottom
						 					- self.current_block.rect.centery)
						   // self.settings.block_height)

			# Check if current block is special block and
			#	apply special block effect if so.
			if self.current_block.special:
				if self.current_block.special_type == 1:
					try:
						block_below = self.grid[(x_position, y_position - 1)]
						colour_to_delete = block_below.colour
						self._activate_special_block_1(colour_to_delete)
					# If block below does not exist move on
					# 	without applying effect.
					except KeyError:
						pass
				elif self.current_block.special_type == 2:
					blast_radius = self.current_block.blast_radius
					self._activate_special_block_2(
										x_position, y_position, blast_radius)
			# If current block not a special block then add it to the grid/pile.
			else:
				self.grid[(x_position, y_position)] = self.current_block
			
			# Take new current block from start of the buffer and
			#	apply its random starting position.
			self.current_block = self.buffer[0]
			self.current_block.rect.x = (self.settings.block_width *
									self.current_block.random_start_position)

			# Update the buffer now first block has been used.
			self._update_buffer_blocks()

	def _display_pile_blocks(self):
		"""Display all pile blocks on screen."""
		for position, block in self.grid.items():
			if block:
				block.draw_block()

	def _check_blocks_for_match(self):
		"""
		Check if three of the same colour block are lined up
		either vertically or horizontally.
		"""
		for position, block in self.grid.items():

			# Only run check on this position if there is a block in it.
			if not block:
				continue

			# Get the x and y coordinates of the current block
			x_position = position[0]
			y_position = position[1]

			# Try to find a vertical match for the current block.
			try:
				block_below = self.grid[(x_position, y_position - 1)]
				block_2_below = self.grid[(x_position, y_position - 2)]
				if block_below and block_2_below:
					if (block.colour == block_below.colour
						== block_2_below.colour):
						self._find_adjacent_blocks(position)
			# If block_below or block_2_below positions don't exist, 
			# 	move on to check for horizontal match. 
			except KeyError:
				pass

			# Try to find a horizonal match for the current block.
			#	Only need to check matches to right as matches to left will
			#	be caught from previous rightward checks.
			try:
				block_right = self.grid[(x_position + 1, y_position)]
				block_2_right = self.grid[(x_position + 2, y_position)]
				if block_right and block_2_right:
					if (block.colour == block_right.colour
						== block_2_right.colour):
						self._find_adjacent_blocks(position)
			# If block_right or block_2_right positions don't exist, 
			# 	move on to check next block. 
			except KeyError:
				pass

	def _find_adjacent_blocks(self, position):
		"""
		After finding 3 blocks that match - call this method to find all
		other blocks of the same colour adjacent to the matching blocks and
		schedule all for deletion.
		"""	
		x = position[0]
		y = position[1]

		starting_block = self.grid[position]
		self.scheduled_for_deletion[position] = starting_block
		match_colour = starting_block.colour

		# Find all the positions adjacent blocks can be at.
		adjacent_block_positions = [(x + 1, y), (x - 1, y), (x, y + 1),
									(x, y - 1)]

		# Check all adjacent positions for matching blocks.
		for adjacent_position in adjacent_block_positions:
			# If that position exists...
			if adjacent_position in self.grid.keys():
				adjacent_block = self.grid[adjacent_position]
				# If there is a block in this position...
				if adjacent_block:
					# Do not recheck blocks already scheduled for deletion.
					if (adjacent_block
						not in self.scheduled_for_deletion.values()):
						# If the block is the matching colour then start
						#	checking process again with this new matching
						#	block as the starting block - this continues in
						#	recursive loop until all adjacent matching blocks
						# 	have been checked and added to delete dict.
						if adjacent_block.colour == match_colour:
							self._find_adjacent_blocks(adjacent_position)

	def _delete_blocks(self):
		"""Delete all blocks in "scheduled for deletion" from the main grid."""
		for position, block in self.scheduled_for_deletion.items():
			if block in self.grid.values():
				self.grid[position] = None
				self._update_score()
		self.scheduled_for_deletion.clear()

	def _check_for_unsupported_blocks(self):
		"""Find blocks that have no block below supporting them."""
		for position, block in self.grid.items():
			x = position[0]
			y = position[1]
			position_below = (x, y - 1)
			if block:
				if position_below in self.grid.keys():
					if not self.grid[position_below]:
						self.unsupported_blocks[position] = block

	def _update_unsupported_blocks(self):
		"""
		Make unsupported blocks fall until they hit another block
		or bottom of the screen.
		"""
		for position, block in self.unsupported_blocks.copy().items():

			# Need this section to stop block from "interacting with itself"
			reduced_pile_block_rects = self.pile_block_rects.copy()
			if block.rect in reduced_pile_block_rects:
				reduced_pile_block_rects.remove(block.rect)

			if (block.rect.bottom < self.screen_rect.bottom 
				and block.rect.collidelist(reduced_pile_block_rects) == -1):
				# While block is unsupported update its vertical position.
				block.update()
			else:
				# Remove block from unsupported dict as no longer unsupported.
				del self.unsupported_blocks[position]
				# Block has now fallen out of original position so = None.
				self.grid[position] = None
				# x position doesn't change.
				new_x_position = position[0]
				# New y position calculated based on where block fell to.
				new_y_position = ((self.screen_rect.bottom - block.rect.centery)
								   // self.settings.block_height)
				# Add block back into grid at its new position.
				self.grid[(new_x_position, new_y_position)] = block

	def _add_new_row(self):
		"""Move all blocks up and add a new row below."""
		# Move all existing blocks up 1 space.
		new_grid = self._create_grid()
		for position, block in self.grid.items():
			new_x_position = position[0] # x position stays the same.
			new_y_position = position[1] + 1 # y position moves up 1.
			new_grid[(new_x_position, new_y_position)] = block
		
		# Overwrite old grid with the new grid positions.
		self.grid = new_grid

		# Add a new row in the space now created at bottom of the screen.
		for space in range(self.settings.blocks_per_row):
			
			# Make sure that no special blocks are put into the pile.
			special_block = True
			while special_block:
				new_block = Block(self)
				if new_block.special:
					special_block = True
				else:
					special_block = False

			# Check block colour and change before adding it to pile
			#	if it will cause colour matches.
			#	Similar process as _create_starting_blocks()
			#	see there for annotations.
			#	(One uses blocks below, one uses blocks above due to order
			#	blocks are created in both cases)

			reduced_colours = self.settings.colour_list.copy()
			
			try:
				block_above = self.grid[(space, 1)]
				block_2_above = self.grid[(space, 2)]

				# Check if the spaces above contain blocks first.
				if block_above and block_2_above:
					if (block_2_above.colour == block_above.colour
						== new_block.colour):
						reduced_colours.remove(new_block.colour)
						new_block.colour = random.choice(reduced_colours)
						new_block.image.fill(new_block.colour)
					if (block_2_above.colour == block_above.colour):
						if block_above.colour in reduced_colours:
							reduced_colours.remove(block_above.colour)
			except KeyError:
				pass

			try:
				block_left = self.grid[(space - 1, 0)]
				block_2_left = self.grid[(space - 2, 0)]
				if block_left and block_2_left:
					if (block_2_left.colour == block_left.colour
						== new_block.colour):
						reduced_colours.remove(new_block.colour)
						new_block.colour = random.choice(reduced_colours)
						new_block.image.fill(new_block.colour)
			except KeyError:
				pass

			# Add the new block to the grid in the correct position.
			position_x = space
			position_y = 0 # Always at bottom of the screen (first row).
			self.grid[(position_x, position_y)] = new_block

			# Give the new blocks rect the correct position so block
			#	can be displayed on screen.
			new_block.rect.bottom = self.screen_rect.bottom
			new_block.rect.left = (self.screen_rect.left +
										(space * self.settings.block_width))
			
	def _activate_special_block_1(self, colour_to_delete):
		"""
		Remove all blocks the same colour as the block
		the special block lands on.
		"""
		for position, block in self.grid.items():
			if block:
				if block.colour == colour_to_delete:
					self.grid[position] = None
					self._update_score()

	def _activate_special_block_2(self, x_position, y_position, blast_radius):
		"""Remove all blocks within the special block's 'blast radius'."""
		# Calculate the list of positions in blast_radius.
		blast_radius_positions = []

		for x in range((x_position - blast_radius),
											(x_position + blast_radius + 1)):
			for y in range((y_position - blast_radius),
											(y_position + blast_radius + 1)):
				position = (x, y)
				blast_radius_positions.append(position)
		# Remove position special block lands from the blast radius positions.
		blast_radius_positions.remove((x_position, y_position))

		# Check for blocks in blast radius and delete them.
		for position, block in self.grid.items():
			if position in blast_radius_positions:
				if block:
					self.grid[position] = None
					self._update_score()

	# Update the screen at the end of all calculations.

	def _update_screen(self):
		"""Update images on the screen and flip to the new screen."""
		# Give screen a background colour.
		self.screen.fill(self.settings.background_colour)

		# Draw all the blocks to the screen.
		self._display_pile_blocks()
		self._display_buffer_blocks()
		if self.setup_completed:
			self.current_block.draw_block()

		# Draw the score information.
		self.sb.show_score()

		# Draw the text buttons on screen when required.
		if (not self.settings.game_active
		 	and not self.settings.difficulty_selected
		   	and not self.settings.display_instructions
		   	and not self.settings.display_high_scores):
			self.title.draw_button()
			self.play_button.draw_button()
			self.display_instructions.draw_button()
			self.display_high_scores.draw_button()
		elif (self.settings.game_active
			  and not self.settings.difficulty_selected):
			self.select_difficulty.draw_button()
			self.easy_button.draw_button()
			self.medium_button.draw_button()
			self.hard_button.draw_button()
		elif self.settings.game_active and self.settings.difficulty_selected:
			self.next_blocks.draw_button()

		if self.settings.display_instructions:
			self.instruction_card.display_instructions()
			self.close.draw_button()

		if self.settings.display_high_scores:
			self.sb.show_high_score()
			self.close.draw_button()

		if self.settings.game_over:
			self.game_over.draw_button()
			self.replay_button.draw_button()

		if self.settings.game_won:
			self.game_won.draw_button()
			self.replay_button.draw_button()

		if self.settings.game_paused:
			self.paused.draw_button()

		# Display the updated screen.
		pygame.display.flip()


if __name__ == '__main__':
	# Make a game instance and run the game.
	cm = ColourMatch()
	cm.run_game()