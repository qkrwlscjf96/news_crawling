
from bs4 import BeautifulSoup
import requests

# 페이지 url 형식에 맞게 바꾸어 주는 함수 만들기
  #입력된 수를 1, 11, 21, 31 ...만들어 주는 함수
def makePgNum(num):
    if num == 1:
        return num
    elif num == 0:
        return num+1
    else:
        return num+9*(num-1)

# 크롤링할 url 생성하는 함수 만들기(검색어, 크롤링 시작 페이지, 크롤링 종료 페이지)
def makeUrl(search, start_pg, end_pg):
    if start_pg == end_pg:
        start_page = makePgNum(start_pg)
        url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(start_page)
        print("생성url: ", url)
        return url
    else:
        urls = []
        for i in range(start_pg, end_pg + 1):
            page = makePgNum(i)
            url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(page)
            urls.append(url)
            
        for url in urls:
            print(url)
            
        return urls    


# html에서 원하는 속성 추출하는 함수 만들기 (기사, 추출하려는 속성값)
def articles_crawler(url,headers):
    #html 불러오기
    original_html = requests.get(url,headers)
    html = BeautifulSoup(original_html.text, "html.parser")

    #원하는 속성 추출
    html_attributes = html.select('a[data-heatmap-target=".tit"]')
    
    
    # urls에 추출한 속성값 담기 (href = 링크)
    news_urls=[]
    for html_attribute in html_attributes:
        news_urls.append(html_attribute.attrs['href'])
    
    # title에 추출한 속성값 담기 (text = 제목)
    news_titles = []
    for html_attribute in html_attributes:
        news_titles.append(html_attribute.text)

    return news_urls, news_titles