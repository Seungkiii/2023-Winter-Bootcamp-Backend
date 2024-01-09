from django.urls import path
from . import views
from .views import ResumeList, ResumeCreate, ResumeDelete

urlpatterns = [
    path('', ResumeList.as_view(), name='resume-list'),
    path('create', views.ResumeCreate.as_view(), name='resume-create'),
    path('delete/<int:id>', ResumeDelete.as_view(), name='resume-delete'),
]
