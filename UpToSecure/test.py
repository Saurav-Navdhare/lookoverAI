import requests
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
# from google_serp_api import ScrapeitCloudClient
from serpapi import GoogleSearch
import re

trusted_websites=[
"https://www.bankinfosecurity.co.uk/",
"https://www.bleepingcomputer.com/news/security/",
"https://www.csoonline.com/",
"https://www.cyberdefensemagazine.com/",
"https://www.cybersecurity-insiders.com/",
"https://cybermagazine.com/",
"https://www.darkreading.com/",
"https://www.govinfosecurity.com/",
"https://gbhackers.com/",
"https://grahamcluley.com/",
"https://www.hackread.com/",
"Blog.cyble.com",
"https://redcanary.com/blog/",
"https://www.microsoft.com/en-us/security/blog/topic/threat-intelligence/",
"https://blog.checkpoint.com/",
"https://research.checkpoint.com/",
"https://thehackernews.com/",
"https://www.malwarebytes.com/blog",
"https://cybersecurity.att.com/blogs/security-essentials",
"https://www.trustedsec.com/blog/",
"https://cybersecurity.att.com/blogs",
"https://www.scmagazine.com/security-weekly",
"https://cyberstrategies.wordpress.com/",
"https://www.bellingcat.com/",
"https://www.microsoft.com/en-us/security/blog/",
"https://krebsonsecurity.com/",
"https://www.crowdstrike.com/blog/",
"https://blog.shodan.io/",
"https://thecyberexpress.com/"
]

load_dotenv()

# SerpAPI configuration
serpapi_key = os.getenv("SERPAPI_API_KEY")
search_engine = "google"  # Or another search engine of your choice

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

def scrape_article_content(url):
    # Send an HTTP GET request to the URL
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the content of the article based on the HTML structure
        article_content = soup.find('div', class_='article-content') + soup.find("div", class_='articleBody')  # Adjust based on your website's structure
        
        # Extract the text from the HTML tags
        if article_content:
            article_text = article_content.get_text()
            print(article_text)
            return article_text
        else:
            return "Content not found"
    else:
        return "Failed to retrieve content"

def search_websites(topic):
    relevant_articles = []
    params = {
        "q": topic,
        "location": "Mumbai, Maharashtra, India",
        "hl": "en",
        "gl": "in",
        "google_domain": "google.com",
        "api_key": serpapi_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    for result in results['organic_results']:
        article = {
            'title': result['title'],
            'link': result['link'],
            'published_date': result.get('published_date', '')  # Adjust key if needed
        }
        # add in relevant articles if they are from trusted websites
        for website in trusted_websites:
            if re.search(website, article['link']):
                relevant_articles.append(article)
    sorted_articles = sorted(relevant_articles, key=lambda x: x['published_date'], reverse=True)
    # return sorted_articles
    return relevant_articles


def generate_conclusion(prompt, content):
    # Combine the content with the prompt
    combined_prompt = f"{prompt}\n\n{content}"
    
    # Generate a conclusion using LangChain
    generated_text = openai.Completion.create(
        engine="text-davinci-003",  # Or another engine of your choice
        prompt=combined_prompt,
        max_tokens=150  # Adjust as needed
    )
    
    conclusion = generated_text.choices[0].text.strip()
    return conclusion

def scrape_article_content(url):
    # Send an HTTP GET request to the URL
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the content of the article based on the HTML structure
        article_content = soup.find('div', class_='article-content')  # Adjust based on your website's structure
        
        # Extract the text from the HTML tags
        if article_content:
            article_text = article_content.get_text()
            return article_text
        else:
            return "Content not found"
    else:
        return "Failed to retrieve content"

def main():
    topic = input("Enter the topic you want to search: ")
    prompt = input("Enter your initial prompt: ")
    
    # Search relevant websites and sort by publishing date
    sorted_articles = search_websites(topic)
    
    # Fetch content from the websites (you might need to use a web scraping library)
    content = ""
    for article in sorted_articles:
        article_url = article['link']
        article_text = scrape_article_content(article_url)
        content += article_text + "\n\n"
    # for article in sorted_articles:
        # Fetch content from the article['link'] and add it to the content variable
        
    # Generate a conclusion using LangChain
    generated_conclusion = generate_conclusion(prompt, content)
    
    print("Modified Prompt:", prompt)
    print("Generated Conclusion:", generated_conclusion)

if __name__ == "__main__":
    main()
