from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json
import uuid


class UserProfile(models.Model):
    """Extended user profile for contest participants"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    rating = models.IntegerField(default=1200)  # Elo-style rating
    total_submissions = models.IntegerField(default=0)
    problems_solved = models.IntegerField(default=0)
    contests_participated = models.IntegerField(default=0)
    rank = models.CharField(max_length=20, default='Beginner')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def update_rating(self, new_rating):
        self.rating = new_rating
        if self.rating < 1000:
            self.rank = 'Beginner'
        elif self.rating < 1500:
            self.rank = 'Intermediate'
        elif self.rating < 2000:
            self.rank = 'Advanced'
        else:
            self.rank = 'Expert'
        self.save()


class Contest(models.Model):
    """Model for coding contests"""
    CONTEST_STATUS = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CONTEST_TYPE = [
        ('practice', 'Practice'),
        ('timed', 'Timed Contest'),
        ('tournament', 'Tournament'),
        ('challenge', 'Challenge'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.IntegerField(help_text='Duration in minutes')
    max_participants = models.IntegerField(default=1000)
    current_participants = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=CONTEST_STATUS, default='upcoming')
    contest_type = models.CharField(max_length=20, choices=CONTEST_TYPE, default='timed')
    is_public = models.BooleanField(default=True)
    registration_required = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contests_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-start_time']


class ContestParticipant(models.Model):
    """Model for contest participants"""
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contest_participations')
    joined_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['contest', 'user']
        ordering = ['-score', 'joined_at']


class ProblemCategory(models.Model):
    """Model for problem categories (Easy, Medium, Hard)"""
    name = models.CharField(max_length=50)  # Easy, Medium, Hard
    color = models.CharField(max_length=7, default='#000000')  # Hex color
    points = models.IntegerField(default=10)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Problem(models.Model):
    """Enhanced model for coding problems"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    problem_statement = models.TextField(help_text='Detailed problem description', blank=True, default='')
    input_format = models.TextField(help_text='Input format description', blank=True, default='')
    output_format = models.TextField(help_text='Output format description', blank=True, default='')
    constraints = models.TextField(help_text='Problem constraints', blank=True, default='')
    sample_input = models.TextField(help_text='Sample input examples', blank=True, default='')
    sample_output = models.TextField(help_text='Sample output examples', blank=True, default='')
    explanation = models.TextField(help_text='Solution explanation', blank=True, default='')
    
    initial_code = models.TextField()
    solution_code = models.TextField(blank=True, help_text='Reference solution', default='')
    
    time_limit = models.IntegerField(default=300, help_text='Time limit in seconds')
    memory_limit = models.IntegerField(default=512, help_text='Memory limit in MB')
    
    category = models.ForeignKey(ProblemCategory, on_delete=models.CASCADE, related_name='problems', null=True, blank=True)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='problems', null=True, blank=True)
    
    difficulty_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    points = models.IntegerField(default=10)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='problems_created', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistics
    total_submissions = models.IntegerField(default=0)
    successful_submissions = models.IntegerField(default=0)
    acceptance_rate = models.FloatField(default=0.0)
    
    def __str__(self):
        return self.title
    
    def update_statistics(self):
        """Update problem statistics"""
        self.total_submissions = self.submissions.count()
        self.successful_submissions = self.submissions.filter(status='accepted').count()
        if self.total_submissions > 0:
            self.acceptance_rate = (self.successful_submissions / self.total_submissions) * 100
        self.save()
    
    class Meta:
        ordering = ['difficulty_score', 'created_at']


class TestCase(models.Model):
    """Enhanced model for test cases"""
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    name = models.CharField(max_length=200)
    input_data = models.JSONField()
    expected_output = models.JSONField()
    is_hidden = models.BooleanField(default=False)
    is_sample = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.problem.title} - {self.name}"
    
    class Meta:
        ordering = ['order']


class ExamSession(models.Model):
    """Enhanced model for exam sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='sessions', null=True, blank=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='sessions')
    session_id = models.CharField(max_length=100, unique=True)
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_remaining = models.IntegerField()
    time_spent = models.IntegerField(default=0)
    
    is_completed = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Session {self.session_id} - {self.problem.title}"
    
    class Meta:
        ordering = ['-start_time']


class Submission(models.Model):
    """Enhanced model for code submissions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('accepted', 'Accepted'),
        ('wrong_answer', 'Wrong Answer'),
        ('time_limit_exceeded', 'Time Limit Exceeded'),
        ('memory_limit_exceeded', 'Memory Limit Exceeded'),
        ('runtime_error', 'Runtime Error'),
        ('compilation_error', 'Compilation Error'),
        ('internal_error', 'Internal Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions', null=True, blank=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submissions')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='submissions', null=True, blank=True)
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='submissions', null=True, blank=True)
    
    code = models.TextField()
    language = models.CharField(max_length=20, default='javascript')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    
    test_results = models.JSONField(default=dict)
    execution_time = models.FloatField(null=True, blank=True)
    memory_used = models.IntegerField(null=True, blank=True)
    
    score = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    
    error_message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Submission {self.id} - {self.problem.title} by {self.user.username}"
    
    class Meta:
        ordering = ['-submitted_at']


class TestResult(models.Model):
    """Enhanced model for individual test results"""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='test_results_detail')
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    
    input_data = models.JSONField()
    expected_output = models.JSONField()
    actual_output = models.JSONField(null=True, blank=True)
    
    is_passed = models.BooleanField(default=False)
    execution_time = models.FloatField(null=True, blank=True)
    memory_used = models.IntegerField(null=True, blank=True)
    
    error_message = models.TextField(blank=True)
    points_earned = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Test {self.test_case.name} - {'Passed' if self.is_passed else 'Failed'}"
    
    class Meta:
        ordering = ['test_case__order']


class Leaderboard(models.Model):
    """Model for contest leaderboards"""
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='leaderboards')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    
    total_score = models.IntegerField(default=0)
    problems_solved = models.IntegerField(default=0)
    total_time = models.IntegerField(default=0, help_text='Total time in seconds')
    rank = models.IntegerField()
    
    last_submission = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['contest', 'user']
        ordering = ['rank', '-total_score', 'total_time']


class Discussion(models.Model):
    """Model for problem discussions"""
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']


class DiscussionReply(models.Model):
    """Model for discussion replies"""
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_replies')
    content = models.TextField()
    is_solution = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at'] 