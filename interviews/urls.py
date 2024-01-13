from django.urls import path
from .views import InterviewCreateView

urlpatterns = [
    path('create/', InterviewCreateView.as_view(), name='create_interview'),
    # 다른 필요한 URL 패턴들을 추가할 수 있습니다.
]