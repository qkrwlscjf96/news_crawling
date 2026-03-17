import torch
import os
import warnings
from transformers import pipeline

# 경고 메시지 억제
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
warnings.filterwarnings('ignore')

import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)


# 감정 분석 함수
def sentiment_analysis(texts):
    """
    한국어 감정분석을 수행합니다.
    
    Args:
        texts: 분석할 텍스트 또는 텍스트 리스트
        
    Returns:
        리스트 형태로 각 텍스트의 감정 결과 반환
    """
    # GPU 사용 가능 여부 확인
    device = 0 if torch.cuda.is_available() else -1
    
    # 한국어 감정분석 파이프라인 로드
    nlp = pipeline(
        "sentiment-analysis",
        model="nlptown/bert-base-multilingual-uncased-sentiment",
        device=device
    )
    
    # 리스트가 아니면 리스트로 변환
    if isinstance(texts, str):
        texts = [texts]
    
    results = []
    
    for text in texts:
        try:
            # 텍스트가 너무 길면 잘라내기
            text = text[:512]
            
            # 감정 분석 수행
            result = nlp(text)[0]
            label = result['label']
            score = result['score']
            
            # 긍정/부정 판단
            if label in ['positive', '5 stars', '4 stars']:
                sentiment = '긍정'
                positive_score = score
                negative_score = 1 - score
            else:
                sentiment = '부정'
                positive_score = 1 - score
                negative_score = score
            
            results.append({
                'negative': round(negative_score, 4),
                'positive': round(positive_score, 4),
                'sentiment': sentiment
            })
        except Exception as e:
            # 에러 발생 시 중립으로 처리
            results.append({
                'negative': 0.5,
                'positive': 0.5,
                'sentiment': '중립'
            })
    
    return results
