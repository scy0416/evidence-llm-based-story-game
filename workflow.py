"""
LangGraph 워크플로우 정의
"""

from typing import Dict, List
import json
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

from game_state import GameState, Message
from story_beats import get_beat, STORY_BEATS
from censorship_rules import get_censorship_level, CENSORSHIP_RULES
from prompts import STORY_MASTER_PROMPT, JINWOO_PROMPT, CENSORSHIP_PROMPT


class StoryGameWorkflow:
    """스토리 게임 워크플로우"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.7
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """LangGraph 워크플로우 구축"""
        workflow = StateGraph(GameState)

        # 노드 추가
        workflow.add_node("story_master", self.story_master_node)
        workflow.add_node("jinwoo_character", self.jinwoo_character_node)
        workflow.add_node("censorship_check", self.censorship_check_node)
        workflow.add_node("update_state", self.update_state_node)

        # 엣지 정의
        workflow.add_edge(START, "story_master")
        workflow.add_edge("story_master", "jinwoo_character")
        workflow.add_edge("jinwoo_character", "censorship_check")
        workflow.add_edge("censorship_check", "update_state")
        workflow.add_edge("update_state", END)

        return workflow.compile()

    def story_master_node(self, state: GameState) -> GameState:
        """스토리 마스터 - 스토리 진행 분석"""
        current_beat = get_beat(state["current_beat"])

        # 경과 시간 계산
        elapsed = datetime.now() - state["beat_start_time"]
        elapsed_minutes = elapsed.total_seconds() / 60

        # 채팅 히스토리 구성
        chat_history = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in state["messages"][-10:]  # 최근 10개만
        ])

        # 미전달 정보 계산
        must_convey = set(current_beat.must_convey)
        conveyed = set(state["conveyed_info"])
        not_conveyed = must_convey - conveyed

        # 프롬프트 구성
        prompt = STORY_MASTER_PROMPT.format_messages(
            current_beat_name=current_beat.name,
            beat_objective=current_beat.objective,
            must_convey=list(not_conveyed),
            conveyed_info=list(conveyed),
            elapsed_minutes=round(elapsed_minutes, 1),
            message_count=state["beat_message_count"],
            urgency=current_beat.urgency,
            chat_history=chat_history,
            user_message=state["user_input"] or ""
        )

        # LLM 호출
        response = self.llm.invoke(prompt)

        # JSON 파싱
        try:
            # 코드 블록 제거
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            analysis = json.loads(content.strip())
            state["story_analysis"] = analysis
        except json.JSONDecodeError as e:
            # 파싱 실패 시 기본값
            state["story_analysis"] = {
                "user_intent": "unknown",
                "user_emotion": "neutral",
                "should_progress": False,
                "next_beat": None,
                "jinwoo_instructions": {
                    "must_convey_this_turn": [],
                    "tone": current_beat.tone,
                    "special_direction": None,
                    "reasoning": "JSON parsing failed"
                }
            }

        return state

    def jinwoo_character_node(self, state: GameState) -> GameState:
        """진우 캐릭터 - 응답 생성"""
        current_beat = get_beat(state["current_beat"])
        analysis = state["story_analysis"]

        # 채팅 히스토리
        chat_history = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in state["messages"][-10:]
        ])

        # 진우 지시사항
        jinwoo_instructions = json.dumps(
            analysis.get("jinwoo_instructions", {}),
            ensure_ascii=False,
            indent=2
        )

        # 프롬프트 구성
        prompt = JINWOO_PROMPT.format_messages(
            current_beat_name=current_beat.name,
            tone=analysis["jinwoo_instructions"].get("tone", current_beat.tone),
            urgency=current_beat.urgency,
            jinwoo_instructions=jinwoo_instructions,
            chat_history=chat_history,
            user_message=state["user_input"] or ""
        )

        # LLM 호출
        response = self.llm.invoke(prompt)

        # JSON 파싱
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            result = json.loads(content.strip())
            messages = result.get("messages", [response.content])
        except json.JSONDecodeError:
            # 파싱 실패 시 전체 응답을 하나의 메시지로
            messages = [response.content]

        state["jinwoo_response"] = messages
        return state

    def censorship_check_node(self, state: GameState) -> GameState:
        """검열 시스템 - 메시지 검열"""
        censorship_level = get_censorship_level(state["current_beat"])
        rule = CENSORSHIP_RULES.get(censorship_level)

        # 이전 차단 메시지들
        previous_blocks = "\n".join(state["blocked_messages"][-5:])

        results = []

        for message in state["jinwoo_response"]:
            # 프롬프트 구성
            prompt = CENSORSHIP_PROMPT.format_messages(
                censorship_level=censorship_level,
                blocked_keywords=", ".join(rule.keywords) if rule else "",
                previous_blocks=previous_blocks,
                message_to_check=message
            )

            # LLM 호출
            response = self.llm.invoke(prompt)

            # JSON 파싱
            try:
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]

                result = json.loads(content.strip())
                result["message"] = message
                results.append(result)

            except json.JSONDecodeError:
                # 파싱 실패 시 기본 통과
                results.append({
                    "decision": "PASS",
                    "reason": "JSON parsing failed - default pass",
                    "message": message
                })

        state["censorship_results"] = results
        return state

    def update_state_node(self, state: GameState) -> GameState:
        """상태 업데이트"""
        current_beat = get_beat(state["current_beat"])
        censorship_level = get_censorship_level(state["current_beat"])

        # 검열 레벨별 경고 메시지
        warning_messages = {
            1: "🚫 메시지 전송 실패 - 부적절한 내용이 감지되었습니다.",
            2: "⚠️ 메시지 차단됨 - 민감한 정보가 포함되어 있습니다.",
            3: "🔒 전송 불가 - 보안 정책 위반이 감지되었습니다.",
            4: "❌ 긴급 차단 - 시스템 보호를 위해 메시지가 차단되었습니다."
        }

        # 검열 결과를 메시지로 변환
        has_blocked = False
        blocked_count = 0

        for result in state["censorship_results"]:
            if result["decision"] == "BLOCK":
                has_blocked = True
                blocked_count += 1

                # 차단된 메시지는 경고로 표시
                warning_msg = Message(
                    role="jinwoo",
                    content=warning_messages.get(censorship_level, warning_messages[1]),
                    timestamp=datetime.now(),
                    blocked=True
                )
                state["messages"].append(warning_msg)
            else:
                # 정상 메시지
                message = Message(
                    role="jinwoo",
                    content=result["message"],
                    timestamp=datetime.now(),
                    blocked=False
                )
                state["messages"].append(message)

        # 차단된 메시지가 있으면 진우의 당황 반응 추가
        if has_blocked:
            if blocked_count == 1:
                reaction = "...어? 지금 제 메시지 보이세요?"
            elif blocked_count == 2:
                reaction = "또 안되네요. 뭔가 차단되는 것 같은데..."
            else:
                reaction = "계속 전송이 안 되네요. 이거 감시당하는 건가요?"

            reaction_message = Message(
                role="jinwoo",
                content=reaction,
                timestamp=datetime.now(),
                blocked=False
            )
            state["messages"].append(reaction_message)

        # 메시지 카운트 증가
        state["beat_message_count"] += 1
        state["total_messages"] += 1

        # 전달된 정보 업데이트 (중복 체크)
        for info in current_beat.must_convey:
            # 이미 전달된 정보는 스킵
            if info in state["conveyed_info"]:
                continue

            # 정보가 전달되었는지 체크
            for result in state["censorship_results"]:
                if result["decision"] == "PASS":
                    # 키워드 매칭
                    keywords = info.split()[:3]
                    if any(kw in result["message"] for kw in keywords):
                        state["conveyed_info"].append(info)
                        break  # 한 번만 추가

        # 차단된 메시지 기록 (중복 체크)
        for result in state["censorship_results"]:
            if result.get("decision") == "BLOCK":
                if result["message"] not in state["blocked_messages"]:
                    state["blocked_messages"].append(result["message"])

        # 비트 전환 체크
        analysis = state.get("story_analysis", {})
        if analysis.get("should_progress") and analysis.get("next_beat"):
            new_beat_id = analysis["next_beat"]
            if new_beat_id in STORY_BEATS and new_beat_id != state["current_beat"]:
                state["current_beat"] = new_beat_id
                state["beat_start_time"] = datetime.now()
                state["beat_message_count"] = 0
                state["censorship_level"] = get_censorship_level(new_beat_id)

        # 강제 전환 체크 (시간/메시지 수 초과)
        elapsed = datetime.now() - state["beat_start_time"]
        elapsed_minutes = elapsed.total_seconds() / 60

        should_force_transition = False

        if current_beat.forced_after_minutes and elapsed_minutes > current_beat.forced_after_minutes:
            should_force_transition = True

        if current_beat.forced_after_messages and state["beat_message_count"] >= current_beat.forced_after_messages:
            should_force_transition = True

        if should_force_transition and current_beat.next_beat:
            if current_beat.next_beat != state["current_beat"]:  # 중복 전환 방지
                state["current_beat"] = current_beat.next_beat
                state["beat_start_time"] = datetime.now()
                state["beat_message_count"] = 0
                state["censorship_level"] = get_censorship_level(current_beat.next_beat)

        return state

    def run(self, state: GameState) -> GameState:
        """워크플로우 실행"""
        return self.graph.invoke(state)