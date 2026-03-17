import sys
import os

from pyparsing import col
ROOT = os.path.dirname(os.path.abspath(__file__))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

#TODO 날짜랑 / 컨텐츠도 추가
#TODO : 불용어 제거

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from utils.func_crawl import *
from utils.func_model import sentiment_analysis

if __name__ == "__main__":

    # ConnectionError방지
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

    #검색어 입력
    search = input("검색할 키워드를 입력해주세요:")
    
    #검색 시작할 페이지 입력
    page = int(input("\n크롤링할 시작 페이지를 입력해주세요. ex)1(숫자만입력):")) # ex)1 =1페이지,2=2페이지...
    print("\n크롤링할 시작 페이지: ",page,"페이지")   
    #검색 종료할 페이지 입력
    page2 = int(input("\n크롤링할 종료 페이지를 입력해주세요. ex)1(숫자만입력):")) # ex)1 =1페이지,2=2페이지...
    print("\n크롤링할 종료 페이지: ",page2,"페이지")   

    # naver url 생성
    url_list = makeUrl(search,page,page2)

    #뉴스 크롤러 실행
    news_titles = []
    news_urls =[]

    for url in url_list:
        news_urls, news_titles = articles_crawler(url,headers)
        news_urls.extend(news_urls)
        news_titles.extend(news_titles)

    #데이터 프레임 만들기
    news_df = pd.DataFrame({'title':news_titles,'link':news_urls})

    #중복 행 지우기
    news_df = news_df.drop_duplicates(keep='first',ignore_index=True)
    print("뉴스 개수: ",news_df.shape[0])
    
    # 불용어 제거
    news_df["title"] = news_df["title"].str.replace(search, "", regex=False) #검색어 제거
    
    # KoBERT 감정 분석 (긍정/부정 예측)
    print("\n감정 분석 중...")
    sentiment_results = sentiment_analysis(news_df["title"].tolist())
    
    # 감정 분석 결과를 데이터프레임에 추가
    news_df["positive_score"] = [result['positive'] for result in sentiment_results]
    news_df["negative_score"] = [result['negative'] for result in sentiment_results]
    news_df["sentiment"] = [result['sentiment'] for result in sentiment_results]
    
    print("\n감정 분석 완료!")
    print(f"긍정: {(news_df['sentiment'] == '긍정').sum()}개")
    print(f"부정: {(news_df['sentiment'] == '부정').sum()}개")
    print(news_df[['title', 'sentiment', 'positive_score', 'negative_score']])

    #wordcloud 만들기
    text = " ".join(news_df["title"].dropna())

    
    wc = WordCloud(
        font_path="malgun.ttf",   # 한글 폰트 (Windows)
        width=800,
        height=400,
        background_color="white"
    ).generate(text)

    plt.imshow(wc)
    plt.axis("off")
    plt.show()