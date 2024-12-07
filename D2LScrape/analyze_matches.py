import json
from pprint import pprint

def analyze_matches():
    # Load results
    with open('question_matches.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Look at top 3 highest confidence matches
    print("\nTop 3 highest confidence matches:")
    for match in sorted(results['matches'], key=lambda x: x['confidence_score'], reverse=True)[:3]:
        print("\nConfidence:", match['confidence_score'])
        print("Question:", match['question'])
        print("Weeks:", match['weeks'])
        if 'explanation' in match:
            print("\nExplanation excerpt:")
            print(match['explanation'][:200] + "..." if len(match['explanation']) > 200 else match['explanation'])
        print("-" * 80)
    
    # Look at some unmatched questions
    print("\nSample of unmatched questions:")
    for q in results['unmatched'][:3]:
        print("\nQuestion:", q['question'])
        print("Best score:", q['best_score'])
        print("-" * 80)

if __name__ == "__main__":
    analyze_matches() 