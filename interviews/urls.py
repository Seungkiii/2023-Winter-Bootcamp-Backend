from django.urls import path
#from .views import QuestionView
from .views import InterviewList

urlpatterns = [
    #path('<int:id>/questions/', QuestionView.as_view(), name='question-view'),

    path('', InterviewList.as_view(), name='interview-list'),
   
    
]
