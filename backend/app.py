from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import hashlib
import os
import subprocess
import tempfile
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this_in_production'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            solved_problems TEXT DEFAULT '[]',
            submissions INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            problem_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            language TEXT DEFAULT 'python',
            status TEXT DEFAULT 'accepted',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
    except:
        pass
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

init_db()
# ========== 100 UNIQUE PROBLEMS ==========
PROBLEMS = {
    1: {"title": "Two Sum", "difficulty": "Easy", "description": "Find two numbers that add up to target.", "examples": "Input: nums=[2,7,11,15], target=9 → Output: [0,1]", "constraints": "2 <= nums.length <= 10^4"},
    2: {"title": "Palindrome Number", "difficulty": "Easy", "description": "Given an integer x, return true if x is a palindrome, and false otherwise.", "examples": "Input: x = 121 → Output: true", "constraints": "-2^31 <= x <= 2^31 - 1"},
    3: {"title": "Valid Parentheses", "difficulty": "Easy", "description": "Check if brackets are valid.", "examples": "Input: '()[]{}' → Output: true", "constraints": "1 <= s.length <= 10^4"},
    4: {"title": "Reverse Integer", "difficulty": "Easy", "description": "Reverse digits of an integer.", "examples": "Input: 123 → Output: 321", "constraints": "-2^31 <= x <= 2^31 - 1"},
    5: {"title": "Roman to Integer", "difficulty": "Easy", "description": "Convert Roman numeral to integer.", "examples": "Input: 'MCMXCIV' → Output: 1994", "constraints": "1 <= s.length <= 15"},
    6: {"title": "Longest Common Prefix", "difficulty": "Easy", "description": "Find longest common prefix string.", "examples": "Input: ['flower','flow','flight'] → Output: 'fl'", "constraints": "1 <= strs.length <= 200"},
    7: {"title": "Merge Two Sorted Lists", "difficulty": "Easy", "description": "Merge two sorted linked lists.", "examples": "Input: list1=[1,2,4], list2=[1,3,4] → Output: [1,1,2,3,4,4]", "constraints": "0 <= node count <= 50"},
    8: {"title": "Remove Duplicates", "difficulty": "Easy", "description": "Remove duplicates from sorted array.", "examples": "Input: [1,1,2] → Output: 2", "constraints": "1 <= nums.length <= 3*10^4"},
    9: {"title": "Plus One", "difficulty": "Easy", "description": "Add one to number represented as array.", "examples": "Input: [1,2,3] → Output: [1,2,4]", "constraints": "1 <= digits.length <= 100"},
    10: {"title": "Climbing Stairs", "difficulty": "Easy", "description": "Count ways to climb n stairs.", "examples": "Input: n=3 → Output: 3", "constraints": "1 <= n <= 45"},
    11: {"title": "Single Number", "difficulty": "Easy", "description": "Find element that appears once.", "examples": "Input: [2,2,1] → Output: 1", "constraints": "1 <= nums.length <= 3*10^4"},
    12: {"title": "Majority Element", "difficulty": "Easy", "description": "Find element appearing more than n/2 times.", "examples": "Input: [3,2,3] → Output: 3", "constraints": "1 <= n <= 5*10^4"},
    13: {"title": "Best Time to Buy Stock", "difficulty": "Easy", "description": "Maximize profit from stock prices.", "examples": "Input: [7,1,5,3,6,4] → Output: 5", "constraints": "1 <= prices.length <= 10^5"},
    14: {"title": "Move Zeroes", "difficulty": "Easy", "description": "Move all zeros to end.", "examples": "Input: [0,1,0,3,12] → Output: [1,3,12,0,0]", "constraints": "1 <= nums.length <= 10^4"},
    15: {"title": "Valid Anagram", "difficulty": "Easy", "description": "Check if strings are anagrams.", "examples": "Input: s='anagram', t='nagaram' → Output: true", "constraints": "1 <= s.length <= 5*10^4"},
    16: {"title": "Missing Number", "difficulty": "Easy", "description": "Find missing number in array.", "examples": "Input: [3,0,1] → Output: 2", "constraints": "1 <= n <= 10^4"},
    17: {"title": "Contains Duplicate", "difficulty": "Easy", "description": "Check if any value appears twice.", "examples": "Input: [1,2,3,1] → Output: true", "constraints": "1 <= nums.length <= 10^5"},
    18: {"title": "Maximum Subarray", "difficulty": "Easy", "description": "Find largest sum subarray.", "examples": "Input: [-2,1,-3,4,-1,2,1,-5,4] → Output: 6", "constraints": "1 <= nums.length <= 10^5"},
    19: {"title": "FizzBuzz", "difficulty": "Easy", "description": "Print Fizz for multiples of 3, Buzz for 5.", "examples": "Input: n=5 → Output: ['1','2','Fizz','4','Buzz']", "constraints": "1 <= n <= 10^4"},
    20: {"title": "Reverse String", "difficulty": "Easy", "description": "Reverse a string in place.", "examples": "Input: ['h','e','l','l','o'] → Output: ['o','l','l','e','h']", "constraints": "1 <= s.length <= 10^5"},
    21: {"title": "3Sum", "difficulty": "Medium", "description": "Find triplets that sum to zero.", "examples": "Input: [-1,0,1,2,-1,-4] → Output: [[-1,-1,2],[-1,0,1]]", "constraints": "3 <= nums.length <= 3000"},
    22: {"title": "Group Anagrams", "difficulty": "Medium", "description": "Group strings by anagram.", "examples": "Input: ['eat','tea','tan','ate','nat','bat'] → Output: groups", "constraints": "1 <= strs.length <= 10^4"},
    23: {"title": "Longest Substring", "difficulty": "Medium", "description": "Longest substring without repeating chars.", "examples": "Input: 'abcabcbb' → Output: 3", "constraints": "0 <= s.length <= 5*10^4"},
    24: {"title": "Container With Most Water", "difficulty": "Medium", "description": "Find max water container.", "examples": "Input: [1,8,6,2,5,4,8,3,7] → Output: 49", "constraints": "2 <= n <= 10^5"},
    25: {"title": "Search in Rotated Array", "difficulty": "Medium", "description": "Search in rotated sorted array.", "examples": "Input: nums=[4,5,6,7,0,1,2], target=0 → Output: 4", "constraints": "1 <= nums.length <= 5000"},
    26: {"title": "Combination Sum", "difficulty": "Medium", "description": "Find combinations that sum to target.", "examples": "Input: candidates=[2,3,6,7], target=7 → Output: [[2,2,3],[7]]", "constraints": "1 <= candidates.length <= 30"},
    27: {"title": "Permutations", "difficulty": "Medium", "description": "Generate all permutations.", "examples": "Input: [1,2,3] → Output: all permutations", "constraints": "1 <= nums.length <= 6"},
    28: {"title": "Rotate Image", "difficulty": "Medium", "description": "Rotate matrix 90 degrees.", "examples": "Input: [[1,2,3],[4,5,6],[7,8,9]] → Output: rotated", "constraints": "1 <= n <= 20"},
    29: {"title": "Spiral Matrix", "difficulty": "Medium", "description": "Return spiral order of matrix.", "examples": "Input: [[1,2,3],[4,5,6],[7,8,9]] → Output: [1,2,3,6,9,8,7,4,5]", "constraints": "m, n >= 1"},
    30: {"title": "Jump Game", "difficulty": "Medium", "description": "Can reach last index?", "examples": "Input: [2,3,1,1,4] → Output: true", "constraints": "1 <= nums.length <= 10^4"},
    31: {"title": "Merge Intervals", "difficulty": "Medium", "description": "Merge overlapping intervals.", "examples": "Input: [[1,3],[2,6],[8,10],[15,18]] → Output: [[1,6],[8,10],[15,18]]", "constraints": "1 <= intervals.length <= 10^4"},
    32: {"title": "Unique Paths", "difficulty": "Medium", "description": "Count unique paths in grid.", "examples": "Input: m=3, n=7 → Output: 28", "constraints": "1 <= m, n <= 100"},
    33: {"title": "Word Search", "difficulty": "Medium", "description": "Find word in grid.", "examples": "Input: board=[[...]], word='ABCCED' → Output: true", "constraints": "m, n <= 6"},
    34: {"title": "Decode Ways", "difficulty": "Medium", "description": "Count ways to decode message.", "examples": "Input: '226' → Output: 3", "constraints": "1 <= s.length <= 100"},
    35: {"title": "Validate BST", "difficulty": "Medium", "description": "Validate binary search tree.", "examples": "Input: root → Output: true/false", "constraints": "Node count <= 10^4"},
    36: {"title": "Level Order Traversal", "difficulty": "Medium", "description": "Binary tree level order.", "examples": "Input: [3,9,20,null,null,15,7] → Output: [[3],[9,20],[15,7]]", "constraints": "Node count <= 2000"},
    37: {"title": "Number of Islands", "difficulty": "Medium", "description": "Count islands in grid.", "examples": "Input: grid of 1s and 0s → Output: island count", "constraints": "m, n <= 300"},
    38: {"title": "Coin Change", "difficulty": "Medium", "description": "Minimum coins for amount.", "examples": "Input: coins=[1,2,5], amount=11 → Output: 3", "constraints": "1 <= coins.length <= 12"},
    39: {"title": "House Robber", "difficulty": "Medium", "description": "Max robbery without adjacent.", "examples": "Input: [1,2,3,1] → Output: 4", "constraints": "1 <= nums.length <= 100"},
    40: {"title": "Top K Frequent", "difficulty": "Medium", "description": "Top K frequent elements.", "examples": "Input: [1,1,1,2,2,3], k=2 → Output: [1,2]", "constraints": "1 <= nums.length <= 10^5"},
    41: {"title": "Median of Two Arrays", "difficulty": "Hard", "description": "Find median of two sorted arrays.", "examples": "Input: nums1=[1,3], nums2=[2] → Output: 2.0", "constraints": "0 <= m, n <= 1000"},
    42: {"title": "Merge k Sorted Lists", "difficulty": "Hard", "description": "Merge k sorted linked lists.", "examples": "Input: lists=[[1,4,5],[1,3,4],[2,6]] → Output: [1,1,2,3,4,4,5,6]", "constraints": "k <= 10^4"},
    43: {"title": "Regular Expression", "difficulty": "Hard", "description": "Regex matching with '.' and '*'.", "examples": "Input: s='aa', p='a*' → Output: true", "constraints": "1 <= s.length <= 20"},
    44: {"title": "Trapping Rain Water", "difficulty": "Hard", "description": "Trapped rainwater calculation.", "examples": "Input: [0,1,0,2,1,0,1,3,2,1,2,1] → Output: 6", "constraints": "1 <= n <= 2*10^4"},
    45: {"title": "N-Queens", "difficulty": "Hard", "description": "Place N queens on board.", "examples": "Input: n=4 → Output: solutions", "constraints": "1 <= n <= 9"},
    46: {"title": "Wildcard Matching", "difficulty": "Hard", "description": "Wildcard pattern matching.", "examples": "Input: s='aa', p='*' → Output: true", "constraints": "0 <= s.length <= 2000"},
    47: {"title": "Maximal Rectangle", "difficulty": "Hard", "description": "Largest rectangle in binary matrix.", "examples": "Input: matrix of 0/1 → Output: max area", "constraints": "rows, cols <= 200"},
    48: {"title": "Binary Tree Max Path", "difficulty": "Hard", "description": "Maximum path sum in tree.", "examples": "Input: root → Output: max sum", "constraints": "Node count <= 3*10^4"},
    49: {"title": "Serialize Deserialize", "difficulty": "Hard", "description": "Serialize/deserialize binary tree.", "examples": "Input: root → Output: serialized string", "constraints": "Node count <= 10^4"},
    50: {"title": "Longest Valid Parens", "difficulty": "Hard", "description": "Longest valid parentheses.", "examples": "Input: '(()' → Output: 2", "constraints": "0 <= s.length <= 3*10^4"},
    51: {"title": "Edit Distance", "difficulty": "Hard", "description": "Minimum edit operations.", "examples": "Input: word1='horse', word2='ros' → Output: 3", "constraints": "0 <= word1.length <= 500"},
    52: {"title": "Jump Game II", "difficulty": "Hard", "description": "Minimum jumps to end.", "examples": "Input: [2,3,1,1,4] → Output: 2", "constraints": "1 <= nums.length <= 10^4"},
    53: {"title": "Largest Rectangle", "difficulty": "Hard", "description": "Largest rectangle in histogram.", "examples": "Input: [2,1,5,6,2,3] → Output: 10", "constraints": "1 <= heights.length <= 10^5"},
    54: {"title": "Sliding Window Max", "difficulty": "Hard", "description": "Maximum in sliding window.", "examples": "Input: [1,3,-1,-3,5,3,6,7], k=3 → Output: [3,3,5,5,6,7]", "constraints": "1 <= nums.length <= 10^5"},
    55: {"title": "Minimum Window", "difficulty": "Hard", "description": "Minimum window substring.", "examples": "Input: s='ADOBECODEBANC', t='ABC' → Output: 'BANC'", "constraints": "1 <= s.length <= 10^5"},
    56: {"title": "Alien Dictionary", "difficulty": "Hard", "description": "Order of alien alphabet.", "examples": "Input: ['wrt','wrf','er','ett','rftt'] → Output: 'wertf'", "constraints": "1 <= words.length <= 100"},
    57: {"title": "Palindrome Pairs", "difficulty": "Hard", "description": "Find palindrome pairs.", "examples": "Input: ['abcd','dcba','lls','s'] → Output: pairs", "constraints": "1 <= words.length <= 5000"},
    58: {"title": "Maximum Gap", "difficulty": "Hard", "description": "Maximum gap in array.", "examples": "Input: [3,6,9,1] → Output: 3", "constraints": "1 <= nums.length <= 10^5"},
    59: {"title": "Reverse Nodes in k-Group", "difficulty": "Hard", "description": "Reverse nodes in k-group.", "examples": "Input: head=[1,2,3,4,5], k=2 → Output: [2,1,4,3,5]", "constraints": "Node count <= 5000"},
    60: {"title": "Sudoku Solver", "difficulty": "Hard", "description": "Solve Sudoku puzzle.", "examples": "Input: 9x9 board → Output: solved board", "constraints": "board.length == 9"},
    61: {"title": "First Missing Positive", "difficulty": "Hard", "description": "Smallest missing positive.", "examples": "Input: [3,4,-1,1] → Output: 2", "constraints": "1 <= nums.length <= 10^5"},
    62: {"title": "Longest Consecutive", "difficulty": "Hard", "description": "Longest consecutive sequence.", "examples": "Input: [100,4,200,1,3,2] → Output: 4", "constraints": "0 <= nums.length <= 10^5"},
    63: {"title": "Word Ladder II", "difficulty": "Hard", "description": "Shortest transformation sequences.", "examples": "Input: begin='hit', end='cog' → Output: paths", "constraints": "1 <= wordList.length <= 500"},
    64: {"title": "Find Median Stream", "difficulty": "Hard", "description": "Median from data stream.", "examples": "Add numbers → get median", "constraints": "0 <= num <= 10^5"},
    65: {"title": "Max Frequency Stack", "difficulty": "Hard", "description": "FreqStack implementation.", "examples": "Push/pop operations", "constraints": "0 <= val <= 10^9"},
    66: {"title": "Shortest Palindrome", "difficulty": "Hard", "description": "Make string palindrome.", "examples": "Input: 'aacecaaa' → Output: 'aaacecaaa'", "constraints": "0 <= s.length <= 5*10^4"},
    67: {"title": "Max Points on Line", "difficulty": "Hard", "description": "Max points on same line.", "examples": "Input: [[1,1],[2,2],[3,3]] → Output: 3", "constraints": "1 <= points.length <= 300"},
    68: {"title": "Russian Doll Envelopes", "difficulty": "Hard", "description": "Max number of envelopes.", "examples": "Input: [[5,4],[6,4],[6,7],[2,3]] → Output: 3", "constraints": "1 <= envelopes.length <= 10^5"},
    69: {"title": "Number of Digit One", "difficulty": "Hard", "description": "Count digit 1 occurrences.", "examples": "Input: n=13 → Output: 6", "constraints": "0 <= n <= 10^9"},
    70: {"title": "Basic Calculator", "difficulty": "Hard", "description": "Evaluate expression.", "examples": "Input: '1 + 1' → Output: 2", "constraints": "1 <= s.length <= 3*10^5"},
    71: {"title": "Max Sliding Window", "difficulty": "Hard", "description": "Sliding window maximum.", "examples": "Input: [1,3,-1,-3,5,3,6,7], k=3 → Output: [3,3,5,5,6,7]", "constraints": "1 <= nums.length <= 10^5"},
    72: {"title": "Serialize BST", "difficulty": "Hard", "description": "Serialize/deserialize BST.", "examples": "BST to string and back", "constraints": "Node count <= 10^4"},
    73: {"title": "Reconstruct Itinerary", "difficulty": "Hard", "description": "Reconstruct flight path.", "examples": "Input: tickets → Output: itinerary", "constraints": "1 <= tickets.length <= 300"},
    74: {"title": "Min Cost to Connect", "difficulty": "Hard", "description": "Connect all points min cost.", "examples": "Input: [[0,0],[2,2],[3,10],[5,2],[7,0]] → Output: 20", "constraints": "1 <= points.length <= 1000"},
    75: {"title": "Maximum Product", "difficulty": "Hard", "description": "Maximum product subarray.", "examples": "Input: [2,3,-2,4] → Output: 6", "constraints": "1 <= nums.length <= 2*10^4"},
    76: {"title": "House Robber III", "difficulty": "Hard", "description": "Binary tree robbery.", "examples": "Input: root → Output: max amount", "constraints": "Node count <= 10^4"},
    77: {"title": "Count of Smaller", "difficulty": "Hard", "description": "Count smaller after self.", "examples": "Input: [5,2,6,1] → Output: [2,1,1,0]", "constraints": "1 <= nums.length <= 10^5"},
    78: {"title": "Remove Invalid Parens", "difficulty": "Hard", "description": "Remove invalid parentheses.", "examples": "Input: '()())()' → Output: ['()()()', '(())()']", "constraints": "1 <= s.length <= 25"},
    79: {"title": "Longest Increasing Path", "difficulty": "Hard", "description": "Longest increasing path in matrix.", "examples": "Input: matrix → Output: length", "constraints": "m, n <= 200"},
    80: {"title": "Palindrome Partitioning", "difficulty": "Hard", "description": "Partition palindrome substrings.", "examples": "Input: 'aab' → Output: [['a','a','b'],['aa','b']]", "constraints": "1 <= s.length <= 16"},
    81: {"title": "Scramble String", "difficulty": "Hard", "description": "Check scramble strings.", "examples": "Input: s1='great', s2='rgeat' → Output: true", "constraints": "1 <= s1.length <= 30"},
    82: {"title": "Largest Divisible Set", "difficulty": "Hard", "description": "Largest divisible subset.", "examples": "Input: [1,2,3] → Output: [1,2] or [1,3]", "constraints": "1 <= nums.length <= 1000"},
    83: {"title": "Strange Printer", "difficulty": "Hard", "description": "Minimum turns to print.", "examples": "Input: 'aaabbb' → Output: 2", "constraints": "1 <= s.length <= 100"},
    84: {"title": "Super Egg Drop", "difficulty": "Hard", "description": "Egg drop problem.", "examples": "Input: k=1, n=2 → Output: 2", "constraints": "1 <= k <= 100, 1 <= n <= 10^4"},
    85: {"title": "Burst Balloons", "difficulty": "Hard", "description": "Max coins from balloons.", "examples": "Input: [3,1,5,8] → Output: 167", "constraints": "1 <= n <= 300"},
    86: {"title": "Minimum Difficulty", "difficulty": "Hard", "description": "Job schedule difficulty.", "examples": "Input: [6,5,4,3,2,1], d=2 → Output: 7", "constraints": "1 <= jobDifficulty.length <= 300"},
    87: {"title": "Max Value of Equation", "difficulty": "Hard", "description": "Max yi+yj+|xi-xj|.", "examples": "Input: points=[[1,3],[2,0],[5,10],[6,-10]], k=1 → Output: 4", "constraints": "2 <= points.length <= 10^5"},
    88: {"title": "Minimum Distance", "difficulty": "Hard", "description": "Min distance to type word.", "examples": "Input: word='CAKE' → Output: 3", "constraints": "1 <= word.length <= 100"},
    89: {"title": "Minimum Skips", "difficulty": "Hard", "description": "Min skips to arrive on time.", "examples": "Input: dist=[1,3,2], speed=4, hoursBefore=2 → Output: 1", "constraints": "1 <= n <= 1000"},
    90: {"title": "Max Score Words", "difficulty": "Hard", "description": "Maximum score from words.", "examples": "Input: words, letters, score → Output: max", "constraints": "1 <= words.length <= 14"},
    91: {"title": "Minimum Cost Tree", "difficulty": "Hard", "description": "Min cost to merge stones.", "examples": "Input: stones=[3,2,4,1], k=2 → Output: 20", "constraints": "1 <= stones.length <= 30"},
    92: {"title": "Count Ways to Build", "difficulty": "Hard", "description": "Ways to build rooms.", "examples": "Input: prevRoom=[-1,0,1] → Output: ways", "constraints": "1 <= n <= 10^5"},
    93: {"title": "Maximum Performance", "difficulty": "Hard", "description": "Max performance of team.", "examples": "Input: n=6, speed=[2,10,3,1,5,8], efficiency=[5,4,3,9,7,2], k=2 → Output: 60", "constraints": "1 <= k <= n <= 10^5"},
    94: {"title": "Minimum Number of Taps", "difficulty": "Hard", "description": "Min taps to water garden.", "examples": "Input: n=5, ranges=[3,4,1,1,0,0] → Output: 1", "constraints": "1 <= n <= 10^4"},
    95: {"title": "Max Profit with K", "difficulty": "Hard", "description": "Max profit with K transactions.", "examples": "Input: k=2, prices=[2,4,1] → Output: 2", "constraints": "0 <= k <= 100"},
    96: {"title": "Race Car", "difficulty": "Hard", "description": "Minimum instructions to reach target.", "examples": "Input: target=3 → Output: 2", "constraints": "1 <= target <= 10^4"},
    97: {"title": "Minimum Window Subsequence", "difficulty": "Hard", "description": "Min window containing subsequence.", "examples": "Input: s='abcdebdde', t='bde' → Output: 'bcde'", "constraints": "1 <= s.length <= 2*10^4"},
    98: {"title": "Maximum Vacation Days", "difficulty": "Hard", "description": "Max vacation days.", "examples": "Input: flights, days → Output: max", "constraints": "n == flights.length"},
    99: {"title": "Minimum Difficulty of Job", "difficulty": "Hard", "description": "Min difficulty job schedule.", "examples": "Input: [6,5,4,3,2,1], d=2 → Output: 7", "constraints": "1 <= jobDifficulty.length <= 300"},
    100: {"title": "Student Attendance II", "difficulty": "Hard", "description": "Rewardable attendance records.", "examples": "Input: n=2 → Output: 8", "constraints": "1 <= n <= 10^5"}
} 


# ========== CODE RUNNER ==========
def run_code(code, user_input=""):
    """Execute Python code and return output"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        result = subprocess.run(
            ['python', temp_file],
            input=user_input,
            capture_output=True,
            text=True,
            timeout=10
        )
        os.unlink(temp_file)
        return result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return "", "Error: Code execution timed out (10 seconds limit)"
    except FileNotFoundError:
        return "", "Error: Python not found. Please make sure Python is installed."
    except Exception as e:
        return "", f"Error: {str(e)}"

# ========== ROUTES ==========

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or len(username) < 3:
            return render_template('signup.html', error="Username must be at least 3 characters")
        if not email or '@' not in email:
            return render_template('signup.html', error="Valid email required")
        if not password or len(password) < 4:
            return render_template('signup.html', error="Password must be at least 4 characters")
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")
        
        hashed_password = hash_password(password)
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, email, password, solved_problems, submissions) VALUES (?, ?, ?, ?, ?)",
                         (username, email, hashed_password, '[]', 0))
            conn.commit()
            conn.close()
            flash("Account created! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup.html', error="Username or email already exists")
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        hashed_password = hash_password(password)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password")
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT solved_problems, submissions FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    solved = eval(user['solved_problems']) if user['solved_problems'] else []
    solved_count = len(solved)
    completion = (solved_count / 100) * 100
    
    return render_template('dashboard.html',
                         username=session['username'],
                         solved_count=solved_count,
                         completion=round(completion),
                         submissions=user['submissions'])

@app.route('/problems')
def problems():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT solved_problems FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    solved = eval(user['solved_problems']) if user['solved_problems'] else []
    
    return render_template('problems.html', problems=PROBLEMS, solved=solved, username=session['username'])

@app.route('/solve/<int:problem_id>')
def solve(problem_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if problem_id not in PROBLEMS:
        return "Problem not found", 404
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT solved_problems FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    solved = eval(user['solved_problems']) if user['solved_problems'] else []
    already_solved = problem_id in solved
    
    return render_template('solve.html', 
                         problem=PROBLEMS[problem_id],
                         problem_id=problem_id,
                         already_solved=already_solved,
                         username=session['username'])

@app.route('/api/run_code', methods=['POST'])
def api_run_code():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.get_json()
    code = data.get('code', '')
    user_input = data.get('input', '')
    
    output, error = run_code(code, user_input)
    
    return jsonify({
        "success": True,
        "output": output,
        "error": error,
        "has_error": bool(error)
    })

@app.route('/submit_solution', methods=['POST'])
def submit_solution():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.get_json()
    problem_id = data.get('problem_id')
    code = data.get('code')
    
    if not code or len(code.strip()) < 20:
        return jsonify({"error": "Code too short"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO submissions (user_id, problem_id, code) VALUES (?, ?, ?)",
                  (session['user_id'], problem_id, code))
    
    cursor.execute("SELECT solved_problems, submissions FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    solved = eval(user['solved_problems']) if user['solved_problems'] else []
    
    if problem_id not in solved:
        solved.append(problem_id)
        cursor.execute("UPDATE users SET solved_problems = ?, submissions = ? WHERE id = ?",
                      (str(solved), user['submissions'] + 1, session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Solution submitted!"})

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, solved_problems, submissions FROM users")
    users = cursor.fetchall()
    conn.close()
    
    leaderboard_data = []
    for user in users:
        solved = eval(user['solved_problems']) if user['solved_problems'] else []
        leaderboard_data.append({
            'username': user['username'],
            'solved': len(solved),
            'submissions': user['submissions']
        })
    
    leaderboard_data.sort(key=lambda x: (-x['solved'], x['submissions']))
    
    return render_template('leaderboard.html', 
                         leaderboard=leaderboard_data,
                         username=session['username'],
                         now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT solved_problems FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    solved_ids = eval(user['solved_problems']) if user['solved_problems'] else []
    
    solved_list = []
    for pid in solved_ids:
        problem = PROBLEMS.get(pid, {})
        solved_list.append({
            'id': pid,
            'title': problem.get('title', f'Problem {pid}'),
            'difficulty': problem.get('difficulty', 'Unknown')
        })
    
    easy_solved = sum(1 for pid in solved_ids if PROBLEMS.get(pid, {}).get('difficulty') == 'Easy')
    medium_solved = sum(1 for pid in solved_ids if PROBLEMS.get(pid, {}).get('difficulty') == 'Medium')
    hard_solved = sum(1 for pid in solved_ids if PROBLEMS.get(pid, {}).get('difficulty') == 'Hard')
    
    easy_total = sum(1 for p in PROBLEMS.values() if p['difficulty'] == 'Easy')
    medium_total = sum(1 for p in PROBLEMS.values() if p['difficulty'] == 'Medium')
    hard_total = sum(1 for p in PROBLEMS.values() if p['difficulty'] == 'Hard')
    
    return render_template('progress.html',
                         username=session['username'],
                         solved_count=len(solved_ids),
                         solved_list=solved_list,
                         easy_solved=easy_solved,
                         easy_total=easy_total,
                         medium_solved=medium_solved,
                         medium_total=medium_total,
                         hard_solved=hard_solved,
                         hard_total=hard_total)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)