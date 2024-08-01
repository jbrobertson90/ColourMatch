from button import Button

class InstructionCard:
	"""
	Class that contains and displays instructions for how to play Colour Match.
	"""

	def __init__(self, cm_game):
		"""Set up the instruction card."""

		self.title_text = ["Colour Match"]

		self.how_to_play_text = [
		"Match 3 blocks of the same colour vertically or horizonally to remove",
		"all adjacent blocks of the same colour.",
		"Win by clearing all blocks before they reach the top of the screen."]

		self.controls_text = [
		"Controls:",
		"Use left/right arrow keys to move block, " + 
			"down arrow to speed up block.",
		"Mouse click on buttons to select options.",
		"Press p to pause/unpause game.",
		"Press q or Esc to exit game."]

		self.difficulty_text = [
		"Select Difficulty:",
		"Easy = 3 colours",
		"Medium = 4 colours",
		"Hard = 5 colours"]

		self.special_blocks_text = [
		"Special Blocks:",
		"1) Number blocks remove all blocks within the radius of that number.",
		"2) 'D' blocks Delete all blocks of the same colour as the block" +
			" they land on."]

		self.title = Button(
			cm_game, self.title_text, y_position = 75, button_width = 300)

		self.how_to_play = Button(
			cm_game, self.how_to_play_text, font_size = 15, y_position = 175,
			button_width = 600, button_height = 70)

		self.controls = Button(
			cm_game, self.controls_text, font_size = 15, y_position = 260,
			button_width = 600, button_height = 100)

		self.difficulty = Button(
			cm_game, self.difficulty_text, font_size = 15, y_position = 375,
			button_width = 600, button_height = 80)

		self.special_blocks = Button(
			cm_game, self.special_blocks_text, font_size = 15, y_position = 475,
			button_width = 600, button_height = 75)

	def display_instructions(self):
		"""Show the instructions to the player."""
		self.title.draw_button()
		self.how_to_play.draw_button()
		self.difficulty.draw_button()
		self.special_blocks.draw_button()
		self.controls.draw_button()