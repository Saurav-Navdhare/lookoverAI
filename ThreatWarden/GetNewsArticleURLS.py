from dotenv import load_dotenv
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

from serpapi import GoogleSearch
import os

load_dotenv()
serpapi_key = os.getenv("SERPAPI_API_KEY")
search_engine = "google"



def getNewsArticleURLS(query):
    relevant_urls = []
    params = {
        "q": query,
        "tbm": "nws",
        "api_key": serpapi_key,
        "engine": search_engine,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "num": 100,
        "safe": "active"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    for result in results["news_results"]:
        for trusted_website in trusted_websites:
            if trusted_website in result["link"]:
                relevant_urls.append(result)
                break
    return relevant_urls

if __name__ == "__main__":
    query = input("Enter query: ")
    print(getNewsArticleURLS(query))