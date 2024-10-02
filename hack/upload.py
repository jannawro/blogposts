import os
import requests
from pathlib import Path
import re

def get_article_title(content):
    for line in content.split('\n'):
        if line.startswith('title:'):
            return line.split(':', 1)[1].strip()
    return None

def article_exists(api_url, headers, title):
    response = requests.get(f"{api_url}/api/articles/title/{title}", headers=headers)
    return response.status_code == 200

def get_existing_article(api_url, headers, title):
    response = requests.get(f"{api_url}/api/articles/title/{title}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def to_slug(title):
    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower().replace(' ', '-')
    # Remove any characters that are not alphanumeric or hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove any duplicate hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug

def process_articles(api_url, api_key):
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    for file in Path('./blogposts').glob('*.md'):
        if file.name == 'TEMPLATE.md':
            continue

        with open(file, 'r') as f:
            content = f.read()

        title = get_article_title(content)
        if not title:
            print(f"Skipping {file.name}: No title found")
            continue

        payload = {
            'article': content
        }

        if article_exists(api_url, headers, title):
            existing_article = get_existing_article(api_url, headers, title)
            if existing_article and existing_article.get('article') != content:
                # Update existing article
                slug = to_slug(title)
                response = requests.put(f"{api_url}/api/articles/{slug}", headers=headers, json=payload)
                if response.status_code == 200:
                    print(f"Successfully updated article: {title}")
                else:
                    print(f"Failed to update article: {title}. Status code: {response.status_code}")
            else:
                print(f"Article {title} exists and content is unchanged. Skipping.")
        else:
            # Create new article
            response = requests.post(f"{api_url}/api/articles", headers=headers, json=payload)
            if response.status_code == 200:
                print(f"Successfully created new article: {title}")
            else:
                print(f"Failed to create article: {title}. Status code: {response.status_code}")

if __name__ == "__main__":
    api_key = os.environ['API_KEY']
    api_url = os.environ['API_URL']
    process_articles(api_url, api_key)
