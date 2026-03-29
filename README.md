# 🔍 상세페이지 SEO/GEO 자동 최적화 도구

> Azure OpenAI GPT-4o 기반으로 이커머스 상세페이지 HTML을 분석하고,  
> SEO(검색엔진 최적화)와 GEO(AI 검색 최적화)에 맞게 자동으로 개선해주는 Streamlit 웹 앱입니다.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)](https://streamlit.io/)
[![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI%20GPT--4o-0078D4)](https://azure.microsoft.com/ko-kr/products/ai-services/openai-service)

---

## 📌 프로젝트 배경

이커머스 셀러들은 상품 상세페이지를 만들 때 SEO를 거의 신경 쓰지 않아요.  
특히 Cafe24, 스마트스토어 운영자들은 이미지만 올리고 끝내는 경우가 대부분이에요.

그 결과:
- `<title>`, `<meta description>` 없거나 기본값 그대로
- 이미지 수십 장에 `alt` 태그 전혀 없음
- `JSON-LD` 구조화 데이터 없어서 Google 리치 스니펫 미노출
- ChatGPT, Gemini 같은 AI 검색에서 상품 정보 인식 불가 (GEO 0점)

이 프로젝트는 이 문제를 **URL 입력 또는 HTML 붙여넣기 한 번**으로 해결해요.

---

## ✨ 주요 기능

### Cafe24 상세페이지 HTML 최적화
| 항목 | 내용 |
|------|------|
| `<title>` 최적화 | 핵심 키워드 앞 배치, 60자 이내 |
| `<meta description>` | 구매 유도 문구 포함, 160자 이내 |
| Open Graph 태그 | 카카오톡·SNS 공유 시 썸네일·제목 자동 표시 |
| JSON-LD 구조화 데이터 | Google 리치 스니펫 + AI 검색 인식률 향상 |
| `img alt` 자동 추가 | 이미지 전체 alt 텍스트 자동 생성 |
| `h1` 태그 최적화 | 상품명 중심 heading 구조 재정리 |
| GEO 설명문 삽입 | ChatGPT·Gemini가 참조하는 자연어 콘텐츠 |

### 스마트스토어 키워드 최적화
| 항목 | 내용 |
|------|------|
| 상품명 최적화 | 네이버 검색 알고리즘에 맞는 키워드 순서 재배치 |
| 태그 10개 자동 생성 | 검색량 높은 키워드 위주 |
| 상품 설명 최적화 | 구매 유도 + 키워드 자연스럽게 포함 |
| GEO 설명문 | AI 검색 최적화용 자연어 설명 2~3문장 |

### GEO 테스트 기능
- ChatGPT · Gemini · Perplexity에서 상품 노출 여부 직접 테스트
- 브랜드 직접형 / 특징 조합형 / 대형 키워드 / URL 직접형 쿼리 자동 생성
- 세팅 전/후 스크린샷 비교 업로드

---

## 🤔 개발 과정에서 고민한 것들

### 1. Azure vs Google 무료 티어
처음엔 Google Cloud Vision API + Gemini 조합도 검토했어요.  
Google Gemini API는 2025년 12월에 무료 한도를 대폭 축소(50~80%)해서,  
크레딧이 있는 Azure OpenAI를 메인으로 결정했어요.

### 2. 이미지 분석 → HTML 최적화로 방향 전환
초기 기획은 "포토리뷰 이미지 → 해시태그 자동 생성"이었어요.  
Azure Vision API로 이미지를 분석하고 GPT-4o로 해시태그를 뽑는 구조였죠.

개발하면서 방향을 바꿨어요.  
**"상세페이지 HTML 자체를 SEO/GEO에 맞게 수정해주는 것"** 이  
셀러 입장에서 훨씬 체감 효과가 크고, 크몽 외주 단가도 높다는 판단이었어요.  
덕분에 Azure Vision API 의존성이 사라지고 코드도 훨씬 단순해졌어요.

### 3. Cafe24 vs 스마트스토어 — 플랫폼별 한계
Cafe24는 HTML을 직접 편집할 수 있어서 이 앱이 잘 맞아요.  
스마트스토어는 JS 렌더링 + 봇 차단으로 URL 크롤링이 거의 불가능해요.  
그래서 플랫폼별로 기능을 분리했어요.

| 플랫폼 | 입력 방식 | 주요 결과물 |
|--------|-----------|-------------|
| Cafe24 | URL 크롤링 또는 HTML 붙여넣기 | 최적화된 HTML + 항목별 입력 가이드 |
| 스마트스토어 | 상품명·설명 텍스트 입력 | 최적화된 상품명 + 태그 10개 + 설명문 |

### 4. GEO — "정말 인용되는지" 어떻게 확인하나?
GEO(Generative Engine Optimization) 효과를 측정하는 공식 API는 없어요.  
ChatGPT, Gemini는 어떤 페이지를 참조했는지 외부에 공개하지 않거든요.

현실적인 확인 방법 3가지를 정리했어요:
1. **Perplexity 직접 검색** — 답변 하단에 출처 URL이 표시됨
2. **Google Search Console** — GPTBot, PerplexityBot 크롤링 횟수 증가 확인
3. **AI에 직접 질문** — 브랜드명+상품명으로 ChatGPT·Gemini에 검색 후 노출 여부 확인

"부츠컷 레깅스 추천해줘" 같은 대형 키워드 노출은 HTML 세팅만으론 한계가 있어요.  
현실적으로 효과가 나타나는 키워드 범위를 3단계로 나눠서 테스트 탭에 반영했어요.

### 5. Cafe24 HTML 다운로드의 함정
초기엔 최적화된 HTML 전체를 다운로드해서 에디터에 붙여넣으라고 했는데,  
Cafe24 에디터는 `<body>` 안의 콘텐츠 영역만 받아요.  
`<html><head>` 구조를 에디터에 넣으면 태그가 깨지거나 무시돼요.

그래서 결과물을 **항목별로 분리**해서 어디에 넣어야 하는지 가이드와 함께 제공하도록 바꿨어요.

---

## 🛠️ 기술 스택

```
Azure OpenAI (GPT-4o)   — SEO/GEO 텍스트 생성
BeautifulSoup4          — HTML 파싱 및 태그 주입
Streamlit               — 웹 UI
Pandas + openpyxl       — 엑셀 리포트 생성
Requests                — URL 크롤링
python-dotenv           — 환경변수 관리
```

---

## 🚀 시작하기

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/seo-geo-ai.git
cd seo-geo-ai
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env.example`을 복사해서 `.env` 파일을 만들고 본인 Azure 정보를 입력하세요.
```bash
cp .env.example .env
```

```env
AZURE_OPENAI_ENDPOINT=https://YOUR_RESOURCE.openai.azure.com/
AZURE_OPENAI_KEY=your_openai_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

Azure OpenAI 키는 [Azure Portal](https://portal.azure.com) →  
해당 리소스 → `Keys and Endpoint` 메뉴에서 확인할 수 있어요.

### 4. 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속하면 바로 사용할 수 있어요.

---

## 📁 프로젝트 구조

```
seo-geo-ai/
├── .env                  # API 키 (gitignore 처리됨)
├── .env.example          # 환경변수 템플릿
├── .gitignore
├── requirements.txt
├── config.py             # 환경변수 로딩
├── html_parser.py        # HTML 파싱 + URL 크롤링
├── seo_optimizer.py      # GPT-4o SEO/GEO 텍스트 생성
├── html_injector.py      # 최적화 결과 HTML 주입
└── app.py                # Streamlit 메인 UI
```

---

## 📊 결과물 예시

### Cafe24 최적화 전/후
| 항목 | 수정 전 | 수정 후 |
|------|---------|---------|
| title | 없음 | 부츠컷 레깅스 DEMI \| 워너비핏 하의 추천 |
| meta description | 없음 | 워너비핏 DEMI 부츠컷 레깅스로 슬림하고 편안한 핏을... |
| alt 없는 이미지 | 23개 | 0개 |
| JSON-LD | 없음 | 삽입 완료 |
| GEO 설명문 | 없음 | 삽입 완료 |

---

## ⚠️ 주의사항

- `.env` 파일은 절대 GitHub에 올리지 마세요 (`.gitignore`에 포함됨)
- Azure OpenAI는 사용량에 따라 과금돼요. 테스트 시 크레딧 소진에 주의하세요
- 스마트스토어 URL 크롤링은 봇 차단으로 동작하지 않아요. HTML 붙여넣기를 이용하세요
- GEO 효과는 크롤링 주기(수일~수주)가 있어 즉시 반영되지 않아요

---

## 📝 라이선스

MIT License