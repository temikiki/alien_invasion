class GameStats:
    """track statistics for Alien Invasion"""

    def __init__(self, ai_game):
        """Initialize statistics."""

        self.settings = ai_game.settings
        self.reset_stats()
        # high score never be reset
        self.high_score = 0
        self.level = 1

    def reset_stats(self):
        """Intial statistics that can change during the game"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
