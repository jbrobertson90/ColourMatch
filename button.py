import pygame.freetype

class Button:
	"""Class to create buttons for displaying in game text and options."""

	def __init__(self, cm_game, msg = [], font_size = 30, x_position = None,
				 y_position = None, button_width = 200, button_height = 50):
		"""Initialise button attributes."""
		self.screen = cm_game.screen
		self.screen_rect = self.screen.get_rect()

		# Set the dimensions and properties of the button.
		self.width, self.height = button_width, button_height
		self.button_colour = (255, 255, 255)
		self.text_colour = (0, 0, 0)
		self.font = pygame.freetype.SysFont(None, font_size)

		# Build the buttons rect object and centre it as default option or
		# 	position on screen at coordinates provided.
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.center = self.screen_rect.center
		if x_position:
			self.rect.x = x_position
		if y_position:
			self.rect.y = y_position

		# Prepare the message to be displayed on the button.
		self.prep_msg(msg)

	def prep_msg(self, msg):
		"""Turn msg into a rendered image and centre text on the button."""
		# Freetype Render returns a tuple in the form: (Surface/Image, Rect)
		#	Make a list to store these for each line of text.
		self.msg_tuples = []
		for line_number, line in enumerate(msg):
			current_line = self.font.render(line, self.text_colour,
											self.button_colour)
			current_line[1].center = self.rect.center
			current_line[1].top = self.rect.top + 5 + (20 * line_number)
			self.msg_tuples.append(current_line)

	def draw_button(self):
		# Draw blank button and then draw message.
		self.screen.fill(self.button_colour, self.rect)
		for line in self.msg_tuples:
			self.screen.blit(line[0], line[1])