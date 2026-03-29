import json
from openai import AzureOpenAI
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT


def get_client():
    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-02-01"
    )


def optimize(parsed: dict, product_name: str, category: str, brand_name: str) -> dict:
    """
    Cafe24 전용 — 파싱된 HTML 정보 → SEO/GEO 최적화 수정안 생성.
    """
    client = get_client()

    headings_text = "\n".join([f"{h['level']}: {h['text']}" for h in parsed["headings"]])
    images_text = "\n".join([
        f"- src: {i['src'][:60]} | 현재 alt: '{i['alt']}'"
        for i in parsed["images"][:10]
    ])

    prompt = f"""
당신은 한국 이커머스 SEO/GEO 전문가입니다.
아래 상세페이지 정보를 분석하고, 최적화된 수정안을 JSON으로 생성하세요.

[상품 정보]
- 브랜드: {brand_name}
- 상품명: {product_name}
- 카테고리: {category}

[현재 HTML 분석 결과]
- 현재 title: {parsed['title'] or '없음'}
- 현재 meta description: {parsed['meta_description'] or '없음'}
- 현재 heading 구조:
{headings_text or '없음'}
- 이미지 목록 (상위 10개):
{images_text or '없음'}
- 본문 텍스트 샘플:
{parsed['body_text'][:500]}

아래 JSON 형식으로만 응답하세요.

{{
  "title": "최적화된 title (60자 이내, 핵심 키워드 앞 배치)",
  "meta_description": "최적화된 meta description (160자 이내, 구매 유도 포함)",
  "h1": "최적화된 h1 텍스트 제안 (1개만)",
  "og": {{
    "og:title": "SNS 공유용 제목",
    "og:description": "SNS 공유용 설명 (100자 이내)",
    "og:type": "product"
  }},
  "alt_texts": [
    {{"src_keyword": "이미지 src 일부", "alt": "최적화된 alt 텍스트"}}
  ],
  "json_ld": {{
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "상품명",
    "brand": {{"@type": "Brand", "name": "브랜드명"}},
    "description": "AI 검색 최적화 상품 설명 (3~4문장)",
    "category": "카테고리"
  }},
  "geo_content": "ChatGPT·Gemini가 참조하기 좋은 자연어 상품 설명 (3~4문장)"
}}

규칙:
- title은 [주요키워드] 브랜드명 형식 권장
- alt_texts는 alt가 없거나 빈 이미지 위주로 생성
- json_ld description과 geo_content는 AI 검색엔진이 자연스럽게 인용할 수 있는 문체
- 한국어 기준 작성
"""

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else parts[0]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"GPT 응답을 JSON으로 파싱할 수 없어요: {e}\n\n응답 내용:\n{raw[:300]}")


def optimize_smartstore(product_name: str, category: str, brand_name: str, product_desc: str) -> dict:
    """
    스마트스토어 전용 — 상품명 + 태그 10개 + 상품 설명 최적화.
    """
    client = get_client()

    prompt = f"""
당신은 네이버 스마트스토어 SEO 전문가입니다.

[상품 정보]
- 브랜드: {brand_name}
- 현재 상품명: {product_name}
- 카테고리: {category}
- 상품 설명: {product_desc or '없음'}

아래 JSON 형식으로만 응답하세요.

{{
  "optimized_name": "최적화된 상품명 (100자 이내, 핵심 검색 키워드 앞 배치, 브랜드명 포함)",
  "tags": ["태그1", "태그2", "태그3", "태그4", "태그5", "태그6", "태그7", "태그8", "태그9", "태그10"],
  "description": "스마트스토어 상품 설명 (500자 이내, 구매 유도 + 키워드 자연스럽게 포함)",
  "search_keywords": ["네이버 검색 핵심 키워드 5개"],
  "geo_content": "AI 검색 최적화용 자연어 설명 (ChatGPT·Gemini가 참조하기 좋은 2~3문장)"
}}

규칙:
- 상품명은 [카테고리 키워드] + [특징] + [브랜드] 순서 권장
- 태그는 10개 정확히, 검색량 높은 키워드 위주
- 태그에 # 기호 넣지 말 것
- 네이버 쇼핑 검색 알고리즘에 최적화된 키워드 선택
"""

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=1500,
    )

    raw = response.choices[0].message.content.strip()
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else parts[0]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"GPT 응답을 JSON으로 파싱할 수 없어요: {e}\n\n응답 내용:\n{raw[:300]}")