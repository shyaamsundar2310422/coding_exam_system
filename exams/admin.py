from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Problem, TestCase, ExamSession, Submission, TestResult,
    UserProfile, Contest, ContestParticipant, ProblemCategory,
    Leaderboard, Discussion, DiscussionReply
)


@admin.register(ProblemCategory)
class ProblemCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'points', 'problems_count']
    list_filter = ['points']
    search_fields = ['name', 'description']
    
    def problems_count(self, obj):
        return obj.problems.count()
    problems_count.short_description = 'Problems Count'


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty_score', 'points', 'contest', 'is_active', 'is_featured', 'acceptance_rate']
    list_filter = ['category', 'difficulty_score', 'is_active', 'is_featured', 'contest']
    search_fields = ['title', 'description', 'problem_statement']
    ordering = ['difficulty_score', 'created_at']
    readonly_fields = ['total_submissions', 'successful_submissions', 'acceptance_rate']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'contest', 'created_by')
        }),
        ('Problem Details', {
            'fields': ('problem_statement', 'input_format', 'output_format', 'constraints')
        }),
        ('Code & Examples', {
            'fields': ('initial_code', 'solution_code', 'sample_input', 'sample_output', 'explanation')
        }),
        ('Settings', {
            'fields': ('time_limit', 'memory_limit', 'difficulty_score', 'points', 'is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('total_submissions', 'successful_submissions', 'acceptance_rate'),
            'classes': ('collapse',)
        })
    )


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'problem', 'is_hidden', 'is_sample', 'order', 'points']
    list_filter = ['is_hidden', 'is_sample', 'problem__category', 'problem']
    search_fields = ['name', 'problem__title']
    ordering = ['problem', 'order']


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ['title', 'contest_type', 'status', 'start_time', 'end_time', 'duration', 'participants_count', 'max_participants']
    list_filter = ['contest_type', 'status', 'is_public', 'registration_required']
    search_fields = ['title', 'description']
    ordering = ['-start_time']
    readonly_fields = ['current_participants']
    
    def participants_count(self, obj):
        return obj.participants.filter(is_active=True).count()
    participants_count.short_description = 'Participants'


@admin.register(ContestParticipant)
class ContestParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'contest', 'score', 'rank', 'joined_at', 'is_active']
    list_filter = ['contest', 'is_active', 'joined_at']
    search_fields = ['user__username', 'contest__title']
    ordering = ['contest', '-score']


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'problem', 'contest', 'start_time', 'is_completed', 'is_submitted', 'score']
    list_filter = ['is_completed', 'is_submitted', 'start_time', 'contest']
    search_fields = ['session_id', 'problem__title', 'user__username']
    ordering = ['-start_time']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'problem', 'contest', 'language', 'status', 'score', 'submitted_at']
    list_filter = ['status', 'language', 'submitted_at', 'contest']
    search_fields = ['user__username', 'problem__title', 'code']
    ordering = ['-submitted_at']
    readonly_fields = ['execution_time', 'memory_used', 'score', 'points_earned']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['submission', 'test_case', 'is_passed', 'execution_time', 'points_earned']
    list_filter = ['is_passed', 'test_case__problem__category']
    search_fields = ['submission__id', 'test_case__name']
    ordering = ['submission', 'test_case__order']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'rank', 'problems_solved', 'contests_participated', 'total_submissions']
    list_filter = ['rank', 'created_at']
    search_fields = ['user__username', 'user__email']
    ordering = ['-rating']
    readonly_fields = ['total_submissions', 'problems_solved', 'contests_participated']


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['contest', 'user', 'total_score', 'problems_solved', 'rank', 'last_submission']
    list_filter = ['contest', 'rank']
    search_fields = ['user__username', 'contest__title']
    ordering = ['contest', 'rank']


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'problem', 'is_resolved', 'replies_count', 'created_at']
    list_filter = ['is_resolved', 'created_at', 'problem__category']
    search_fields = ['title', 'content', 'user__username', 'problem__title']
    ordering = ['-created_at']
    readonly_fields = ['replies_count']
    
    def replies_count(self, obj):
        return obj.replies.count()
    replies_count.short_description = 'Replies'


@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ['discussion', 'user', 'is_solution', 'created_at']
    list_filter = ['is_solution', 'created_at']
    search_fields = ['content', 'user__username', 'discussion__title']
    ordering = ['discussion', 'created_at']


# Custom admin site configuration
admin.site.site_header = "HackerRank-Style Coding Platform Admin"
admin.site.site_title = "Coding Platform Admin"
admin.site.index_title = "Welcome to the Coding Platform Administration" 