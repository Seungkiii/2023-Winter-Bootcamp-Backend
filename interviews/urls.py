from django.urls import path
from .views import QuestionView

urlpatterns = [
    path('<int:id>/questions/', QuestionView.as_view(), name='question-view'),
]
