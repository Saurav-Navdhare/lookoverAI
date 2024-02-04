from GetNewsArticle import getNewsArticle
from GetNewsArticleURLS import getNewsArticleURLS
from summarizer import summarizer

query = input("Enter a Query: ")

URLS = getNewsArticleURLS(query)

Links = list(filter(lambda x: (x is not None and len(x.split())), [getNewsArticle(article["link"]) for article in URLS]))[:10]

Summarized = "\n\n-----------\n\n".join(Links)
print(f"Number of articles: {len(Links)}")

print(Summarized)