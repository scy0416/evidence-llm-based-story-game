"""
스토리 비트 정의
각 비트는 게임의 진행 단계를 나타냅니다.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel


class StoryBeat(BaseModel):
    """스토리 비트 모델"""
    id: str
    name: str
    act: int  # 막 번호 (1, 2, 3)
    objective: str
    must_convey: List[str]
    tone: str
    urgency: int  # 1-10
    forced_after_minutes: Optional[float] = None
    forced_after_messages: Optional[int] = None
    next_beat: Optional[str] = None


# 전체 스토리 비트 정의
STORY_BEATS = {
    "beat_01_first_contact": StoryBeat(
        id="beat_01_first_contact",
        name="첫 접촉",
        act=1,
        objective="진우가 자신을 소개하고 신뢰 구축",
        must_convey=[
            "자신이 제약회사 내부자임",
            "기자의 기사를 읽었음",
            "중요한 제보가 있음"
        ],
        tone="조심스러움",
        urgency=3,
        forced_after_minutes=3.0,
        forced_after_messages=8,
        next_beat="beat_02_first_censorship"
    ),

    "beat_02_first_censorship": StoryBeat(
        id="beat_02_first_censorship",
        name="첫 검열 경험",
        act=1,
        objective="검열 시스템의 존재를 인지",
        must_convey=[
            "회사 이름은 바이탈헬스",
            "회사 이름이 차단됨",
            "메시지 전송 실패 경험",
            "시스템이 감시하고 있음을 인지"
        ],
        tone="당황함",
        urgency=5,
        forced_after_minutes=4.0,
        forced_after_messages=10,
        next_beat="beat_03_revelation"
    ),

    "beat_03_revelation": StoryBeat(
        id="beat_03_revelation",
        name="진실 공개",
        act=1,
        objective="임상시험 사망 사고 정보 전달",
        must_convey=[
            "813호 임상시험",
            "52명 중 19명 사망",
            "데이터 조작 지시",
            "자신도 참여했음",
            "딸도 희생자임"
        ],
        tone="절박함",
        urgency=7,
        forced_after_minutes=5.0,
        forced_after_messages=12,
        next_beat="beat_04_encryption"
    ),

    "beat_04_encryption": StoryBeat(
        id="beat_04_encryption",
        name="암호화 소통",
        act=2,
        objective="우회 소통 방법 모색",
        must_convey=[
            "숫자/암호로 소통 시도",
            "파일 전송 실패",
            "USB에 증거 보관",
            "직접 만나야 함"
        ],
        tone="긴장함",
        urgency=6,
        forced_after_minutes=4.0,
        forced_after_messages=10,
        next_beat="beat_05_meeting_plan"
    ),

    "beat_05_meeting_plan": StoryBeat(
        id="beat_05_meeting_plan",
        name="만남 계획",
        act=2,
        objective="대면 약속 잡기",
        must_convey=[
            "홍대입구역 2호선",
            "239번 출구",
            "내일 밤 9시",
            "USB 전달"
        ],
        tone="조심스러움",
        urgency=7,
        forced_after_minutes=5.0,
        forced_after_messages=12,
        next_beat="beat_06_confession"
    ),

    "beat_06_confession": StoryBeat(
        id="beat_06_confession",
        name="고백",
        act=2,
        objective="진우의 과거와 동기 공개",
        must_convey=[
            "자신도 데이터 조작에 참여했음",
            "딸이 죽고 나서야 정신 차림",
            "속죄와 복수 사이의 갈등",
            "법적 책임 각오함"
        ],
        tone="슬픔과 결의",
        urgency=5,
        forced_after_minutes=4.0,
        forced_after_messages=10,
        next_beat="beat_07_dday_departure"
    ),

    "beat_07_dday_departure": StoryBeat(
        id="beat_07_dday_departure",
        name="D-Day 출발",
        act=3,
        objective="진우가 약속 장소로 출발",
        must_convey=[
            "지금 회사에서 나옴",
            "경비가 이상하게 쳐다봄",
            "USB는 가방에 숨김",
            "택시 탑승"
        ],
        tone="긴장과 불안",
        urgency=8,
        forced_after_minutes=2.0,
        forced_after_messages=6,
        next_beat="beat_08_chase"
    ),

    "beat_08_chase": StoryBeat(
        id="beat_08_chase",
        name="추격",
        act=3,
        objective="추격 시퀀스",
        must_convey=[
            "뒤에 차가 따라옴",
            "택시 기사는 신경과민이라고 함",
            "경찰 신고 시도하지만 차단됨",
            "점점 가까워짐"
        ],
        tone="패닉",
        urgency=9,
        forced_after_minutes=3.0,
        forced_after_messages=8,
        next_beat="beat_09_final_moment"
    ),

    "beat_09_final_moment": StoryBeat(
        id="beat_09_final_moment",
        name="최후의 순간",
        act=3,
        objective="클라이막스 - 모든 긴급 메시지 차단",
        must_convey=[
            "239번 출구 도착",
            "기자를 봄",
            "추격자들이 차에서 내림",
            "30미터 거리",
            "딸 이름도 차단됨"
        ],
        tone="극도의 긴박함",
        urgency=10,
        forced_after_minutes=5.0,
        forced_after_messages=15,
        next_beat="ending"
    )
}


def get_beat(beat_id: str) -> Optional[StoryBeat]:
    """비트 ID로 스토리 비트 가져오기"""
    return STORY_BEATS.get(beat_id)


def get_first_beat() -> StoryBeat:
    """첫 번째 비트 반환"""
    return STORY_BEATS["beat_01_first_contact"]