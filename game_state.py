"""
LangGraph 게임 상태 정의
"""

from typing import TypedDict, List, Dict, Optional
from datetime import datetime


class Message(TypedDict):
    """메시지 타입"""
    role: str  # "user" or "jinwoo" or "system"
    content: str
    timestamp: datetime
    blocked: bool  # 검열 여부


class GameState(TypedDict):
    """게임 전체 상태"""
    # 대화 기록
    messages: List[Message]

    # 현재 스토리 진행
    current_beat: str
    beat_start_time: datetime
    beat_message_count: int
    conveyed_info: List[str]  # 전달된 정보들

    # 검열 시스템
    censorship_level: int
    blocked_messages: List[str]  # 차단된 메시지들

    # 사용자 입력
    user_input: Optional[str]

    # 스토리 마스터 분석 결과
    story_analysis: Optional[Dict]

    # 진우 응답
    jinwoo_response: Optional[List[str]]

    # 검열 결과
    censorship_results: Optional[List[Dict]]

    # 게임 메타데이터
    game_start_time: datetime
    total_messages: int
    user_engagement: int  # 사용자 반응 횟수