class Settings:
	"""Class to hold the settings for the Colour Match game."""

	def __init__(self):
		"""Initialise the settings for the game."""
		# Screen settings.
		self.screen_width = 700
		self.screen_height = 700
		self.background_colour = (0, 0, 0)

		# Block settings.
		self.block_width = 50
		self.block_height = 50

		# Block colours.
		self.RED = (255, 0, 0)
		self.GREEN = (0, 255, 0)
		self.BLUE = (0, 0, 255)
		self.YELLOW = (255, 255, 0)
		self.ORANGE = (255, 150, 0)
		
		# Game settings.
		self.starting_rows = 3
		self.blocks_per_row = (self.screen_width //	self.block_width)
		self.blocks_per_column = (self.screen_height // self.block_height)

		# Game will speed up each time the player scores this many points.
		self.point_intervals_to_increase_speed = 50

		# Define the max number of high score places that will be recorded.
		self.max_high_scores = 5

		# Define how many blocks ahead the player will be able to see.
		self.buffer_size = 5

		# Flags for controlling flow of the game.
		self.game_active = False
		self.display_instructions = False
		self.display_high_scores = False
		self.difficulty_selected = False
		self.game_over = False
		self.game_won = False
		self.game_paused = False

		# Initialise difficulty variables before these are selected by player.
		self.difficulty = ""
		self.colour_list = []

		# Set the initial values for speed variables that will 
		#	increase throughout the game.
		self.set_initial_speed()

	def set_initial_speed(self):
		"""Start the game at the initial speed values."""
		self.block_speed = 0.4
		self.new_row_time_limit = 50000
		self.points_to_increase_speed = 50

	def set_difficulty(self):
		"""Set the difficulty level (number of colours) after player selects."""
		if self.difficulty == "easy":
			self.colour_list = [self.RED, self.GREEN, self.BLUE]
		elif self.difficulty == "medium":
			self.colour_list = [self.RED, self.GREEN, self.BLUE, self.YELLOW]
		elif self.difficulty == "hard":
			self.colour_list = [self.RED, self.GREEN, self.BLUE, 
								self.YELLOW, self.ORANGE]

	def speed_up_game(self):
		"""Speed up the game as it progresses."""
		# Speed up game by 10% each time.
		self.block_speed *= 1.1
		self.new_row_time_limit /= 1.1