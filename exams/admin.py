from django.contrib import admin
from .models import Problem, TestCase, ExamSession, Submission, TestResult


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'time_limit', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'problem', 'is_hidden', 'order']
    list_filter = ['is_hidden', 'problem']
    search_fields = ['name', 'problem__title']
    ordering = ['problem', 'order']


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'problem', 'user', 'start_time', 'is_completed', 'is_submitted']
    list_filter = ['is_completed', 'is_submitted', 'start_time']
    search_fields = ['session_id', 'problem__title']
    ordering = ['-start_time']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'exam_session', 'language', 'status', 'submitted_at']
    list_filter = ['status', 'language', 'submitted_at']
    search_fields = ['exam_session__session_id']
    ordering = ['-submitted_at']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['submission', 'test_case', 'is_passed', 'execution_time']
    list_filter = ['is_passed', 'test_case__problem']
    search_fields = ['submission__id', 'test_case__name']
    ordering = ['submission', 'test_case__order'] 