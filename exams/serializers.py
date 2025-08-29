from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Problem, TestCase, ExamSession, Submission, TestResult,
    UserProfile, Contest, ContestParticipant, ProblemCategory,
    Leaderboard, Discussion, DiscussionReply
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'username', 'bio', 'avatar', 'rating', 'rank',
            'total_submissions', 'problems_solved', 'contests_participated',
            'created_at'
        ]


class ProblemCategorySerializer(serializers.ModelSerializer):
    """Serializer for ProblemCategory model"""
    class Meta:
        model = ProblemCategory
        fields = ['id', 'name', 'color', 'points', 'description']


class TestCaseSerializer(serializers.ModelSerializer):
    """Serializer for TestCase model"""
    class Meta:
        model = TestCase
        fields = ['id', 'name', 'input_data', 'expected_output', 'is_hidden', 'is_sample', 'order', 'points']


class ProblemSerializer(serializers.ModelSerializer):
    """Enhanced serializer for Problem model"""
    test_cases = TestCaseSerializer(many=True, read_only=True)
    category = ProblemCategorySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Problem
        fields = [
            'id', 'title', 'description', 'problem_statement', 'input_format', 'output_format',
            'constraints', 'sample_input', 'sample_output', 'explanation', 'initial_code',
            'solution_code', 'time_limit', 'memory_limit', 'category', 'contest',
            'difficulty_score', 'points', 'is_active', 'is_featured', 'created_by',
            'total_submissions', 'successful_submissions', 'acceptance_rate',
            'created_at', 'updated_at'
        ]


class ContestSerializer(serializers.ModelSerializer):
    """Serializer for Contest model"""
    created_by = UserSerializer(read_only=True)
    current_participants_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contest_type_display = serializers.CharField(source='get_contest_type_display', read_only=True)
    
    class Meta:
        model = Contest
        fields = [
            'id', 'title', 'description', 'start_time', 'end_time', 'duration',
            'max_participants', 'current_participants', 'current_participants_count',
            'status', 'status_display', 'contest_type', 'contest_type_display',
            'is_public', 'registration_required', 'created_by', 'created_at', 'updated_at'
        ]
    
    def get_current_participants_count(self, obj):
        return obj.participants.filter(is_active=True).count()


class ContestParticipantSerializer(serializers.ModelSerializer):
    """Serializer for ContestParticipant model"""
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ContestParticipant
        fields = ['id', 'contest', 'user', 'username', 'joined_at', 'score', 'rank', 'is_active']


class ExamSessionSerializer(serializers.ModelSerializer):
    """Enhanced serializer for ExamSession model"""
    problem = ProblemSerializer(read_only=True)
    contest = ContestSerializer(read_only=True)
    problem_id = serializers.IntegerField(write_only=True)
    contest_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ExamSession
        fields = [
            'id', 'session_id', 'problem', 'contest', 'problem_id', 'contest_id',
            'start_time', 'end_time', 'time_remaining', 'time_spent',
            'is_completed', 'is_submitted', 'score'
        ]
        read_only_fields = ['id', 'session_id', 'start_time', 'end_time', 'is_completed', 'is_submitted', 'score']


class TestResultSerializer(serializers.ModelSerializer):
    """Enhanced serializer for TestResult model"""
    test_case_name = serializers.CharField(source='test_case.name', read_only=True)
    
    class Meta:
        model = TestResult
        fields = [
            'id', 'test_case_name', 'input_data', 'expected_output', 'actual_output',
            'is_passed', 'execution_time', 'memory_used', 'error_message', 'points_earned'
        ]


class SubmissionSerializer(serializers.ModelSerializer):
    """Enhanced serializer for Submission model"""
    test_results = TestResultSerializer(many=True, read_only=True)
    exam_session = ExamSessionSerializer(read_only=True)
    problem = ProblemSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'user', 'problem', 'contest', 'exam_session', 'code', 'language',
            'status', 'status_display', 'test_results', 'execution_time', 'memory_used',
            'score', 'points_earned', 'error_message', 'submitted_at'
        ]
        read_only_fields = [
            'id', 'status', 'test_results', 'execution_time', 'memory_used',
            'score', 'points_earned', 'error_message', 'submitted_at'
        ]


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for Leaderboard model"""
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = ['id', 'contest', 'user', 'username', 'total_score', 'problems_solved', 'total_time', 'rank', 'last_submission']


class DiscussionSerializer(serializers.ModelSerializer):
    """Serializer for Discussion model"""
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Discussion
        fields = ['id', 'problem', 'user', 'username', 'title', 'content', 'is_resolved', 'replies_count', 'created_at', 'updated_at']
    
    def get_replies_count(self, obj):
        return obj.replies.count()


class DiscussionReplySerializer(serializers.ModelSerializer):
    """Serializer for DiscussionReply model"""
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = DiscussionReply
        fields = ['id', 'discussion', 'user', 'username', 'content', 'is_solution', 'created_at']


class CodeExecutionSerializer(serializers.Serializer):
    """Serializer for code execution requests"""
    code = serializers.CharField()
    language = serializers.CharField(default='javascript')
    test_cases = serializers.ListField(child=serializers.DictField(), required=False)


class CodeExecutionResponseSerializer(serializers.Serializer):
    """Serializer for code execution responses"""
    success = serializers.BooleanField()
    results = serializers.ListField(child=serializers.DictField())
    execution_time = serializers.FloatField()
    memory_used = serializers.IntegerField(required=False)
    error_message = serializers.CharField(required=False)


class ContestRegistrationSerializer(serializers.Serializer):
    """Serializer for contest registration"""
    contest_id = serializers.IntegerField()
    user_id = serializers.IntegerField()


class ProblemSubmissionSerializer(serializers.Serializer):
    """Serializer for problem submissions"""
    code = serializers.CharField()
    language = serializers.CharField(default='javascript')
    problem_id = serializers.IntegerField()
    contest_id = serializers.IntegerField(required=False) 