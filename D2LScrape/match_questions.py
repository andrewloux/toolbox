import json
import re
from typing import Dict, List, Optional, Tuple, Set
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

class TextCleaner:
    """Handles text cleaning and preprocessing"""
    
    def __init__(self):
        # Only remove control text at the very end
        self.cleanup_patterns = [
            (r'^poll\n', ''),  # Remove 'poll' prefix at start
            (r'\nSend\nVoting.*$', ''),  # Remove voting info at end
            (r'\nAcceptable Use.*$', ''),  # Remove acceptable use at end
            (r'\n\nNote: You can have multiple answers.', ''),  # Remove note about multiple answers
        ]
        
    def clean_text(self, text: str) -> str:
        """Clean up text using defined patterns"""
        if not text:
            return ""
        cleaned = text
        for pattern, replacement in self.cleanup_patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE | re.DOTALL)
        return cleaned.strip()
    
    def extract_question_parts(self, full_text: str) -> Tuple[str, List[str]]:
        """Extract question text and options from full text"""
        if not full_text:
            return "", []
            
        # First clean the text
        cleaned = self.clean_text(full_text)
        
        # Split into lines and filter empty lines
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        if not lines:
            return "", []
        
        # First line that's not a number is the question
        question = ""
        option_start = 0
        for i, line in enumerate(lines):
            if not re.match(r'^\d+\s*$', line):
                question = line
                option_start = i + 1
                break
        
        # Find where options start (after "Results are hidden")
        for i in range(option_start, len(lines)):
            if lines[i].lower() == "results are hidden":
                option_start = i + 1
                break
        
        # Collect options until control text
        options = []
        for line in lines[option_start:]:
            if (not re.match(r'^\d+\s*$', line) and  # Skip standalone numbers
                not line.lower().startswith('send') and
                not line.lower().startswith('voting') and
                not line.lower().startswith('note:') and
                not line.lower() == 'results are hidden' and
                not line.lower().startswith('acceptable')):
                options.append(line)
        
        # Debug output
        print("\nExtracted question:", question)
        print("Extracted options:", options)
        
        return question, options

class WeekExtractor:
    """Handles extraction of week numbers from text"""
    
    def __init__(self):
        self.week_pattern = re.compile(r'Weeks?\s*(\d+)(?:\s*&\s*(\d+))?')
        self.module_pattern = re.compile(r'(?:in|the)\s+(?:Week|Weeks)\s*(\d+)(?:\s*&\s*(\d+))?\s*Module', re.IGNORECASE)
    
    def extract_weeks(self, text: str) -> Set[int]:
        """Extract week numbers from text, handling combined weeks"""
        if not text:
            return set()
        
        weeks = set()
        
        # Look for explicit week mentions
        for pattern in [self.week_pattern, self.module_pattern]:
            matches = pattern.finditer(text)
            for match in matches:
                weeks.add(int(match.group(1)))
                if match.group(2):  # Combined weeks (e.g., "Weeks 3 & 4")
                    start_week = int(match.group(1))
                    end_week = int(match.group(2))
                    weeks.update(range(start_week, end_week + 1))
        
        return weeks

class SimilarityAnalyzer:
    """Handles different types of similarity analysis"""
    
    def __init__(self):
        print("Loading semantic model (this may take a moment to download if it's the first time)...")
        try:
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./.model_cache')
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
        
    def string_similarity(self, text1: str, text2: str) -> float:
        """Calculate string similarity using SequenceMatcher"""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        if not text1 or not text2:
            return 0.0
        embeddings = self.semantic_model.encode([text1, text2])
        return float(np.dot(embeddings[0], embeddings[1]) / 
                    (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])))
    
    def combined_similarity(self, text1: str, text2: str) -> float:
        """Combine string and semantic similarity"""
        string_sim = self.string_similarity(text1, text2)
        semantic_sim = self.semantic_similarity(text1, text2)
        return (string_sim * 0.3) + (semantic_sim * 0.7)  # Weight semantic similarity higher

class ExplanationParser:
    """Handles parsing of explanation content into individual answers"""
    
    def __init__(self):
        self.question_pattern = re.compile(r'Question (\d+) - ([A-Za-z]+) (\d+)\n(.*?)(?=Question \d+|\Z)', re.DOTALL)
        
    def parse_explanation_content(self, content: str) -> List[Dict[str, str]]:
        """Parse explanation content into individual answers with metadata"""
        if not content:
            return []
            
        answers = []
        matches = self.question_pattern.finditer(content)
        
        for match in matches:
            answer = {
                'question_number': int(match.group(1)),
                'month': match.group(2),
                'day': int(match.group(3)),
                'explanation': match.group(4).strip()
            }
            answers.append(answer)
            
        return answers

class QuestionMatcher:
    def __init__(self):
        self.questions = []
        self.explanations = []
        self.matches = []
        self.unmatched_questions = []
        self.all_parsed_answers = []  # New: store all parsed answers
        
        # Initialize components
        self.text_cleaner = TextCleaner()
        self.week_extractor = WeekExtractor()
        self.similarity_analyzer = SimilarityAnalyzer()
        self.explanation_parser = ExplanationParser()
    
    def load_data(self, questions_file: str, explanations_file: str):
        """Load data from both JSON files and parse all answers"""
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
            with open(explanations_file, 'r', encoding='utf-8') as f:
                self.explanations = json.load(f)
                
            # Parse all explanations into individual answers upfront
            print("Parsing all explanations into individual answers...")
            for explanation in self.explanations:
                answers = self.explanation_parser.parse_explanation_content(explanation.get('content', ''))
                for answer in answers:
                    answer['section_weeks'] = self.week_extractor.extract_weeks(explanation.get('mainSection', ''))
                    answer['section_title'] = explanation.get('mainSection', '')
                self.all_parsed_answers.extend(answers)
                
            print(f"Loaded {len(self.questions)} questions and parsed {len(self.all_parsed_answers)} individual answers")
        except Exception as e:
            print(f"Error loading files: {e}")
            raise
    
    def find_best_answer_match(self, question: str, options: List[str], question_number: Optional[int] = None) -> Tuple[float, str, Set[int]]:
        """Find the best matching answer from all parsed answers"""
        if not question or not self.all_parsed_answers:
            return 0.0, "", set()
        
        best_score = 0.0
        best_explanation = ""
        best_weeks = set()
        
        # Try each parsed answer
        for answer in self.all_parsed_answers:
            explanation_text = answer['explanation']
            
            # Base similarity between question and explanation
            question_similarity = self.similarity_analyzer.combined_similarity(question, explanation_text)
            
            # Calculate option similarities - combine exact and semantic matching
            option_scores = []
            for option in options:
                # Exact match gets highest score
                if option.lower() in explanation_text.lower():
                    option_scores.append(1.0)
                else:
                    # Semantic similarity for non-exact matches
                    option_scores.append(self.similarity_analyzer.combined_similarity(option, explanation_text))
            
            # Combined score (70% question, 30% options)
            option_score = np.mean(option_scores) if option_scores else 0
            score = (question_similarity * 0.7) + (option_score * 0.3)
            
            # Question number boost if available
            if question_number is not None and answer['question_number'] == question_number:
                score *= 1.5  # Restored to original 50% boost
            
            if score > best_score:
                best_score = score
                best_explanation = explanation_text
                best_weeks = answer['section_weeks']
        
        return best_score, best_explanation.strip(), best_weeks
    
    def find_matches(self):
        """Find matches between questions and all parsed answers"""
        print("\nMatching questions to answers...")
        
        matches = []
        unmatched = []
        
        for question_data in tqdm(self.questions):
            # Extract question and options
            question_text, options = self.text_cleaner.extract_question_parts(question_data.get('text', ''))
            if not question_text:
                continue
            
            # Get question number if available
            question_number = None
            number_match = re.search(r'Question\s+(\d+)', question_text)
            if number_match:
                question_number = int(number_match.group(1))
            
            # Get weeks from question context
            context_weeks = self.week_extractor.extract_weeks(question_data.get('contextText', ''))
            question_weeks = self.week_extractor.extract_weeks(question_text)
            
            # Find best matching answer
            score, explanation, answer_weeks = self.find_best_answer_match(
                question_text,
                options,
                question_number
            )
            
            # Week-based confidence boost (restored to original values)
            if context_weeks and context_weeks.intersection(answer_weeks):
                score *= 1.5  # Restored to 50% boost
            elif question_weeks and question_weeks.intersection(answer_weeks):
                score *= 1.3  # Restored to 30% boost
            
            # Record match data
            match_data = {
                'question': question_text,
                'options': options,
                'confidence_score': score,
                'weeks': sorted(list(answer_weeks)) if answer_weeks else [],
                'question_number': question_number
            }
            
            if score >= 0.4:  # Confidence threshold
                match_data['explanation'] = explanation
                matches.append(match_data)
            else:
                match_data['best_score'] = score
                unmatched.append(match_data)
        
        self.matches = matches
        self.unmatched_questions = unmatched
        
        # Print summary statistics
        print(f"\nTotal questions processed: {len(self.questions)}")
        print(f"Questions matched: {len(matches)}")
        print(f"Questions unmatched: {len(unmatched)}")
        
        # Print week distribution
        print("\nMatches by week (total appearances):")
        week_counts = {}
        for match in matches:
            for week in match['weeks']:
                week_counts[week] = week_counts.get(week, 0) + 1
        
        for week in sorted(week_counts.keys()):
            print(f"Week {week}: {week_counts[week]} questions")
        
        # Print unique questions per week
        print("\nUnique questions by week:")
        unique_week_counts = {}
        for match in matches:
            if len(match['weeks']) == 1:  # Only count questions that appear in exactly one week
                week = match['weeks'][0]
                unique_week_counts[week] = unique_week_counts.get(week, 0) + 1
        
        for week in sorted(unique_week_counts.keys()):
            print(f"Week {week}: {unique_week_counts[week]} unique questions")
        
        # Count multi-week questions
        multi_week_count = sum(1 for match in matches if len(match['weeks']) > 1)
        
        # Print confidence distribution
        print("\nConfidence distribution (total {} matches):".format(len(matches)))
        very_high = sum(1 for m in matches if m['confidence_score'] > 0.8)
        high = sum(1 for m in matches if 0.6 < m['confidence_score'] <= 0.8)
        medium = sum(1 for m in matches if 0.5 < m['confidence_score'] <= 0.6)
        low = sum(1 for m in matches if 0.4 <= m['confidence_score'] <= 0.5)
        
        print(f"Very High (>0.8): {very_high} matches")
        print(f"High (0.6-0.8): {high} matches")
        print(f"Medium (0.5-0.6): {medium} matches")
        print(f"Low (0.4-0.5): {low} matches")
    
    def save_results(self, output_file: str):
        """Save matching results to a JSON file"""
        results = {
            'matches': sorted(self.matches, key=lambda x: (-x['confidence_score'], x['weeks'][0] if x['weeks'] else 0)),
            'unmatched': sorted(self.unmatched_questions, key=lambda x: -x['best_score']),
            'statistics': {
                'total_questions': len(self.questions),
                'matched_questions': len(self.matches),
                'unmatched_questions': len(self.unmatched_questions)
            }
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def print_summary(self):
        """Print a summary of matching results"""
        print(f"\nTotal questions processed: {len(self.questions)}")
        print(f"Questions matched: {len(self.matches)}")
        print(f"Questions unmatched: {len(self.unmatched_questions)}")
        
        # Print week distribution
        week_counts = {}
        multi_week_questions = 0
        unique_questions_by_week = {}
        
        for match in self.matches:
            weeks = match.get('weeks', [])
            if len(weeks) > 1:
                multi_week_questions += 1
            
            # Count total appearances
            for week in weeks:
                week_counts[week] = week_counts.get(week, 0) + 1
                
            # Track unique questions
            question = match['question']
            for week in weeks:
                if week not in unique_questions_by_week:
                    unique_questions_by_week[week] = set()
                unique_questions_by_week[week].add(question)
        
        print("\nMatches by week (total appearances):")
        for week in sorted(week_counts.keys()):
            print(f"Week {week}: {week_counts[week]} questions")
            
        print("\nUnique questions by week:")
        for week in sorted(unique_questions_by_week.keys()):
            print(f"Week {week}: {len(unique_questions_by_week[week])} unique questions")
            
        if multi_week_questions:
            print(f"\nNote: {multi_week_questions} questions appear in multiple weeks")
        
        # Print confidence distribution
        confidence_ranges = {
            'Very High (>0.8)': len([m for m in self.matches if m['confidence_score'] > 0.8]),
            'High (0.6-0.8)': len([m for m in self.matches if 0.6 <= m['confidence_score'] <= 0.8]),
            'Medium (0.5-0.6)': len([m for m in self.matches if 0.5 <= m['confidence_score'] < 0.6]),
            'Low (0.4-0.5)': len([m for m in self.matches if 0.4 <= m['confidence_score'] < 0.5])
        }
        
        total_confidence_matches = sum(confidence_ranges.values())
        print(f"\nConfidence distribution (total {total_confidence_matches} matches):")
        for range_name, count in confidence_ranges.items():
            print(f"{range_name}: {count} matches")

if __name__ == "__main__":
    matcher = QuestionMatcher()
    matcher.load_data('slido_questions.json', 'quiz_explanations.json')
    matcher.find_matches()
    matcher.save_results('question_matches.json')
    matcher.print_summary() 