import json
import requests
from openai import OpenAI
import streamlit as st
import re


def parse_ideas(post_ideas_content):
    ideas = []
    idea_parts = post_ideas_content.split("\n\n")  # Розділити на окремі ідеї

    for part in idea_parts:
        ideas.append(part)

    return ideas


def analyze_trends_and_generate_post_idea_gpt(articles, openai_api_key):
    client = OpenAI(api_key=openai_api_key)

    article_details = "\n".join([f"Title: {article['title']}\nURL: {article['url']}" for article in articles])
    instructions = """
    Ви - креативний письменник, який розробляє ідеї для постів у соціальних медіа українською мовою. Ваша компанія спеціалізується на аутсорсингу та впровадженні штучного інтелекту для автоматизації процесів у різних організаціях. Проаналізуйте наступні новини про ШІ та, виходячи з цього, створіть ідеї постів. Кожна ідея має бути цікавою, інформативною та актуальною для аудиторії, яка цікавиться штучним інтелектом та його застосуванням у бізнесі.

    Форматуйте кожну ідею у JSON з наступними полями:
    1) "title": "Назва ідеї",
    2) "content": "Суть ідеї (50-80 слів), з акцентом на те, як штучний інтелект може трансформувати бізнес та оптимізувати процеси",
    3) "inform": "Інформаційний привід",
    4) "links": "URL новини"

    Наприклад:
    {
      "title": "Назва ідеї тут",
      "content": "Текст суті ідеї тут...",
      "inform": "Інформаційний привід тут...",
      "links": "https://example.com/link-to-news-article"
    }

    Будь ласка, створіть 3 ідеї за цим форматом.
    """

    prompt = f"{instructions}\n\nNews Articles:\n{article_details}\n\nGenerate three post ideas:"

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Generate the ideas."}
            ],
            max_tokens=1500,
            temperature=0.5
        )

        print("Відповідь від OpenAI API:")
        print(response.choices[0].message.content)

        if response.choices and response.choices[0].message.content:
            ideas = parse_ideas(response.choices[0].message.content)

            # Запис ідей у JSON файл
            with open('post_ideas.json', 'w', encoding='utf-8') as f:
                json.dump(ideas, f, ensure_ascii=False, indent=4)
                print("Ідеї для постів збережено у JSON файл.")

            return ideas
        else:
            print("Помилка: Відповідь від OpenAI API не містить змістовної інформації.")
            return []

    except Exception as e:
        print(f"Error in GPT-4 post idea generation: {e}")
        return []

def get_news_articles(news_api_key, search_queries=["AI", "Artificial Itelligence", "Technology"]):
    api_url = "https://newsapi.org/v2/top-headlines"
    all_results = []
    for query in search_queries:
        params = {
            "q": query,
            "from": "2023-12-02",
            "to": "2023-12-05",
            "sortBy": "popularity",
            "page": 1,
            "apiKey": news_api_key
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            news_data = response.json()
            all_results.extend(news_data.get("articles", []))
        else:
            print(f"Error fetching news for '{query}': {response.status_code}")
            pass

    return all_results

def main():
    openai_api_key = "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"
    news_api_key = "4c5096179734485aba9279b5a9183788"

    st.title("Iдеї по новинам про штучний інтелект")
    text_input = st.text_input("Введіть теми новин які вас цікавлять 👇", placeholder="AI, Artificial Itelligence, Technology")
    if text_input:
        with st.spinner("Отримання списку новин..."):
            articles = get_news_articles(news_api_key, text_input.split(','))
        if articles:
            for article in articles:
                st.markdown(f'**{article["source"]["name"]}** [{article["title"]}]({article["url"]})')
            st.success(f"Отримано {len(articles)} новин.")
            with st.spinner("Генерація ідей для постів..."):
                post_ideas = analyze_trends_and_generate_post_idea_gpt(articles, openai_api_key)
            st.success(f"Згенеровано {len(post_ideas)} ідеї.")
        else:
            st.success("Немає новин для аналізу.")

        if post_ideas:
            for idx, idea in enumerate(post_ideas, start=1):
                idea_dict = dict(json.loads(idea))
                st.markdown(f"""
                    ### Ідея {idx}\n
                    #### {idea_dict["title"]}\n
                    {idea_dict["content"]}\n
                    {idea_dict["inform"]}
                    {idea_dict["links"]}
                """)
                st.json(idea, expanded=False)

        st.button('Rerun')

if __name__ == "__main__":
    main()
