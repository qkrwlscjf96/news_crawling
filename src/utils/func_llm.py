"""
LangChain 기반 뉴스 요약 유틸리티.

1. ``data/llm_crawl_site.md`` 파일에서 사이트 목록을 읽습니다.
2. 사이트 URL 목록 자체를 종목 기준으로 LLM에 전달합니다.
3. 요약 결과를 ``data/<종목명>.parquet`` 파일로 저장합니다.
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
SITE_LIST_PATH = DATA_DIR / "llm_crawl_site.md"


def load_target_sites(site_file: Path | str = SITE_LIST_PATH) -> list[str]:
    """크롤링 대상 사이트 목록을 읽어 URL 리스트로 반환합니다."""
    site_path = Path(site_file)

    if not site_path.exists():
        raise FileNotFoundError(f"사이트 목록 파일이 없습니다: {site_path}")

    sites: list[str] = []
    with site_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                sites.append(line)

    if not sites:
        raise ValueError(f"사이트 목록이 비어 있습니다: {site_path}")

    return sites


def _get_summary_chain(model_name: str = "gpt-4o-mini", temperature: float = 0):
    """LangChain 요약 체인을 생성합니다."""
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise ImportError(
            "LangChain 실행에 필요한 패키지가 없습니다. "
            "`langchain`, `langchain-openai`를 설치해주세요."
        ) from exc

    prompt = ChatPromptTemplate.from_template(
        """
당신은 한국 주식/경제 뉴스 분석가입니다.
아래 사이트 URL 목록을 참고해 "{stock_name}" 관련 뉴스/정보를 어떤 출처 기준으로 확인해야 할지 한국어로 정리해주세요.

요약 규칙:
- 실제 사이트 본문이 아니라 URL 목록만 전달된 상태라는 점을 반영
- 각 사이트가 어떤 성격의 정보원인지 추정해서 설명
- "{stock_name}"를 조사할 때 어떤 순서로 참고하면 좋을지 정리
- 과장 없이, 확인 가능한 범위만 설명
- 마지막에 "추가 크롤링 필요" 여부를 1문장으로 덧붙이기

사이트 URL 목록:
{site_list}
"""
    )

    llm = ChatOpenAI(model=model_name, temperature=temperature)
    return prompt | llm | StrOutputParser()


def summarize_stock_news(
    stock_name: str,
    site_urls: list[str] | None = None,
    model_name: str = "gpt-4o-mini",
) -> dict[str, Any]:
    """종목명을 기준으로 사이트 URL 목록을 LLM에 전달하고 요약 결과를 반환합니다."""
    urls = site_urls or load_target_sites()
    site_list = "\n".join(f"- {url}" for url in urls)

    chain = _get_summary_chain(model_name=model_name)
    summary = chain.invoke(
        {
            "stock_name": stock_name,
            "site_list": site_list,
        }
    )

    return {
        "stock_name": stock_name,
        "summary": summary.strip(),
        "source_urls": urls,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def save_summary_to_parquet(
    summary_result: dict[str, Any],
    output_dir: Path | str = DATA_DIR,
) -> Path:
    """요약 결과를 parquet 파일로 저장하고 경로를 반환합니다."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^\w\-가-힣]+", "_", summary_result["stock_name"]).strip("_")
    output_path = destination / f"{safe_name}.parquet"

    dataframe = pd.DataFrame([summary_result])
    dataframe.to_parquet(output_path, index=False)

    return output_path


def run_llm_summary_flow(stock_name: str, model_name: str = "gpt-4o-mini") -> tuple[dict[str, Any], Path]:
    """사이트 로드부터 요약 저장까지 한 번에 실행합니다."""
    summary_result = summarize_stock_news(stock_name=stock_name, model_name=model_name)
    saved_path = save_summary_to_parquet(summary_result)
    return summary_result, saved_path
