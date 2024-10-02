import os
import urllib.request
import urllib.error
import urllib.parse
import json
from pathlib import Path
import re

def get_article_title(content):
    for line in content.split('\n'):
        if line.startswith('title:'):
            return line.split(':', 1)[1].strip()
    return None

def extract_markdown_content(content):
    _, markdown_content = content.split('===', 1)
    return markdown_content.strip()

def article_exists(api_url, headers, title):
    encoded_title = urllib.parse.quote(title)
    req = urllib.request.Request(f"{api_url}/api/articles/title/{encoded_title}", headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode() == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise

def get_existing_article(api_url, headers, title):
    encoded_title = urllib.parse.quote(title)
    req = urllib.request.Request(f"{api_url}/api/articles/title/{encoded_title}", headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                return json.loads(response.read().decode())
    except urllib.error.HTTPError:
        pass
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
            content = f.read().replace('\n', '\\n')

        title = get_article_title(content)
        if not title:
            print(f"Skipping {file.name}: No title found")
            continue

        payload = json.dumps({'article': content}).encode('utf-8')

        markdown_content = extract_markdown_content(content)

        if article_exists(api_url, headers, title):
            existing_article = get_existing_article(api_url, headers, title)
            if existing_article and existing_article.get('content').replace('\\n', '\n') != markdown_content:
                # Update existing article
                slug = to_slug(title)
                req = urllib.request.Request(f"{api_url}/api/articles/{slug}", data=payload, headers=headers, method='PUT')
                try:
                    with urllib.request.urlopen(req) as response:
                        if response.getcode() == 200:
                            print(f"Successfully updated article: {title}")
                        else:
                            print(f"Failed to update article: {title}. Status code: {response.getcode()}")
                            print(f"Response content: {response.read().decode()}")
                except urllib.error.HTTPError as e:
                    print(f"Failed to update article: {title}. Status code: {e.code}")
                    print(f"Response content: {e.read().decode()}")
            else:
                print(f"Article {title} exists and content is unchanged. Skipping.")
        else:
            # Create new article
            req = urllib.request.Request(f"{api_url}/api/articles", data=payload, headers=headers, method='POST')
            try:
                with urllib.request.urlopen(req) as response:
                    if response.getcode() == 200:
                        print(f"Successfully created new article: {title}")
                    else:
                        print(f"Failed to create article: {title}. Status code: {response.getcode()}")
                        print(f"Response content: {response.read().decode()}")
            except urllib.error.HTTPError as e:
                print(f"Failed to create article: {title}. Status code: {e.code}")
                print(f"Response content: {e.read().decode()}")

if __name__ == "__main__":
    api_key = os.environ['API_KEY']
    api_url = os.environ['API_URL']
    process_articles(api_url, api_key)
