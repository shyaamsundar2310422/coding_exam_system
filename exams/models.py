from django.db import models
from django.contrib.auth.models import User
import json


class Problem(models.Model):
    """Model for coding problems"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    initial_code = models.TextField()
    time_limit = models.IntegerField(default=300)  # in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created_at']


class TestCase(models.Model):
    """Model for test cases"""
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    name = models.CharField(max_length=200)
    input_data = models.JSONField()  # Store input as JSON
    expected_output = models.JSONField()  # Store expected output as JSON
    is_hidden = models.BooleanField(default=False)  # Hidden test cases for final evaluation
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.problem.title} - {self.name}"

    class Meta:
        ordering = ['order']


class ExamSession(models.Model):
    """Model for tracking exam sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_remaining = models.IntegerField()  # in seconds
    is_completed = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.session_id} - {self.problem.title}"

    class Meta:
        ordering = ['-start_time']


class Submission(models.Model):
    """Model for code submissions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]

    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=20, default='javascript')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    test_results = models.JSONField(default=dict)  # Store test results
    execution_time = models.FloatField(null=True, blank=True)  # in seconds
    memory_used = models.IntegerField(null=True, blank=True)  # in KB
    error_message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission {self.id} - {self.exam_session.problem.title}"

    class Meta:
        ordering = ['-submitted_at']


class TestResult(models.Model):
    """Model for individual test results"""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='test_results_detail')
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    input_data = models.JSONField()
    expected_output = models.JSONField()
    actual_output = models.JSONField(null=True, blank=True)
    is_passed = models.BooleanField(default=False)
    execution_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    memory_used = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Test {self.test_case.name} - {'Passed' if self.is_passed else 'Failed'}"

    class Meta:
        ordering = ['test_case__order'] 