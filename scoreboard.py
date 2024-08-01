import pygame.font

class Scoreboard:
	"""A class to report scoring information."""

	def __init__(self, cm_game):
		"""Initialise scorekeeping attributes."""
		self.screen = cm_game.screen
		self.screen_rect = self.screen.get_rect()
		self.settings = cm_game.settings
		self.stats = cm_game.stats

		# Font settings for scoring information.
		self.text_colour = (255, 255, 255)
		self.font = pygame.font.SysFont(None, 48)

		# Prepare the scores as rendered images to be displayed.
		self.prep_score()
		self.prep_high_score()

	def prep_score(self):
		"""Turn the score into a rendered image."""
		score_str = str(self.stats.score)
		self.score_image = self.font.render(score_str, True, self.text_colour,
											self.settings.background_colour)

		# Display the score at the top left of the screen.
		self.score_rect = self.score_image.get_rect()
		self.score_rect.left = 20
		self.score_rect.top = 20

	def prep_high_score(self):
		"""Turn the high scores into rendered images."""
		self.high_score_images = []
		self.high_score_rects = []
		for place, high_score in enumerate(self.stats.high_scores):
			# Find the correct suffix for the place number.
			#	(Count starts at 0 but places start at 1st)
			if place + 1 == 1:
				suffix = "st"
			elif place + 1 == 2:
				suffix = "nd"
			elif place + 1 == 3:
				suffix = "rd"
			else:
				suffix = "th"

			# Create an image for the high score and store it in image list.
			high_score_str = str(place+1) + suffix + ": " + str(high_score)
			self.high_score_image = self.font.render(high_score_str, True,
							self.text_colour, self.settings.background_colour)
			self.high_score_images.append(self.high_score_image)

			# Get the rect for the high score, position it on screen to
			# 	be displayed, then store in rect list.
			self.high_score_rect = self.high_score_image.get_rect()
			self.high_score_rect.centerx = self.screen_rect.centerx
			self.high_score_rect.y = 200 + (place * 50)
			self.high_score_rects.append(self.high_score_rect)

	def show_score(self):
		"""Draw score to the screen."""
		self.screen.blit(self.score_image, self.score_rect)

	def show_high_score(self):
		"""Draw high scores to the screen."""
		for place, high_score in enumerate(self.stats.high_scores):
			self.screen.blit(self.high_score_images[place],
							 self.high_score_rects[place])