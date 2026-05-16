"""LangChain 기반 뉴스 요약 실행 스크립트."""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.func_llm import run_llm_summary_flow


def main() -> None:
    stock_name = input("요약할 종목명 또는 키워드를 입력해주세요: ").strip()

    if not stock_name:
        raise ValueError("종목명 또는 키워드는 비워둘 수 없습니다.")

    summary_result, saved_path = run_llm_summary_flow(stock_name=stock_name)

    print("\nLLM 요약 완료")
    print(f"종목명: {summary_result['stock_name']}")
    print(f"저장 경로: {saved_path}")
    print("\n요약 결과:")
    print(summary_result["summary"])


if __name__ == "__main__":
    main()
