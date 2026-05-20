from django.test import TestCase
from games.models import Game, Achievement

class AchievementDifficultyTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            steam_id=12345,
            name="Test Strategy Game",
            price=499.0,
            image="http://example.com/image.jpg"
        )

    def test_calculate_difficulty_rare(self):
        "Тест: Если ачивку получили 0.1% игроков, сложность должна стремиться к 10"
        achievement = Achievement.objects.create(
            game=self.game,
            api_name="ACH_HARDCORE",
            display_name="Hardcore Winner",
            rarity_percent=0.1
        )

        difficulty = achievement.calculate_difficulty()
        self.assertAlmostEqual(difficulty, 9.99, places=2)

    def test_calculate_difficulty_popular(self):
        """Тест: Если ачивку получили 100% игроков, сложность должна быть 0"""
        achievement = Achievement.objects.create(
            game=self.game,
            api_name="ACH_WELCOME",
            display_name="Welcome to Game",
            rarity_percent=100.0
        )
        difficulty = achievement.calculate_difficulty()
        self.assertEqual(difficulty, 0.0)