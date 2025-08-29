from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'problems', views.ProblemViewSet)
router.register(r'sessions', views.ExamSessionViewSet)
router.register(r'submissions', views.SubmissionViewSet)
router.register(r'contests', views.ContestViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'discussions', views.DiscussionViewSet)

# API URLs
urlpatterns = [
    path('', include(router.urls)),
    path('execute/', views.CodeExecutionView.as_view(), name='code_execute'),
    # Contest-specific endpoints
    path('contests/<int:contest_id>/register/', views.ContestViewSet.as_view({'post': 'register'}), name='contest_register'),
    path('contests/<int:contest_id>/leaderboard/', views.ContestViewSet.as_view({'get': 'leaderboard'}), name='contest_leaderboard'),
    path('contests/<int:contest_id>/problems/', views.ContestViewSet.as_view({'get': 'problems'}), name='contest_problems'),
    # User profile endpoints
    path('profiles/<int:profile_id>/submissions/', views.UserProfileViewSet.as_view({'get': 'submissions'}), name='user_submissions'),
    # Discussion endpoints
    path('discussions/<int:discussion_id>/replies/', views.DiscussionViewSet.as_view({'get': 'list', 'post': 'create'}), name='discussion_replies'),
] 