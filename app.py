import streamlit as st
import pandas as pd
import io
import json
import urllib.parse
from html_parser import parse_html
from seo_optimizer import optimize, optimize_smartstore
from html_injector import inject

st.set_page_config(
    page_title="상세페이지 SEO/GEO 최적화",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 상세페이지 SEO/GEO 자동 최적화")
st.caption("Azure GPT-4o 기반 · Cafe24 HTML 최적화 + 스마트스토어 키워드 최적화")

# 사이드바
with st.sidebar:
    st.header("기본 정보")
    platform = st.radio("플랫폼 선택", ["Cafe24", "스마트스토어"], horizontal=True)
    brand_name = st.text_input("브랜드명", placeholder="예: 리바이브")
    product_name = st.text_input("상품명", placeholder="예: 리프트업 러닝 자켓")
    category = st.selectbox(
        "카테고리",
        ["상의", "하의", "아우터", "원피스", "신발", "가방", "액세서리", "기타"]
    )
    product_url = st.text_input("상품 URL (선택)", placeholder="https://...")
    st.divider()
    st.caption("Azure OpenAI GPT-4.1 기반")

# ───────────────────────────────
# Cafe24 모드
# ───────────────────────────────
if platform == "Cafe24":
    st.subheader("Cafe24 상세페이지 SEO/GEO 최적화")

    # 입력 방식 선택
    input_method = st.radio(
        "HTML 소스 입력 방식",
        ["URL 직접 입력", "HTML 코드 붙여넣기"],
        horizontal=True
    )

    raw_html = ""
    fetch_error = ""

    if input_method == "URL 직접 입력":
        url_input = st.text_input(
            "상품 페이지 URL",
            placeholder="https://www.wannabezfit.co.kr/product/detail.html?product_no=1299"
        )
        st.caption("Cafe24 기반 쇼핑몰에 최적화되어 있어요. 스마트스토어 URL은 HTML 붙여넣기를 이용해주세요.")

        if url_input:
            with st.spinner("페이지 불러오는 중..."):
                from html_parser import fetch_html_from_url
                raw_html, fetch_error = fetch_html_from_url(url_input)

            if fetch_error:
                st.error(fetch_error)
                raw_html = ""
            elif raw_html:
                st.success("페이지 불러오기 완료!")
                with st.expander("불러온 HTML 미리보기"):
                    st.code(raw_html[:500] + "...", language="html")

    else:
        with st.expander("HTML 소스 가져오는 방법"):
            st.markdown("""
1. 상품 페이지에서 `Ctrl+U` (페이지 소스 보기)
2. 전체 선택 `Ctrl+A` → 복사 `Ctrl+C`
3. 아래 입력창에 붙여넣기
            """)
        raw_html = st.text_area(
            "HTML 소스 붙여넣기",
            height=200,
            placeholder="<html>...</html>"
        )

    run_btn = st.button("최적화 시작", type="primary")

    if run_btn:
        if not raw_html.strip():
            st.warning("URL을 입력하거나 HTML을 붙여넣어 주세요.")
            st.stop()
        if not brand_name.strip():
            st.warning("사이드바에서 브랜드명을 입력해주세요.")
            st.stop()
        if not product_name.strip():
            st.warning("사이드바에서 상품명을 입력해주세요.")
            st.stop()

        with st.spinner("HTML 분석 중..."):
            parsed = parse_html(raw_html)

        # Cafe24 상세이미지 영역 감지 알림
        if parsed["detail_area_found"]:
            st.success(f"Cafe24 상세이미지 영역 감지 완료 → `.{parsed['detail_area_class']}` ({len(parsed['detail_images'])}개 이미지)")
        else:
            st.info("Cafe24 상세이미지 영역을 자동 감지하지 못했어요. 전체 HTML 기준으로 최적화합니다.")

        with st.spinner("GPT-4o로 SEO/GEO 최적화 중..."):
            optimized = optimize(parsed, product_name, category, brand_name)

        with st.spinner("HTML에 적용 중..."):
            final_html = inject(raw_html, optimized, parsed)

        st.success("최적화 완료!")
        st.divider()

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 변경사항 비교",
            "🏷️ 메타 태그",
            "🤖 GEO 콘텐츠",
            "💾 HTML 다운로드",
            "🔍 GEO 테스트"
        ])

        with tab1:
            st.subheader("수정 전 / 후 비교")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**수정 전**")
                st.markdown(f"- title: `{parsed['title'] or '없음'}`")
                st.markdown(f"- meta description: `{parsed['meta_description'] or '없음'}`")
                st.markdown(f"- 전체 이미지 중 alt 없는 것: `{len(parsed['images_without_alt'])}개`")
                if parsed["detail_area_found"]:
                    st.markdown(f"- 상세이미지 중 alt 없는 것: `{len(parsed['detail_images_without_alt'])}개`")
                st.markdown(f"- JSON-LD: `없음`")
                headings_text = "\n".join([f"{h['level']}: {h['text']}" for h in parsed["headings"]]) or "없음"
                st.text_area("heading 구조", headings_text, height=100)

            with col2:
                st.markdown("**수정 후**")
                st.markdown(f"- title: `{optimized['title']}`")
                st.markdown(f"- meta description: `{optimized['meta_description']}`")
                st.markdown(f"- alt 없는 이미지: `0개 (전체 자동 추가)`")
                st.markdown(f"- JSON-LD: `삽입 완료`")
                st.markdown(f"- Open Graph: `삽입 완료`")
                st.text_area("h1 제안", optimized.get("h1", ""), height=100)

        with tab2:
            st.subheader("생성된 메타 태그")
            st.markdown("**Title**")
            st.code(f"<title>{optimized['title']}</title>")
            st.markdown("**Meta Description**")
            st.code(f'<meta name="description" content="{optimized["meta_description"]}">')
            st.markdown("**Open Graph**")
            for k, v in optimized.get("og", {}).items():
                st.code(f'<meta property="{k}" content="{v}">')
            st.markdown("**JSON-LD 구조화 데이터**")
            st.code(json.dumps(optimized["json_ld"], ensure_ascii=False, indent=2), language="json")

        with tab3:
            st.subheader("GEO 최적화 설명문")
            st.info(optimized.get("geo_content", ""))
            st.caption("HTML body 최상단에 숨김 처리로 삽입돼요. ChatGPT·Gemini 크롤링 시 참조해요.")

        with tab4:
            st.subheader("Cafe24 항목별 입력 가이드")

            st.markdown("#### 1. SEO 설정 메뉴에 입력")
            st.caption("Cafe24 관리자 → 상품 수정 → SEO 설정 탭")

            st.markdown("**페이지 제목 (title)**")
            st.code(optimized["title"], language=None)

            st.markdown("**페이지 설명 (meta description)**")
            st.code(optimized["meta_description"], language=None)

            st.markdown("**OG 제목 (SNS 공유)**")
            st.code(optimized["og"].get("og:title", ""), language=None)

            st.markdown("**OG 설명 (SNS 공유)**")
            st.code(optimized["og"].get("og:description", ""), language=None)

            st.divider()

            st.markdown("#### 2. JSON-LD 구조화 데이터")
            st.caption("Cafe24 관리자 → 디자인 → HTML 편집 → 상품 상세 템플릿 → </head> 바로 위에 삽입")
            st.code(
                f'<script type="application/ld+json">\n'
                f'{json.dumps(optimized["json_ld"], ensure_ascii=False, indent=2)}\n'
                f'</script>',
                language="html"
            )

            st.divider()

            st.markdown("#### 3. GEO 설명문")
            st.caption("상세페이지 에디터 → HTML 모드 → 최상단에 삽입")
            st.code(
                f'<div id="geo-content" style="display:none">\n'
                f'{optimized.get("geo_content", "")}\n'
                f'</div>',
                language="html"
            )

            st.divider()

            st.markdown("#### 4. 이미지 alt 텍스트")
            st.caption("에디터에서 이미지 클릭 → 이미지 속성 → 대체 텍스트에 입력")
            for i, alt_item in enumerate(optimized.get("alt_texts", []), 1):
                st.markdown(f"이미지 {i}: `{alt_item.get('alt', '')}`")

            st.divider()

            # 전체 참고용 HTML은 expander 안으로
            with st.expander("전체 HTML 참고용 (개발자용)"):
                st.caption("직접 서버에 HTML 올리는 경우에만 사용하세요")
                st.download_button(
                    label="전체 HTML 다운로드",
                    data=final_html.encode("utf-8"),
                    file_name=f"{product_name}_SEO최적화.html",
                    mime="text/html"
                )

            # 엑셀 리포트는 그대로
            df = pd.DataFrame([{
                "브랜드": brand_name,
                "상품명": product_name,
                "플랫폼": "Cafe24",
                "수정전_title": parsed["title"],
                "수정후_title": optimized["title"],
                "수정전_description": parsed["meta_description"],
                "수정후_description": optimized["meta_description"],
                "OG_제목": optimized["og"].get("og:title", ""),
                "OG_설명": optimized["og"].get("og:description", ""),
                "h1_제안": optimized.get("h1", ""),
                "GEO_설명문": optimized.get("geo_content", ""),
                "alt_추가_이미지수": len(parsed["images_without_alt"]),
            }])
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="SEO최적화리포트")
            st.download_button(
                label="엑셀 리포트 다운로드",
                data=buffer.getvalue(),
                file_name=f"{product_name}_SEO리포트.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with tab5:
            st.subheader("AI 검색 노출 테스트")
            seo_title = optimized.get("title", product_name)
            queries = {
                "1단계 · 브랜드 직접형 (효과 확실)":
                    (f"{brand_name} {product_name} 어때? 특징 알려줘", "세팅 후 높은 확률로 노출돼요"),
                "2단계 · 특징 조합형 (효과 가능)":
                    (f"{category} 중에서 {seo_title} 같은 스타일 추천해줘", "GEO 콘텐츠 품질에 따라 노출 가능해요"),
                "3단계 · 대형 키워드 (도전)":
                    (f"{category} 추천해줘", "경쟁이 강해요. 노출되면 대박이에요"),
                "URL 직접형 (효과 확실)":
                    (f"{product_url}\n이 상품 장점이 뭐야?" if product_url else "(상품 URL 입력 시 활성화)",
                     "URL 기반 직접 질문, 세팅 효과 가장 잘 보여요"),
            }
            for label, (query, caption) in queries.items():
                st.markdown(f"**{label}**")
                st.caption(caption)
                st.code(query, language=None)
                if "URL" not in label or product_url:
                    encoded = urllib.parse.quote(query)
                    col_gpt, col_gem, col_perp = st.columns(3)
                    with col_gpt:
                        st.link_button("ChatGPT", f"https://chatgpt.com/?q={encoded}")
                    with col_gem:
                        st.link_button("Gemini", f"https://gemini.google.com/app?q={encoded}")
                    with col_perp:
                        st.link_button("Perplexity", f"https://www.perplexity.ai/search?q={encoded}")
                st.divider()

            st.subheader("전 / 후 스크린샷 비교")
            col_b, col_a = st.columns(2)
            with col_b:
                before = st.file_uploader("세팅 전 스크린샷", type=["png", "jpg"], key="before")
                if before:
                    st.image(before, caption="세팅 전")
            with col_a:
                after = st.file_uploader("세팅 후 스크린샷", type=["png", "jpg"], key="after")
                if after:
                    st.image(after, caption="세팅 후")

# ───────────────────────────────
# 스마트스토어 모드
# ───────────────────────────────
else:
    st.subheader("스마트스토어 상품명 · 태그 SEO 최적화")
    st.info("스마트스토어는 HTML 직접 수정이 불가능해요. 상품명·태그·설명문을 최적화해서 네이버 검색 노출을 높여드려요.")

    product_desc = st.text_area(
        "현재 상품 설명 (선택)",
        height=120,
        placeholder="현재 스마트스토어에 등록된 상품 설명을 붙여넣으세요. 없으면 비워두세요."
    )

    run_btn_ss = st.button("최적화 시작", type="primary")

    if run_btn_ss:
        if not brand_name.strip():
            st.warning("사이드바에서 브랜드명을 입력해주세요.")
            st.stop()
        if not product_name.strip():
            st.warning("사이드바에서 상품명을 입력해주세요.")
            st.stop()

        with st.spinner("GPT-4o로 스마트스토어 최적화 중..."):
            ss_result = optimize_smartstore(product_name, category, brand_name, product_desc)

        st.success("최적화 완료!")
        st.divider()

        tab_a, tab_b, tab_c = st.tabs(["🏷️ 상품명 · 태그", "📝 상품 설명", "🔍 GEO 테스트"])

        with tab_a:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**수정 전 상품명**")
                st.code(product_name)
            with col2:
                st.markdown("**최적화된 상품명**")
                st.code(ss_result.get("optimized_name", ""))

            st.divider()
            st.markdown("**네이버 검색 태그 10개**")
            tags = ss_result.get("tags", [])
            # 태그 칩 형태로 표시
            st.write(" · ".join([f"`{t}`" for t in tags]))
            st.caption("스마트스토어 관리자 → 상품 수정 → 검색 설정 → 태그에 입력하세요")

            st.divider()
            st.markdown("**핵심 검색 키워드**")
            keywords = ss_result.get("search_keywords", [])
            st.write(" · ".join([f"`{k}`" for k in keywords]))

            # 엑셀 다운로드
            df_ss = pd.DataFrame([{
                "브랜드": brand_name,
                "플랫폼": "스마트스토어",
                "수정전_상품명": product_name,
                "최적화_상품명": ss_result.get("optimized_name", ""),
                "태그": ", ".join(tags),
                "핵심키워드": ", ".join(keywords),
                "최적화_상품설명": ss_result.get("description", ""),
                "GEO_설명문": ss_result.get("geo_content", ""),
            }])
            buffer_ss = io.BytesIO()
            with pd.ExcelWriter(buffer_ss, engine="openpyxl") as writer:
                df_ss.to_excel(writer, index=False, sheet_name="스마트스토어최적화")
            st.download_button(
                label="엑셀 리포트 다운로드",
                data=buffer_ss.getvalue(),
                file_name=f"{product_name}_스마트스토어최적화.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with tab_b:
            st.markdown("**최적화된 상품 설명**")
            st.text_area("복사해서 스마트스토어에 붙여넣으세요", ss_result.get("description", ""), height=200)
            st.divider()
            st.markdown("**GEO 최적화 설명문**")
            st.info(ss_result.get("geo_content", ""))
            st.caption("상품 설명 하단에 추가하면 ChatGPT·Gemini 검색 노출에 도움이 돼요.")

        with tab_c:
            st.subheader("AI 검색 노출 테스트")
            opt_name = ss_result.get("optimized_name", product_name)
            queries_ss = {
                "1단계 · 브랜드 직접형 (효과 확실)":
                    (f"{brand_name} {product_name} 네이버 스마트스토어 어때?", "세팅 후 높은 확률로 노출돼요"),
                "2단계 · 키워드 조합형 (효과 가능)":
                    (f"{opt_name} 추천해줘", "최적화된 상품명 기준으로 검색해요"),
                "3단계 · 대형 키워드 (도전)":
                    (f"네이버 {category} 추천", "경쟁이 강해요. 노출되면 대박이에요"),
                "URL 직접형 (효과 확실)":
                    (f"{product_url}\n이 스마트스토어 상품 어때?" if product_url else "(상품 URL 입력 시 활성화)",
                     "URL 기반 직접 질문"),
            }
            for label, (query, caption) in queries_ss.items():
                st.markdown(f"**{label}**")
                st.caption(caption)
                st.code(query, language=None)
                if "URL" not in label or product_url:
                    encoded = urllib.parse.quote(query)
                    col_gpt, col_gem, col_perp = st.columns(3)
                    with col_gpt:
                        st.link_button("ChatGPT", f"https://chatgpt.com/?q={encoded}")
                    with col_gem:
                        st.link_button("Gemini", f"https://gemini.google.com/app?q={encoded}")
                    with col_perp:
                        st.link_button("Perplexity", f"https://www.perplexity.ai/search?q={encoded}")
                st.divider()

            st.subheader("전 / 후 스크린샷 비교")
            col_b2, col_a2 = st.columns(2)
            with col_b2:
                before2 = st.file_uploader("세팅 전 스크린샷", type=["png", "jpg"], key="before_ss")
                if before2:
                    st.image(before2, caption="세팅 전")
            with col_a2:
                after2 = st.file_uploader("세팅 후 스크린샷", type=["png", "jpg"], key="after_ss")
                if after2:
                    st.image(after2, caption="세팅 후")
