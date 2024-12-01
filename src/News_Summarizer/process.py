from src.News_Summarizer.model_load import tokenizer
import re
import requests
from bs4 import BeautifulSoup

def summarizeTextP(text, model):
    whitespace_handler = lambda k: re.sub(r'\s+', ' ', re.sub(r'\n+', ' ', k.strip()))
    text_encoding = tokenizer(
        whitespace_handler(text),
        max_length=400,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt'
    )
    generated_ids = model.model.generate(
        input_ids=text_encoding['input_ids'],
        attention_mask=text_encoding['attention_mask'],
        max_length=100,
        num_beams=4,
        no_repeat_ngram_size=2,
        length_penalty=1.0,
        early_stopping=True
    )

    preds = [
        tokenizer.decode(gen_id, skip_special_tokens=True, clean_up_tokenization_spaces=False)
        for gen_id in generated_ids
    ]
    return "".join(preds)




def scrape_article(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # This can vary depending on the website structure
        article_text = ' '.join([p.text for p in soup.find_all('p')])
        return article_text
    else:
        return "Could not scrape article, Please use below feature to summarize text"
