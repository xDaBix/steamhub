from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='developer_home'),
    path('signup/', views.signup, name='developer_signup'),
    path('login/', views.login, name='developer_login'),
    path('verifyotp/', views.verify_otp, name='developer_verifyotp'),
    path('profile/', views.userprofile, name='developer_profile'),  
    path('logout/', views.logout_view, name='developer_logout'),  
    path('forgotpassword/', views.forgotpassword, name='developer_forgotpassword'),
    path('forgototp/', views.forgototp, name='developer_forgototp'),
    path('check-developer/', views.check_user_exists, name='developer_check_user_exists'),
    path('resetpassword/', views.resetpassword, name='developer_resetpassword'),
    path('upload/', views.upload_game, name='developer_upload_game'),  
     path('game/delete/<int:game_id>/', views.delete_game, name='developer_delete_game'),
    path('gamelist/', views.game_list, name='developer_game_list'),  

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
