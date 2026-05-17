# 프로젝트 개요

- 주식 종목별 호재/악재 판단에 도움이 될 수 있도록 개발 중
- 네이버 뉴스 검색 결과를 기반으로 기사 제목을 수집하고 감성 분석을 수행하는 파이프라인
- 지정된 뉴스 사이트 목록을 바탕으로 LLM 요약 결과를 생성하고 저장하는 파이프라인

## 데이터

- 네이버 뉴스 검색어 기반 기사 제목을 크롤링 후 텍스트 전처리
- 뉴스 기사 사이트 정리 후 LLM 기반 summary

## 모델

- BERT 오픈 소스 기반 긍/부정 감성 분석 pre-trained 모델 활용 후 추가 최적화
- MLflow를 활용하여 다양한 모델 실험 및 성능 비교를 수행하고, 뉴스 데이터에 최적화된 감성 분석 모델 선정
- Apache Airflow를 통해 모델 재학습 및 배포를 자동화하는 배치 파이프라인 구성


## 현재 구현된 기능

### 1. 뉴스 크롤링 + 감성 분석

`src/main_crawl.py`는 아래 작업을 수행합니다.

- 검색 키워드 입력
- 네이버 뉴스 검색 결과 페이지 범위 입력
- 기사 제목과 링크 수집
- 중복 제거
- 기사 제목 기반 감성 분석 수행
- 워드클라우드 시각화

감성 분석은 `src/utils/func_model.py`에서 `transformers` 파이프라인을 이용해 처리합니다.

### 2. LLM 기반 뉴스 요약

`src/main_llm.py`는 아래 작업을 수행합니다.

- 종목명 또는 키워드 입력
- `data/llm_crawl_site.md`의 사이트 목록 로드
- LangChain + OpenAI 모델을 사용해 사이트 성격과 조사 우선순위 요약
- 결과를 `data/<종목명>.parquet` 파일로 저장

주의할 점은 현재 이 기능이 실제 뉴스 본문을 직접 크롤링해 요약하는 방식은 아니라는 것입니다.
지금은 "사이트 URL 목록"을 LLM에 전달해 참고 우선순위를 정리하는 형태입니다.

## 프로젝트 구조

```text
news_crawling/
├── README.md
├── data/
│   └── llm_crawl_site.md
└── src/
    ├── main_crawl.py
    ├── main_llm.py
    └── utils/
        ├── func_crawl.py
        ├── func_llm.py
        └── func_model.py
```

## 환경 변수

LLM 요약 기능을 사용하려면 `.env` 또는 셸 환경에 아래 값이 필요합니다.

```bash
OPENAI_API_KEY=your_api_key
```

## 실행 방법

### 1. 뉴스 크롤링 + 감성 분석 실행

프로젝트 루트에서 실행합니다.

```bash
python src/main_crawl.py
```

실행 중 아래 값을 순서대로 입력합니다.

- 검색 키워드
- 시작 페이지 번호
- 종료 페이지 번호

실행 결과

- 기사 제목/링크 수집
- 감성 분석 결과 출력
- 워드클라우드 표시

### 2. LLM 요약 실행

```bash
python src/main_llm.py
```

실행 중 입력값

- 종목명 또는 키워드

실행 결과

- 요약 텍스트 콘솔 출력
- `data/<종목명>.parquet` 파일 저장

## 데이터 파일

### `data/llm_crawl_site.md`

LLM 요약 시 참고할 사이트 목록 파일입니다.
한 줄에 하나씩 URL을 작성하면 됩니다.

예시:

```text
https://kr.investing.com/news/stock-market-news
https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=401
```
