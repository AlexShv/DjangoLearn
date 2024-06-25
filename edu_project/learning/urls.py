from django.urls import path
from .views import *


urlpatterns = [
    path('', main, name='main_page'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('profile/<str:username>', profile, name='profile'),
    path('course/<int:course_id>', course_detail, name='course_detail'),
    path('catalog/<str:category>', courses_catalog, name='courses_catalog'),
]
