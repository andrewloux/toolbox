import json
from match_questions import TextCleaner

def test_question_parsing():
    # Load questions
    with open('slido_questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    cleaner = TextCleaner()
    
    # Test first few questions
    print("\nTesting question parsing...")
    for i, question in enumerate(questions[:3]):
        print(f"\n=== Question {i+1} Raw Text ===")
        print(question.get('text', ''))
        print("=" * 50)
        
        print(f"\n=== Question {i+1} Parsed ===")
        question_text, options = cleaner.extract_question_parts(question.get('text', ''))

if __name__ == "__main__":
    test_question_parsing() 