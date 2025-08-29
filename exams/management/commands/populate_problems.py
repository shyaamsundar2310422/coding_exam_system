from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from exams.models import (
    Problem, TestCase, ProblemCategory, Contest, ContestParticipant,
    UserProfile, Leaderboard
)


class Command(BaseCommand):
    help = 'Populate the database with sample problems, categories, and contests'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data for HackerRank-style coding platform...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(f'Created superuser: {admin_user.username}')
        else:
            admin_user = User.objects.get(username='admin')
        
        # Create problem categories
        categories = self.create_problem_categories()
        
        # Create sample problems
        problems = self.create_sample_problems(admin_user, categories)
        
        # Create contests
        contests = self.create_sample_contests(admin_user)
        
        # Create user profiles
        self.create_user_profiles()
        
        # Create leaderboards
        self.create_leaderboards(contests)
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
        self.stdout.write(f'Created {len(categories)} problem categories')
        self.stdout.write(f'Created {len(problems)} sample problems')
        self.stdout.write(f'Created {len(contests)} contests')

    def create_problem_categories(self):
        """Create problem difficulty categories"""
        categories = []
        
        category_data = [
            {'name': 'Easy', 'color': '#00B894', 'points': 10, 'description': 'Basic problems for beginners'},
            {'name': 'Medium', 'color': '#FDCB6E', 'points': 20, 'description': 'Intermediate problems'},
            {'name': 'Hard', 'color': '#E17055', 'points': 30, 'description': 'Advanced problems for experts'},
        ]
        
        for data in category_data:
            category, created = ProblemCategory.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
            categories.append(category)
        
        return categories

    def create_sample_problems(self, admin_user, categories):
        """Create sample coding problems"""
        problems = []
        
        # Easy problems
        easy_category = categories[0]
        
        # Problem 1: Two Sum
        two_sum, created = Problem.objects.get_or_create(
            title='Two Sum',
            defaults={
                'description': 'Find two numbers in an array that add up to a target value',
                'problem_statement': '''Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.''',
                'input_format': 'nums: array of integers, target: integer',
                'output_format': 'array of two integers representing indices',
                'constraints': '2 <= nums.length <= 10^4, -10^9 <= nums[i] <= 10^9, -10^9 <= target <= 10^9',
                'sample_input': '[2, 7, 11, 15], target = 9',
                'sample_output': '[0, 1]',
                'explanation': 'Because nums[0] + nums[1] == 9, we return [0, 1].',
                'initial_code': '''function solve(nums, target) {
    // Your code here
    // Return array of two indices
}''',
                'solution_code': '''function solve(nums, target) {
    const map = new Map();
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        if (map.has(complement)) {
            return [map.get(complement), i];
        }
        map.set(nums[i], i);
    }
    return [];
}''',
                'time_limit': 1,
                'memory_limit': 256,
                'category': easy_category,
                'difficulty_score': 1,
                'points': 10,
                'created_by': admin_user
            }
        )
        
        if created:
            # Create test cases for Two Sum
            test_cases = [
                {'name': 'Basic Test', 'input': [2, 7, 11, 15], 'expected': 9, 'is_hidden': False, 'is_sample': True, 'order': 1, 'points': 2},
                {'name': 'Test Case 1', 'input': [3, 2, 4], 'expected': 6, 'is_hidden': False, 'is_sample': True, 'order': 2, 'points': 2},
                {'name': 'Test Case 2', 'input': [3, 3], 'expected': 6, 'is_hidden': False, 'is_sample': True, 'order': 3, 'points': 2},
                {'name': 'Hidden Test 1', 'input': [1, 5, 8, 10, 13, 17], 'expected': 18, 'is_hidden': True, 'is_sample': False, 'order': 4, 'points': 4},
            ]
            
            for tc_data in test_cases:
                TestCase.objects.get_or_create(
                    problem=two_sum,
                    name=tc_data['name'],
                    defaults={
                        'input_data': tc_data['input'],
                        'expected_output': tc_data['expected'],
                        'is_hidden': tc_data['is_hidden'],
                        'is_sample': tc_data['is_sample'],
                        'order': tc_data['order'],
                        'points': tc_data['points']
                    }
                )
            
            self.stdout.write(f'Created problem: {two_sum.title}')
        problems.append(two_sum)
        
        # Problem 2: Palindrome Number
        palindrome, created = Problem.objects.get_or_create(
            title='Palindrome Number',
            defaults={
                'description': 'Check if a number is a palindrome',
                'problem_statement': '''Given an integer x, return true if x is a palindrome, and false otherwise.

A number is a palindrome when it reads the same backward as forward.''',
                'input_format': 'x: integer',
                'output_format': 'boolean (true/false)',
                'constraints': '-2^31 <= x <= 2^31 - 1',
                'sample_input': '121',
                'sample_output': 'true',
                'explanation': '121 reads as 121 from left to right and from right to left.',
                'initial_code': '''function solve(x) {
    // Your code here
    // Return true if x is palindrome, false otherwise
}''',
                'solution_code': '''function solve(x) {
    if (x < 0) return false;
    if (x < 10) return true;
    
    let reversed = 0;
    let original = x;
    
    while (x > 0) {
        reversed = reversed * 10 + x % 10;
        x = Math.floor(x / 10);
    }
    
    return original === reversed;
}''',
                'time_limit': 1,
                'memory_limit': 256,
                'category': easy_category,
                'difficulty_score': 2,
                'points': 15,
                'created_by': admin_user
            }
        )
        
        if created:
            # Create test cases for Palindrome
            test_cases = [
                {'name': 'Positive Palindrome', 'input': [121], 'expected': True, 'is_hidden': False, 'is_sample': True, 'order': 1, 'points': 3},
                {'name': 'Negative Number', 'input': [-121], 'expected': False, 'is_hidden': False, 'is_sample': True, 'order': 2, 'points': 3},
                {'name': 'Single Digit', 'input': [5], 'expected': True, 'is_hidden': False, 'is_sample': True, 'order': 3, 'points': 3},
                {'name': 'Hidden Test 1', 'input': [12321], 'expected': True, 'is_hidden': True, 'is_sample': False, 'order': 4, 'points': 6},
            ]
            
            for tc_data in test_cases:
                TestCase.objects.get_or_create(
                    problem=palindrome,
                    name=tc_data['name'],
                    defaults={
                        'input_data': tc_data['input'],
                        'expected_output': tc_data['expected'],
                        'is_hidden': tc_data['is_hidden'],
                        'is_sample': tc_data['is_sample'],
                        'order': tc_data['order'],
                        'points': tc_data['points']
                    }
                )
            
            self.stdout.write(f'Created problem: {palindrome.title}')
        problems.append(palindrome)
        
        # Medium problem
        medium_category = categories[1]
        
        # Problem 3: Longest Substring Without Repeating Characters
        longest_substring, created = Problem.objects.get_or_create(
            title='Longest Substring Without Repeating Characters',
            defaults={
                'description': 'Find the length of the longest substring without repeating characters',
                'problem_statement': '''Given a string s, find the length of the longest substring without repeating characters.

A substring is a contiguous sequence of characters within a string.''',
                'input_format': 's: string',
                'output_format': 'integer representing the length',
                'constraints': '0 <= s.length <= 5 * 10^4, s consists of English letters, digits, symbols and spaces',
                'sample_input': '"abcabcbb"',
                'sample_output': '3',
                'explanation': 'The answer is "abc", with the length of 3.',
                'initial_code': '''function solve(s) {
    // Your code here
    // Return the length of longest substring without repeating characters
}''',
                'solution_code': '''function solve(s) {
    if (s.length <= 1) return s.length;
    
    let maxLength = 0;
    let start = 0;
    const charMap = new Map();
    
    for (let end = 0; end < s.length; end++) {
        const currentChar = s[end];
        
        if (charMap.has(currentChar) && charMap.get(currentChar) >= start) {
            start = charMap.get(currentChar) + 1;
        }
        
        charMap.set(currentChar, end);
        maxLength = Math.max(maxLength, end - start + 1);
    }
    
    return maxLength;
}''',
                'time_limit': 2,
                'memory_limit': 512,
                'category': medium_category,
                'difficulty_score': 5,
                'points': 25,
                'created_by': admin_user
            }
        )
        
        if created:
            # Create test cases for Longest Substring
            test_cases = [
                {'name': 'Basic Test', 'input': ['abcabcbb'], 'expected': 3, 'is_hidden': False, 'is_sample': True, 'order': 1, 'points': 5},
                {'name': 'Single Character', 'input': ['bbbbb'], 'expected': 1, 'is_hidden': False, 'is_sample': True, 'order': 2, 'points': 5},
                {'name': 'Hidden Test 1', 'input': ['pwwkew'], 'expected': 3, 'is_hidden': True, 'is_sample': False, 'order': 3, 'points': 15},
            ]
            
            for tc_data in test_cases:
                TestCase.objects.get_or_create(
                    problem=longest_substring,
                    name=tc_data['name'],
                    defaults={
                        'input_data': tc_data['input'],
                        'expected_output': tc_data['expected'],
                        'is_hidden': tc_data['is_hidden'],
                        'is_sample': tc_data['is_sample'],
                        'order': tc_data['order'],
                        'points': tc_data['points']
                    }
                )
            
            self.stdout.write(f'Created problem: {longest_substring.title}')
        problems.append(longest_substring)
        
        return problems

    def create_sample_contests(self, admin_user):
        """Create sample contests"""
        contests = []
        
        # Contest 1: Weekly Challenge
        weekly_contest, created = Contest.objects.get_or_create(
            title='Weekly Coding Challenge',
            defaults={
                'description': 'Weekly coding challenge with problems of varying difficulty',
                'start_time': timezone.now() + timedelta(days=1),
                'end_time': timezone.now() + timedelta(days=1, hours=2),
                'duration': 120,
                'max_participants': 1000,
                'contest_type': 'timed',
                'is_public': True,
                'registration_required': False,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'Created contest: {weekly_contest.title}')
        contests.append(weekly_contest)
        
        # Contest 2: Practice Contest
        practice_contest, created = Contest.objects.get_or_create(
            title='Practice Problems',
            defaults={
                'description': 'Practice problems for skill development',
                'start_time': timezone.now() - timedelta(days=1),
                'end_time': timezone.now() + timedelta(days=30),
                'duration': 1440,  # 24 hours
                'max_participants': 5000,
                'contest_type': 'practice',
                'is_public': True,
                'registration_required': False,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'Created contest: {practice_contest.title}')
        contests.append(practice_contest)
        
        return contests

    def create_user_profiles(self):
        """Create user profiles for existing users"""
        for user in User.objects.all():
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': f'Coding enthusiast {user.username}',
                    'rating': 1200,
                    'rank': 'Beginner'
                }
            )
            if created:
                self.stdout.write(f'Created profile for user: {user.username}')

    def create_leaderboards(self, contests):
        """Create sample leaderboards for contests"""
        for contest in contests:
            # Get some users for the leaderboard
            users = User.objects.all()[:5]
            
            for i, user in enumerate(users):
                leaderboard, created = Leaderboard.objects.get_or_create(
                    contest=contest,
                    user=user,
                    defaults={
                        'total_score': (5 - i) * 10,
                        'problems_solved': 5 - i,
                        'total_time': (5 - i) * 300,  # 5 minutes per problem
                        'rank': i + 1
                    }
                )
                
                if created:
                    self.stdout.write(f'Created leaderboard entry for {user.username} in {contest.title}') 