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


    print('news 개수: ',len(news_urls))

    #데이터 프레임 만들기
    news_df = pd.DataFrame({'title':news_titles,'link':news_urls})
    print('news 개수: ',news_df.shape[0])

    #중복 행 지우기
    news_df = news_df.drop_duplicates(keep='first',ignore_index=True)
    print("중복 제거 후 행 개수: ",news_df.shape[0])

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