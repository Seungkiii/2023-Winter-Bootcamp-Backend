from django.urls import path
from . import views

urlpatterns = [
    path('github/callback/', views.github_callback, name='github-callback'),
    path('logout/', views.logout_view, name='logout'),
]
