from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('approve/<int:game_id>/', views.approve_game, name='approve_game'),
    path('reject/<int:game_id>/', views.reject_game, name='reject_game'),  
    path('approved_games/', views.approved_games, name='approved_games'),
    path('rejected_games/', views.rejected_games, name='rejected_games')

]