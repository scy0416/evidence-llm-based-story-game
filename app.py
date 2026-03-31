"""
Streamlit 메인 애플리케이션
"""

import streamlit as st
from datetime import datetime
import time
import os
from dotenv import load_dotenv

from workflow import StoryGameWorkflow
from game_state import GameState, Message
from story_beats import get_first_beat, get_beat

# 환경 변수 로드
load_dotenv()


def initialize_session_state():
    """세션 상태 초기화"""
    if "game_state" not in st.session_state:
        first_beat = get_first_beat()

        st.session_state.game_state = {
            "messages": [],
            "current_beat": first_beat.id,
            "beat_start_time": datetime.now(),
            "beat_message_count": 0,
            "conveyed_info": [],
            "censorship_level": 1,
            "blocked_messages": [],
            "user_input": None,
            "story_analysis": None,
            "jinwoo_response": None,
            "censorship_results": None,
            "game_start_time": datetime.now(),
            "total_messages": 0,
            "user_engagement": 0
        }

        # 진우의 첫 메시지 추가
        st.session_state.game_state["messages"].append(
            Message(
                role="jinwoo",
                content="안녕하세요. 혹시 한국일보 탐사팀 기자님 맞으시죠?",
                timestamp=datetime.now(),
                blocked=False
            )
        )

    if "workflow" not in st.session_state:
        # Streamlit Cloud의 secrets 사용 (배포 시)
        # 로컬에서는 .env 파일 사용
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except (KeyError, FileNotFoundError):
            # secrets가 없으면 환경 변수에서 가져오기
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            st.error("⚠️ OPENAI_API_KEY가 설정되지 않았습니다.")
            st.info("**로컬 실행**: .env 파일에 API 키를 추가하세요.\n\n**Streamlit Cloud**: Settings > Secrets에서 OPENAI_API_KEY를 설정하세요.")
            st.stop()

        st.session_state.workflow = StoryGameWorkflow(api_key=api_key)


def display_message(msg: Message, is_latest: bool = False):
    """메시지 표시"""
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])

    elif msg["role"] == "jinwoo":
        # 차단된 메시지는 시스템 경고로 표시
        if msg["blocked"]:
            with st.chat_message("assistant", avatar="⚠️"):
                st.error("🚫 메시지 전송 실패 - 부적절한 내용이 감지되었습니다.")
        else:
            with st.chat_message("assistant", avatar="🕵️"):
                st.write(msg["content"])

    elif msg["role"] == "system":
        st.info(msg["content"])


def display_game_info():
    """게임 정보 사이드바"""
    with st.sidebar:
        st.title("🎮 게임 정보")

        game_state = st.session_state.game_state
        current_beat = get_beat(game_state["current_beat"])

        st.subheader("📖 현재 스토리")
        st.write(f"**비트**: {current_beat.name}")
        st.write(f"**막**: {current_beat.act}막")
        st.write(f"**목표**: {current_beat.objective}")

        st.subheader("📊 진행 상황")
        elapsed = datetime.now() - game_state["beat_start_time"]
        st.write(f"**비트 경과 시간**: {int(elapsed.total_seconds() / 60)}분")
        st.write(f"**비트 메시지**: {game_state['beat_message_count']}개")
        st.write(f"**총 메시지**: {game_state['total_messages']}개")

        st.subheader("🔒 검열 시스템")
        st.write(f"**레벨**: {game_state['censorship_level']}")
        st.write(f"**차단된 메시지**: {len(game_state['blocked_messages'])}개")

        st.subheader("✅ 전달된 정보")
        if game_state["conveyed_info"]:
            for info in game_state["conveyed_info"]:
                st.write(f"- {info}")
        else:
            st.write("아직 없음")

        st.divider()

        if st.button("🔄 게임 재시작", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def main():
    """메인 함수"""
    st.set_page_config(
        page_title="증거 - 스토리 게임",
        page_icon="🕵️",
        layout="wide"
    )

    initialize_session_state()

    st.title("🕵️ 증거 (Evidence)")
    st.caption("채팅 기반 인터랙티브 스릴러 게임")

    display_game_info()

    # 메시지 히스토리 표시
    for i, msg in enumerate(st.session_state.game_state["messages"]):
        is_latest = (i == len(st.session_state.game_state["messages"]) - 1)
        display_message(msg, is_latest)

    # 사용자 입력
    user_input = st.chat_input("메시지를 입력하세요...")

    if user_input:
        # 사용자 메시지 추가
        user_msg = Message(
            role="user",
            content=user_input,
            timestamp=datetime.now(),
            blocked=False
        )
        st.session_state.game_state["messages"].append(user_msg)
        st.session_state.game_state["user_input"] = user_input
        st.session_state.game_state["user_engagement"] += 1

        # 사용자 메시지 즉시 표시
        with st.chat_message("user"):
            st.write(user_input)

        # 타이핑 인디케이터
        with st.chat_message("assistant", avatar="🕵️"):
            with st.spinner("진우가 입력 중..."):
                # 워크플로우 실행
                result_state = st.session_state.workflow.run(
                    st.session_state.game_state
                )

                # 상태 업데이트
                st.session_state.game_state = result_state

        # 페이지 새로고침하여 새 메시지 표시
        st.rerun()


if __name__ == "__main__":
    main()