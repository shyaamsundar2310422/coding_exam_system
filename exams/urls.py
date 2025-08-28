from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'problems', views.ProblemViewSet)
router.register(r'sessions', views.ExamSessionViewSet)
router.register(r'submissions', views.SubmissionViewSet)

# API URLs
urlpatterns = [
    path('', include(router.urls)),
    path('execute/', views.CodeExecutionView.as_view(), name='code_execute'),
    # Add explicit submit endpoint for better debugging
    path('sessions/<str:session_id>/submit/', views.ExamSessionViewSet.as_view({'post': 'submit'}), name='submit_code'),
] 