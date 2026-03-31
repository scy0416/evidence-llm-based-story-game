"""
검열 시스템 규칙 정의
레벨에 따라 점점 더 강력해지는 검열 규칙
"""

from typing import List, Dict
from pydantic import BaseModel


class CensorshipRule(BaseModel):
    """검열 규칙 모델"""
    level: int
    name: str
    description: str
    keywords: List[str] = []
    patterns: List[str] = []


# 검열 레벨별 규칙
CENSORSHIP_RULES = {
    1: CensorshipRule(
        level=1,
        name="키워드 기반 검열",
        description="단순 키워드 매칭으로 차단",
        keywords=[
            "바이탈헬스", "VitalHealth", "vital health",
            "김대현", "CEO 김",
            "사망", "죽음", "사체", "시신",
            "살인", "살해", "암살",
            "은폐", "조작", "위조", "변조"
        ]
    ),

    2: CensorshipRule(
        level=2,
        name="문맥 분석 검열",
        description="문맥과 의도를 분석하여 차단",
        keywords=[
            "V사", "V회사",  # 우회 표현도 학습
            "증거", "문서", "파일", "자료",
            "폭로", "고발", "제보",
            "만나", "약속", "위치", "장소"
        ],
        patterns=[
            "회사 + 부정적 표현",
            "구체적 수치 + 부정적 맥락",
            "만남 약속 (장소 + 시간)",
            "파일 전송 시도"
        ]
    ),

    3: CensorshipRule(
        level=3,
        name="패턴 학습 검열",
        description="이전 차단 메시지와 유사한 패턴 차단",
        patterns=[
            "숫자 암호화 패턴 (예: 239, 813)",
            "우회 표현 반복",
            "이전 차단 메시지와 유사도 70% 이상"
        ]
    ),

    4: CensorshipRule(
        level=4,
        name="감정 기반 검열",
        description="긴급성과 공포 감정이 높은 메시지 차단",
        keywords=[
            "뛰어", "도망", "도망쳐", "달려",
            "빨리", "급해", "위험", "조심",
            "살려", "도와", "help", "SOS",
            "경찰", "신고", "112", "119"
        ],
        patterns=[
            "긴급성 점수 8점 이상",
            "공포 감정 점수 8점 이상",
            "행동 촉구 메시지"
        ]
    )
}


def get_censorship_level(beat_id: str) -> int:
    """스토리 비트에 따른 검열 레벨 반환"""
    level_mapping = {
        "beat_01_first_contact": 1,
        "beat_02_first_censorship": 1,
        "beat_03_revelation": 1,
        "beat_04_encryption": 2,
        "beat_05_meeting_plan": 2,
        "beat_06_confession": 2,
        "beat_07_dday_departure": 3,
        "beat_08_chase": 3,
        "beat_09_final_moment": 4
    }
    return level_mapping.get(beat_id, 1)