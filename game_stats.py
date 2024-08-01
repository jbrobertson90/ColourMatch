class GameStats:
	"""Track statistics for Colour Match."""

	def __init__(self, cm_game):
		"""Initialise statistics."""
		self.settings = cm_game.settings
		self.score = 0

		self.high_scores = []
		# Read the high score from file or set to None if no high scores found.
		try:
			with open('high_score.txt') as file_object:
				for line in file_object:
					try:
						line = line.rstrip()
						line = int(line)
						self.high_scores.append(line)
					except ValueError:
						self.high_scores.append(None)
		except FileNotFoundError:
			self.high_scores = [None] * self.settings.max_high_scores

		# Check that correct amount of values stored for high scores.
		while len(self.high_scores) < self.settings.max_high_scores:
			self.high_scores.append(None)
		while len(self.high_scores) > self.settings.max_high_scores:
			del self.high_scores[-1]