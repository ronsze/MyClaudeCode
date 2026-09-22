#!/usr/bin/env python3
# 목적: 지정 스킬을 로드하지 않은 상태의 도구 호출을 막는다. 스킬 본문 지시만으로는 로드가 강제되지 않는다.
#   인수: 필수 스킬 이름(디렉토리명). 여러 개면 그 중 하나라도 로드돼 있으면 통과.
#   판정: 세션 트랜스크립트에서 Skill 도구 호출 또는 `/<이름>` 슬래시 호출을 찾는다.
# 판정 불가 시(transcript_path 없음·읽기 실패·JSON 파싱 실패): 통과. 이 훅은 로드 강제이지 도구 검증이 아니다.
# 검증: 빈 트랜스크립트 파일 경로를 넘기면 exit 2, Skill 호출(`{"message":{"content":[{"type":"tool_use",
#   "name":"Skill","input":{"skill":"trello"}}]}}`)이 담긴 트랜스크립트를 넘기면 exit 0인지 확인한다.
import json
import os
import sys


def iter_blocks(line):
    try:
        entry = json.loads(line)
    except Exception:
        return
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                yield block


def is_loaded(transcript_path, skills):
    slash_marks = tuple("<command-name>%s" % s for s in skills) + tuple("/%s" % s for s in skills)
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            for block in iter_blocks(line):
                if block.get("type") == "tool_use" and block.get("name") == "Skill":
                    if (block.get("input") or {}).get("skill") in skills:
                        return True
                if block.get("type") == "text":
                    text = block.get("text") or ""
                    if any(mark in text for mark in slash_marks):
                        return True
    return False


def main():
    skills = sys.argv[1:]
    if not skills:
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    transcript_path = payload.get("transcript_path")
    if not transcript_path or not os.path.isfile(transcript_path):
        return 0
    try:
        if is_loaded(transcript_path, skills):
            return 0
    except Exception:
        return 0
    print("%s 스킬을 로드하지 않았다. Skill 도구로 %s 스킬을 먼저 로드하고 그 규칙에 맞춰 다시 호출한다."
          % (", ".join(skills), skills[0]), file=sys.stderr)
    return 2


sys.exit(main())
