# 증거 (Evidence) - 채팅 기반 스토리 게임

LangGraph와 Streamlit을 활용한 인터랙티브 스릴러 게임입니다.

## 📋 개요

플레이어는 탐사 기자가 되어 내부고발자 "진우"와 채팅으로 소통합니다.
하지만 AI 검열 시스템이 중요한 메시지를 차단하며, 이를 우회하여 진실을 밝혀내야 합니다.

## 🎮 핵심 기능

- **자유 대화**: 선택지가 아닌 자연스러운 채팅으로 스토리 진행
- **동적 검열**: LLM 기반 실시간 메시지 검열 시스템
- **3막 구조**: 9개의 스토리 비트로 구성된 긴장감 넘치는 스토리
- **LangGraph 워크플로우**: 스토리 마스터 → 캐릭터 → 검열 시스템의 3단계 AI 처리

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **LLM Orchestration**: LangChain, LangGraph
- **LLM**: OpenAI GPT-4
- **Language**: Python 3.9+

## 📦 설치 방법

### 1. 필수 요구사항

- Python 3.9 이상
- OpenAI API 키

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 입력하세요:

```bash
cp .env.example .env
# .env 파일을 열어 API 키 입력
```

`.env` 파일 내용:
```
OPENAI_API_KEY=sk-your-api-key-here
```

## 🚀 실행 방법

```bash
streamlit run app.py
```

브라우저에서 자동으로 열리며, 수동으로 접속하려면:
```
http://localhost:8501
```

## 📁 프로젝트 구조

```
.
├── app.py                  # Streamlit 메인 애플리케이션
├── workflow.py             # LangGraph 워크플로우 정의
├── game_state.py           # 게임 상태 타입 정의
├── story_beats.py          # 스토리 비트 정의
├── censorship_rules.py     # 검열 규칙 정의
├── prompts.py              # LLM 프롬프트 템플릿
├── requirements.txt        # Python 패키지 목록
└── .env.example           # 환경 변수 템플릿
```

## 🎯 게임 플레이 가이드

### 기본 플레이

1. 게임이 시작되면 진우가 먼저 말을 걸어옵니다
2. 자유롭게 대화하며 정보를 수집하세요
3. 중요한 정보는 검열 시스템에 의해 차단될 수 있습니다
4. 우회적인 표현으로 소통 방법을 찾아야 합니다

### 사이드바 정보

- **현재 스토리**: 현재 진행 중인 비트와 목표
- **진행 상황**: 시간, 메시지 수 등
- **검열 시스템**: 현재 검열 레벨과 차단 통계
- **전달된 정보**: 성공적으로 전달된 핵심 정보들

### 팁

- 진우에게 직접적인 질문을 하세요
- 메시지가 차단되면 다른 방식으로 표현해보세요
- 긴급한 순간에는 모든 메시지가 차단될 수 있습니다
- 스토리는 약 40-60분 정도 소요됩니다

## 🔧 커스터마이징

### 스토리 비트 수정

`story_beats.py`에서 각 비트의 내용을 수정할 수 있습니다:

```python
"beat_01_first_contact": StoryBeat(
    id="beat_01_first_contact",
    name="첫 접촉",
    objective="진우가 자신을 소개하고 신뢰 구축",
    must_convey=["자신이 제약회사 내부자임", ...],
    # ... 기타 설정
)
```

### 검열 규칙 조정

`censorship_rules.py`에서 레벨별 검열 규칙을 수정할 수 있습니다:

```python
1: CensorshipRule(
    level=1,
    keywords=["바이탈헬스", "사망", ...],
    # ... 기타 규칙
)
```

### LLM 모델 변경

`workflow.py`에서 모델을 변경할 수 있습니다:

```python
def __init__(self, api_key: str, model: str = "gpt-4o"):  # 원하는 모델로 변경
```

## ⚙️ 고급 설정

### 강제 전환 시간 조정

각 비트의 `forced_after_minutes`와 `forced_after_messages`를 조정하여 
스토리 진행 속도를 제어할 수 있습니다.

### 프롬프트 수정

`prompts.py`에서 각 AI 에이전트의 프롬프트를 수정하여 
캐릭터 성격이나 검열 강도를 조절할 수 있습니다.

## 🐛 트러블슈팅

### API 키 오류
- `.env` 파일이 올바른 위치에 있는지 확인
- API 키가 유효한지 확인
- API 사용량 한도를 확인

### JSON 파싱 오류
- LLM이 가끔 잘못된 형식으로 응답할 수 있습니다
- 이 경우 기본값으로 폴백되며 게임은 계속 진행됩니다

### 메시지가 표시되지 않음
- 브라우저를 새로고침해보세요
- 사이드바의 "게임 재시작" 버튼을 눌러보세요

## 📝 라이센스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요!