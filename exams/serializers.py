from rest_framework import serializers
from .models import Problem, TestCase, ExamSession, Submission, TestResult


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['id', 'name', 'input_data', 'expected_output', 'is_hidden', 'order']


class ProblemSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True, read_only=True)
    
    class Meta:
        model = Problem
        fields = ['id', 'title', 'description', 'initial_code', 'time_limit', 'test_cases']


class ExamSessionSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer(read_only=True)
    problem_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ExamSession
        fields = ['id', 'session_id', 'problem', 'problem_id', 'start_time', 'end_time', 
                 'time_remaining', 'is_completed', 'is_submitted']
        read_only_fields = ['id', 'session_id', 'start_time', 'end_time', 'is_completed', 'is_submitted']


class TestResultSerializer(serializers.ModelSerializer):
    test_case_name = serializers.CharField(source='test_case.name', read_only=True)
    
    class Meta:
        model = TestResult
        fields = ['id', 'test_case_name', 'input_data', 'expected_output', 'actual_output', 
                 'is_passed', 'execution_time', 'error_message']


class SubmissionSerializer(serializers.ModelSerializer):
    test_results = TestResultSerializer(many=True, read_only=True)
    exam_session = ExamSessionSerializer(read_only=True)
    
    class Meta:
        model = Submission
        fields = ['id', 'exam_session', 'code', 'language', 'status', 'test_results', 
                 'execution_time', 'memory_used', 'error_message', 'submitted_at']
        read_only_fields = ['id', 'status', 'test_results', 'execution_time', 'memory_used', 
                           'error_message', 'submitted_at']


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
    error_message = serializers.CharField(required=False) 