from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    steam_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0)
    image = models.URLField()

    def __str__(self):
        return self.name

class Achievement(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    api_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    rarity_percent = models.FloatField(default=0.0)
    difficulty_score = models.FloatField(default=0.0)

    def calculate_difficulty(self):
        # логика - чем меньше процент игроков (конкретно rarity_percent), тем выше сложность (0-10)
        # если ачивку получили 0.1% игроков — это 10/10 сложность
        # если 100% — то это 0/10
        if self.rarity_percent == 0:
            return 10.0
        score = 10 - (self.rarity_percent / 10)
        return round(max(0, min(10, score)), 2)

    def __str__(self):
        return f"{self.game.name} | {self.display_name} ({self.difficulty_score})"

class PriceHistory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.query}"