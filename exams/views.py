from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import json
import time
import uuid
import subprocess
import tempfile
import os
from datetime import datetime, timedelta
from django.utils import timezone
from .models import (
    Problem, TestCase, ExamSession, Submission, TestResult,
    UserProfile, Contest, ContestParticipant, ProblemCategory,
    Leaderboard, Discussion, DiscussionReply
)
from .serializers import (
    ProblemSerializer, TestCaseSerializer, ExamSessionSerializer,
    SubmissionSerializer, TestResultSerializer, CodeExecutionSerializer,
    CodeExecutionResponseSerializer, UserProfileSerializer, ContestSerializer,
    ContestParticipantSerializer, LeaderboardSerializer, DiscussionSerializer,
    DiscussionReplySerializer, ContestRegistrationSerializer, ProblemSubmissionSerializer
)


class CodeExecutionView(View):
    """Enhanced view for executing code and running tests"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            language = data.get('language', 'javascript')
            test_cases = data.get('test_cases', [])
            
            if not code:
                return JsonResponse({'error': 'Code is required'}, status=400)
            
            # Execute code and run tests
            results = self.execute_code(code, language, test_cases)
            
            return JsonResponse({
                'success': True,
                'results': results,
                'execution_time': 0.1,  # Placeholder
                'memory_used': 0  # Placeholder
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def execute_code(self, code, language, test_cases):
        """Execute code and run test cases"""
        results = []
        
        if language == 'javascript':
            results = self.execute_javascript(code, test_cases)
        elif language == 'python':
            results = self.execute_python(code, test_cases)
        else:
            # Default to JavaScript
            results = self.execute_javascript(code, test_cases)
        
        return results
    
    def execute_javascript(self, code, test_cases):
        """Execute JavaScript code using Node.js"""
        results = []
        
        for test_case in test_cases:
            try:
                # Create a temporary file with the code
                with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                    # Wrap the code in a function and add test execution
                    wrapped_code = f"""
{code}

// Test execution
const testInput = {json.dumps(test_case.get('input', []))};
const expectedOutput = {json.dumps(test_case.get('expected', None))};

try {{
    const result = solve(...testInput);
    console.log(JSON.stringify({{
        success: true,
        result: result,
        expected: expectedOutput,
        passed: result === expectedOutput
    }}));
}} catch (error) {{
    console.log(JSON.stringify({{
        success: false,
        error: error.message
    }}));
}}
"""
                    f.write(wrapped_code)
                    temp_file = f.name
                
                # Execute the code
                result = subprocess.run(
                    ['node', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Parse the output
                if result.returncode == 0:
                    try:
                        output = json.loads(result.stdout.strip())
                        results.append({
                            'name': test_case.get('name', 'Test'),
                            'input': test_case.get('input', []),
                            'expected': test_case.get('expected', None),
                            'actual': output.get('result'),
                            'passed': output.get('passed', False),
                            'error': output.get('error')
                        })
                    except json.JSONDecodeError:
                        results.append({
                            'name': test_case.get('name', 'Test'),
                            'input': test_case.get('input', []),
                            'expected': test_case.get('expected', None),
                            'actual': result.stdout.strip(),
                            'passed': False,
                            'error': 'Invalid output format'
                        })
                else:
                    results.append({
                        'name': test_case.get('name', 'Test'),
                        'input': test_case.get('input', []),
                        'expected': test_case.get('expected', None),
                        'actual': None,
                        'passed': False,
                        'error': result.stderr.strip()
                    })
                
                # Clean up
                os.unlink(temp_file)
                
            except subprocess.TimeoutExpired:
                results.append({
                    'name': test_case.get('name', 'Test'),
                    'input': test_case.get('input', []),
                    'expected': test_case.get('expected', None),
                    'actual': None,
                    'passed': False,
                    'error': 'Execution timeout'
                })
            except Exception as e:
                results.append({
                    'name': test_case.get('name', 'Test'),
                    'input': test_case.get('input', []),
                    'expected': test_case.get('expected', None),
                    'actual': None,
                    'passed': False,
                    'error': str(e)
                })
        
        return results
    
    def execute_python(self, code, test_cases):
        """Execute Python code"""
        results = []
        
        for test_case in test_cases:
            try:
                # Create a temporary file with the code
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    # Wrap the code in a function and add test execution
                    wrapped_code = f"""
{code}

# Test execution
import json
test_input = {json.dumps(test_case.get('input', []))}
expected_output = {json.dumps(test_case.get('expected', None))}

try:
    result = solve(*test_input)
    print(json.dumps({{
        "success": True,
        "result": result,
        "expected": expected_output,
        "passed": result == expected_output
    }}))
except Exception as error:
    print(json.dumps({{
        "success": False,
        "error": str(error)
    }}))
"""
                    f.write(wrapped_code)
                    temp_file = f.name
                
                # Execute the code
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Parse the output
                if result.returncode == 0:
                    try:
                        output = json.loads(result.stdout.strip())
                        results.append({
                            'name': test_case.get('name', 'Test'),
                            'input': test_case.get('input', []),
                            'expected': test_case.get('expected', None),
                            'actual': output.get('result'),
                            'passed': output.get('passed', False),
                            'error': output.get('error')
                        })
                    except json.JSONDecodeError:
                        results.append({
                            'name': test_case.get('name', 'Test'),
                            'input': test_case.get('input', []),
                            'expected': test_case.get('expected', None),
                            'actual': result.stdout.strip(),
                            'passed': False,
                            'error': 'Invalid output format'
                        })
                else:
                    results.append({
                        'name': test_case.get('name', 'Test'),
                        'input': test_case.get('input', []),
                        'expected': test_case.get('expected', None),
                        'actual': None,
                        'passed': False,
                        'error': result.stderr.strip()
                    })
                
                # Clean up
                os.unlink(temp_file)
                
            except subprocess.TimeoutExpired:
                results.append({
                    'name': test_case.get('name', 'Test'),
                    'input': test_case.get('input', []),
                    'expected': test_case.get('expected', None),
                    'actual': None,
                    'passed': False,
                    'error': 'Execution timeout'
                })
            except Exception as e:
                results.append({
                    'name': test_case.get('name', 'Test'),
                    'input': test_case.get('input', []),
                    'expected': test_case.get('expected', None),
                    'actual': None,
                    'passed': False,
                    'error': str(e)
                })
        
        return results


class ProblemViewSet(viewsets.ReadOnlyModelViewSet):
    """Enhanced ViewSet for problems"""
    queryset = Problem.objects.filter(is_active=True)
    serializer_class = ProblemSerializer
    permission_classes = [AllowAny]
    
    def list(self, request, *args, **kwargs):
        """Override list method to add filtering and error handling"""
        try:
            # Add filtering options
            category = request.query_params.get('category')
            difficulty = request.query_params.get('difficulty')
            contest = request.query_params.get('contest')
            
            queryset = self.queryset
            
            if category:
                queryset = queryset.filter(category__name=category)
            if difficulty:
                queryset = queryset.filter(difficulty_score=difficulty)
            if contest:
                queryset = queryset.filter(contest_id=contest)
            
            # Update the queryset
            self.queryset = queryset
            
            return super().list(request, *args, **kwargs)
            
        except Exception as e:
            print(f"Error in ProblemViewSet.list: {e}")
            return Response(
                {'error': 'Failed to fetch problems', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def start_exam(self, request, pk=None):
        """Start an exam session for a problem"""
        problem = self.get_object()
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create exam session
        exam_session = ExamSession.objects.create(
            session_id=session_id,
            problem=problem,
            time_remaining=problem.time_limit * 60  # Convert to seconds
        )
        
        return Response({
            'session_id': session_id,
            'problem': ProblemSerializer(problem).data,
            'time_remaining': problem.time_limit * 60
        })


class ContestViewSet(viewsets.ModelViewSet):
    """ViewSet for contests"""
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """Register user for a contest"""
        contest = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if already registered
        if ContestParticipant.objects.filter(contest=contest, user=user).exists():
            return Response({'error': 'Already registered'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check contest capacity
        if contest.current_participants >= contest.max_participants:
            return Response({'error': 'Contest is full'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Register user
        participant = ContestParticipant.objects.create(
            contest=contest,
            user=user
        )
        
        # Update contest participant count
        contest.current_participants += 1
        contest.save()
        
        return Response({
            'message': 'Successfully registered for contest',
            'participant': ContestParticipantSerializer(participant).data
        })
    
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Get contest leaderboard"""
        contest = self.get_object()
        leaderboard = Leaderboard.objects.filter(contest=contest).order_by('rank')
        
        return Response(LeaderboardSerializer(leaderboard, many=True).data)
    
    @action(detail=True, methods=['get'])
    def problems(self, request, pk=None):
        """Get problems for a contest"""
        contest = self.get_object()
        problems = contest.problems.filter(is_active=True)
        
        return Response(ProblemSerializer(problems, many=True).data)


class ExamSessionViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for exam sessions"""
    queryset = ExamSession.objects.all()
    serializer_class = ExamSessionSerializer
    permission_classes = [AllowAny]
    
    def create(self, request):
        """Create a new exam session"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Create session
            exam_session = ExamSession.objects.create(
                session_id=session_id,
                problem_id=serializer.validated_data['problem_id'],
                contest_id=serializer.validated_data.get('contest_id'),
                time_remaining=serializer.validated_data.get('time_remaining', 300)
            )
            
            return Response(ExamSessionSerializer(exam_session).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit code for evaluation"""
        try:
            exam_session = self.get_object()
            print(f"Submit action called for session ID: {pk}")
            print(f"Exam session found: {exam_session}")
        except Exception as e:
            print(f"Error getting exam session: {e}")
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get submission data
        code = request.data.get('code')
        language = request.data.get('language', 'javascript')
        
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create submission
        submission = Submission.objects.create(
            user=request.user if request.user.is_authenticated else None,
            problem=exam_session.problem,
            contest=exam_session.contest,
            exam_session=exam_session,
            code=code,
            language=language
        )
        
        # Execute code against test cases
        test_cases = exam_session.problem.test_cases.all()
        test_data = []
        
        for test_case in test_cases:
            test_data.append({
                'name': test_case.name,
                'input': test_case.input_data,
                'expected': test_case.expected_output
            })
        
        # Execute code
        code_executor = CodeExecutionView()
        results = code_executor.execute_code(code, language, test_data)
        
        # Calculate score and update submission
        total_points = 0
        passed_tests = 0
        
        for i, result in enumerate(results):
            test_case = test_cases[i]
            points_earned = test_case.points if result['passed'] else 0
            total_points += points_earned
            
            if result['passed']:
                passed_tests += 1
            
            # Create detailed test results
            TestResult.objects.create(
                submission=submission,
                test_case=test_case,
                input_data=result['input'],
                expected_output=result['expected'],
                actual_output=result['actual'],
                is_passed=result['passed'],
                error_message=result.get('error', ''),
                points_earned=points_earned
            )
        
        # Determine submission status
        if passed_tests == len(test_cases):
            submission.status = 'accepted'
        else:
            submission.status = 'wrong_answer'
        
        # Update submission
        submission.score = total_points
        submission.points_earned = total_points
        submission.test_results = results
        submission.status = submission.status
        submission.save()
        
        # Update problem statistics
        exam_session.problem.update_statistics()
        
        # Mark session as submitted
        exam_session.is_submitted = True
        exam_session.score = total_points
        exam_session.save()
        
        print(f"Submission successful: {submission.id}")
        return Response(SubmissionSerializer(submission).data)


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Enhanced ViewSet for submissions"""
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter submissions based on user and contest"""
        queryset = super().get_queryset()
        
        # Filter by user if authenticated
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by contest if specified
        contest_id = self.request.query_params.get('contest')
        if contest_id:
            queryset = queryset.filter(contest_id=contest_id)
        
        return queryset


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user profiles"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Get user's submission history"""
        profile = self.get_object()
        submissions = profile.user.submissions.all().order_by('-submitted_at')
        
        return Response(SubmissionSerializer(submissions, many=True).data)


class DiscussionViewSet(viewsets.ModelViewSet):
    """ViewSet for problem discussions"""
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter discussions by problem"""
        queryset = super().get_queryset()
        problem_id = self.request.query_params.get('problem')
        if problem_id:
            queryset = queryset.filter(problem_id=problem_id)
        return queryset


def frontend_view(request):
    """Frontend view for the coding exam system"""
    return render(request, 'exams/index.html')


def contest_view(request, contest_id):
    """Contest-specific view"""
    contest = get_object_or_404(Contest, id=contest_id)
    return render(request, 'exams/contest.html', {'contest': contest})


def leaderboard_view(request):
    """Global leaderboard view"""
    return render(request, 'exams/leaderboard.html')


def profile_view(request, username):
    """User profile view"""
    user = get_object_or_404(User, username=username)
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None
    
    return render(request, 'exams/profile.html', {'user': user, 'profile': profile}) 