import requests
from newspaper import Article

def getNewsArticle(url):
    # article = Article(url)
    # article.download()
    # article.parse()
    response = requests.get(url, timeout=20)
    if(response.status_code not in range(200, 300)):
        return ""
    try:
        article = Article(url)
        article.download()
        article.parse()
        article = article.text.strip()
    except Exception as e:
        return None
    else:
        return article if len(article) else None

# article1 = getNewsArticle("https://www.safetydetectives.com/blog/most-dangerous-new-malware-and-security-threats/")

# print(article1)