import json
import re
from bs4 import BeautifulSoup
import html

def clean_html(text):
    # Convert HTML entities
    text = html.unescape(text)
    
    # Parse with BeautifulSoup to handle HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    
    # Get text content
    text = soup.get_text()
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def format_thread_to_markdown(thread):
    markdown = []
    
    # Add thread title and question
    markdown.append(f"# {thread['threadTitle']}\n")
    markdown.append(clean_html(thread['question']) + "\n")
    
    # Add responses
    markdown.append("## Responses\n")
    for response in thread['responses']:
        markdown.append(f"### {response['author']}")
        markdown.append(f"*Posted: {response['timestamp']}*\n")
        
        # Clean and add content
        content = clean_html(response['content'])
        markdown.append(content + "\n")
        
        # Add attachments if any
        if response['attachments']:
            markdown.append("\n**Attachments:**")
            for attachment in response['attachments']:
                markdown.append(f"- [{attachment['filename']}]({attachment['url']})")
        markdown.append("\n---\n")
    
    return "\n".join(markdown)

def main():
    # Read the JSON file
    with open('Section1/forum_threads.json', 'r') as f:
        threads = json.load(f)
    
    # Process each thread and write to markdown file
    with open('forum_clean.md', 'w') as f:
        for thread in threads:
            markdown = format_thread_to_markdown(thread)
            f.write(markdown)
            f.write("\n\n")

if __name__ == "__main__":
    main() 