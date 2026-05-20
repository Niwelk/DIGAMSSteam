from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    path('game/<int:game_id>/achievements/', views.get_achievements, name='achievements'),
    path('game/<int:game_id>/ai/', views.ai_analysis, name='ai_analysis'),
]