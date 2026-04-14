from django.contrib import admin
from .models import Game, Achievement, PriceHistory, SearchHistory

admin.site.register(Game)
admin.site.register(Achievement)
admin.site.register(PriceHistory)
admin.site.register(SearchHistory)