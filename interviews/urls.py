from django.urls import path
from .views import QuestionView, AnswerCreateView

urlpatterns = [
    path('<int:id>/questions/', QuestionView.as_view(), name='question-view'),
    path('questions/<int:id>/answers/create/', AnswerCreateView.as_view(), name='answer-create'),

]
