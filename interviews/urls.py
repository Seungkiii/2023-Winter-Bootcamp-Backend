from django.urls import path
#from .views import QuestionView
from .views import InterviewList, InterviewDetail

urlpatterns = [
    #path('<int:id>/questions/', QuestionView.as_view(), name='question-view'),

    path('', InterviewList.as_view(), name='interview-list'),
    path('<int:id>', InterviewDetail.as_view(), name='interview-detail')
]
