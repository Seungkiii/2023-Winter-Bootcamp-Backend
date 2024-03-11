from django.urls import path
from . import views
from .views import UserView, LogoutView, GithubCallbackView, UserStatusView

urlpatterns = [
    path('', UserView.as_view(), name='user-view'),
    path('status/', UserStatusView.as_view(), name='user-status-view'),
    path('logout/', LogoutView.as_view(), name='logout-view'),
    path('github/callback/', GithubCallbackView.as_view(), name='github-callback-view'),
]
