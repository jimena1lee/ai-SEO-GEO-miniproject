import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Cafe24 상세이미지 영역 클래스명 후보들 (쇼핑몰마다 다를 수 있음)
CAFE24_DETAIL_SELECTORS = [
    "detail-img-area",
    "productDetail",
    "product-detail",
    "goods_description",
    "detail_content",
    "prdDetail",
    "product_detail",
    "cont-product-detail",
]

def fetch_html_from_url(url: str) -> tuple[str, str]:
    """
    URL → HTML 소스 크롤링.
    반환값: (html_str, 에러메시지 or "")
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text, ""
    except requests.exceptions.Timeout:
        return "", "요청 시간이 초과됐어요. URL을 확인해주세요."
    except requests.exceptions.HTTPError as e:
        return "", f"HTTP 오류: {e.response.status_code}"
    except Exception as e:
        return "", f"크롤링 실패: {str(e)}"


def parse_html(raw_html: str) -> dict:
    soup = BeautifulSoup(raw_html, "html.parser")

    # 기존 title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # 기존 meta description
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag.get("content", "") if meta_desc_tag else ""

    # 기존 Open Graph 태그
    og_tags = {}
    for og in soup.find_all("meta", property=lambda x: x and x.startswith("og:")):
        og_tags[og.get("property")] = og.get("content", "")

    # heading 구조
    headings = []
    for level in ["h1", "h2", "h3"]:
        for tag in soup.find_all(level):
            text = tag.get_text(strip=True)
            if text:
                headings.append({"level": level, "text": text})

    # 전체 이미지
    images = []
    for img in soup.find_all("img"):
        images.append({
            "src": img.get("src", ""),
            "alt": img.get("alt", ""),
            "has_alt": bool(img.get("alt", "").strip())
        })

    # Cafe24 상세이미지 영역 특화 파싱
    detail_area = None
    detail_area_class = None
    for selector in CAFE24_DETAIL_SELECTORS:
        found = soup.find(class_=selector)
        if found:
            detail_area = found
            detail_area_class = selector
            break

    detail_images = []
    if detail_area:
        for img in detail_area.find_all("img"):
            detail_images.append({
                "src": img.get("src", ""),
                "alt": img.get("alt", ""),
                "has_alt": bool(img.get("alt", "").strip())
            })

    # 본문 텍스트
    body = soup.find("body")
    body_text = body.get_text(separator=" ", strip=True)[:1000] if body else ""

    return {
        "title": title,
        "meta_description": meta_description,
        "og_tags": og_tags,
        "headings": headings,
        "images": images,
        "images_without_alt": [i for i in images if not i["has_alt"]],
        "body_text": body_text,
        # Cafe24 특화
        "detail_area_found": detail_area is not None,
        "detail_area_class": detail_area_class,
        "detail_images": detail_images,
        "detail_images_without_alt": [i for i in detail_images if not i["has_alt"]],
    }