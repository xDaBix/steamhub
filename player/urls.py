from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('verifyotp/', views.verify_otp, name='verifyotp'),
    path('profile/', views.userprofile, name='userprofile'),  
    path('logout/', views.logout_view, name='logout'),  
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('forgototp/', views.forgototp, name='forgototp'),
    path('check-user/', views.check_user_exists, name='check_user_exists'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),
    path('games/', views.game_list, name='game_list'),
    path('payment/create/<int:game_id>/', views.create_payment, name='create_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('library/', views.library, name='library'),
    path('payment_page/<int:game_id>/', views.payment_page, name='payment_page'),
    path('download/<int:game_id>/', views.download_game, name='download_game'),
     path('send_friend_request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<str:username>/', views.reject_friend_request, name='reject_friend_request'),
     path('friends/', views.friends_list, name='friends_list'),
      
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)