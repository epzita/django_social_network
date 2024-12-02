from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views 

urlpatterns = [
    path("", views.index, name = "index"),
    path("all/", views.index_all, name = "index_all"),
    path("register/", views.register, name = "register"),
    path('login/',views.login_user, name='login'),
    path('user/<slug:username>/games', views.user_page_games, name = 'user_games'),
    path('user/<slug:username>/followers', views.user_page_followers, name = 'user_followers'),
    path('user/<slug:username>', views.user_page_posts, name = 'user_posts'),
    path('game/<game_name>', views.game_page, name = 'game_page'),
    path('logout/', views.logout_user, name = 'logout'),
    path('debug/', views.index_debug, name = 'debug'),
    path('game_index/', views.game_index, name = 'game_index'),
    path('user_index/', views.user_index, name = 'user_index'),
    path('toggle_follow/game/<game_name>', views.follow_game, name = 'follow_game'),
    path('toggle_follow/user/<slug:username>', views.follow_user, name = 'follow_user'),
    path('toggle_like/<post_id>', views.like_post, name = 'liked_post'),
    path('settings/', views.settings, name = 'settings'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
