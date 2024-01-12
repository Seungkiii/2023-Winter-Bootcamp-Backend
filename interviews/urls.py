from django.urls import path
#from .views import QuestionView
from .views import InterviewList

urlpatterns = [
    #path('<int:id>/questions/', QuestionView.as_view(), name='question-view'),

    path('', InterviewList.as_view(), name='interview-list'),
       
]


# from django.urls import path
# from .views import InterviewViewSet

# interview_list = InterviewViewSet.as_view({'get': 'list', 'post': 'create'})

# urlpatterns = [
#     path('', interview_list, name='interview-list'),
# ]
