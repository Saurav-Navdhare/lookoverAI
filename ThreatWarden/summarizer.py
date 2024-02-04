from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain import PromptTemplate
from GetNewsArticle import getNewsArticle
from dotenv import load_dotenv

load_dotenv()


def summarizer(article_url, prompt):
    article = getNewsArticle(article_url)
    article_text = article.text

    if(not article):
        print("Invalid URL")
        exit()

    chat = ChatOpenAI(model_name="gpt-4", temperature=1)

    template = """
    You are an advanced assistant that summarizes different articles into a single text giving best outputs as per required by user

    Here is the article in backticks : 
    `{article_text}`

    Now extract the required information according to the user Prompt in backticks in required format (if any):
    `{prompt}`
    Now give me the information out of this article, neither too short nor to long, just a perfect summary
    """

    promptToLLM = PromptTemplate(template=template, input_variables=["article_text", "prompt"])
    formattedPrompt = promptToLLM.format(article_text=article_text, prompt=prompt)

    messages = [HumanMessage(content=formattedPrompt)]

    response = chat(messages)

    return (response.content)