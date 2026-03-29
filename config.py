import os
from dotenv import load_dotenv

load_dotenv()

AZURE_VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT")
AZURE_VISION_KEY = os.getenv("AZURE_VISION_KEY")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# 해시태그 생성 개수
HASHTAG_COUNT = 10
# Vision 태그 신뢰도 최소값 (0~1)
TAG_CONFIDENCE_THRESHOLD = 0.7