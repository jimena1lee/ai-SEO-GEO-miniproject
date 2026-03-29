import json
from bs4 import BeautifulSoup


def inject(raw_html: str, optimized: dict, parsed: dict) -> str:
    """
    최적화 수정안을 원본 HTML에 주입.
    반환값: 수정된 HTML 문자열
    """
    soup = BeautifulSoup(raw_html, "lxml")
    head = soup.find("head")
    if not head:
        head = soup.new_tag("head")
        soup.html.insert(0, head)

    # 1. title 수정
    title_tag = soup.find("title")
    if title_tag:
        title_tag.string = optimized["title"]
    else:
        new_title = soup.new_tag("title")
        new_title.string = optimized["title"]
        head.append(new_title)

    # 2. meta description 수정/추가
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        meta_desc["content"] = optimized["meta_description"]
    else:
        new_meta = soup.new_tag("meta")
        new_meta["name"] = "description"
        new_meta["content"] = optimized["meta_description"]
        head.append(new_meta)

    # 3. Open Graph 태그 수정/추가
    for og_property, og_content in optimized.get("og", {}).items():
        og_tag = soup.find("meta", property=og_property)
        if og_tag:
            og_tag["content"] = og_content
        else:
            new_og = soup.new_tag("meta")
            new_og["property"] = og_property
            new_og["content"] = og_content
            head.append(new_og)

    # 4. JSON-LD 구조화 데이터 삽입 (기존 것 제거 후 새로 삽입)
    for old_ld in soup.find_all("script", type="application/ld+json"):
        old_ld.decompose()

    json_ld_tag = soup.new_tag("script")
    json_ld_tag["type"] = "application/ld+json"
    json_ld_tag.string = json.dumps(optimized["json_ld"], ensure_ascii=False, indent=2)
    head.append(json_ld_tag)

    # 5. GEO 설명문 삽입 (body 최상단에 숨김 div로)
    body = soup.find("body")
    if body and optimized.get("geo_content"):
        geo_div = soup.new_tag("div")
        geo_div["id"] = "geo-content"
        geo_div["style"] = "display:none"
        geo_div.string = optimized["geo_content"]
        body.insert(0, geo_div)

    # 6. img alt 태그 추가
    alt_map = {
        item["src_keyword"]: item["alt"]
        for item in optimized.get("alt_texts", [])
    }
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not img.get("alt", "").strip():
            # src에 키워드가 포함된 alt 매핑 시도
            for keyword, alt_text in alt_map.items():
                if keyword in src:
                    img["alt"] = alt_text
                    break
            else:
                # 매핑 안 되면 상품명으로 기본값
                img["alt"] = f"{optimized['title']} 상품 이미지"

    # 7. h1 태그 최적화 (첫 번째 h1만)
    h1_tag = soup.find("h1")
    if h1_tag and optimized.get("h1"):
        h1_tag.string = optimized["h1"]

    return str(soup)