#!/usr/bin/env python3
# 목적: PreToolUse(Edit|Write)에서 허용 경로 밖 파일 수정을 막는다.
#   인수: [--agent <이름>] <허용 경로 정규식>... — 프로젝트 루트 기준 상대 경로에 search. 하나라도 매치하면 통과.
#   `!정규식` 인수는 제외 패턴 — 매치하면 허용 패턴과 무관하게 차단.
#   `--agent`가 있으면 stdin의 agent_type(`<플러그인>:` 접두 무시)이 그 이름일 때만 판정하고, 아니면 통과한다 —
#   플러그인 에이전트는 frontmatter hooks를 가질 수 없어 플러그인 hooks.json에서 에이전트별로 건다.
#   프로젝트 `.claude/write-scope.json`에 `{"<에이전트>": ["<정규식>", "!<정규식>"]}`가 있으면 그 에이전트의 인수 패턴을 대체한다.
# 판정 불가 시(file_path 없음, JSON 파싱 실패): 통과. 이 훅은 경계 강제이지 도구 검증이 아니다.
# 검증: `echo '{"agent_type":"test-engineer","tool_input":{"file_path":"<허용 밖 경로>"}}' | hooks/write-scope.py --agent test-engineer '<허용 정규식>'`가
#   exit 2, 허용 경로가 exit 0, agent_type이 다른 입력이 exit 0인지 확인한다.
import json
import os
import re
import sys


def main():
    args = sys.argv[1:]
    agent = None
    if args[:1] == ["--agent"] and len(args) >= 2:
        agent, args = args[1], args[2:]
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if agent:
        agent_type = payload.get("agent_type")
        if not isinstance(agent_type, str) or agent_type.split(":")[-1] != agent:
            return 0
    path = (payload.get("tool_input") or {}).get("file_path")
    if not path:
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    if agent:
        args = override(root, agent) or args
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    allow = [a for a in args if not a.startswith("!")]
    deny = [a[1:] for a in args if a.startswith("!")]
    if any(re.search(d, rel) for d in deny) or not any(re.search(a, rel) for a in allow):
        print("허용 범위 밖 파일 수정: %s — 이 에이전트의 수정 범위는 %s 이다. 범위 밖 변경은 보고만 한다."
              % (rel, ", ".join(allow)), file=sys.stderr)
        return 2
    return 0


def override(root, agent):
    try:
        with open(os.path.join(root, ".claude", "write-scope.json"), encoding="utf-8") as f:
            patterns = json.load(f).get(agent)
    except Exception:
        return None
    return patterns if isinstance(patterns, list) and patterns else None


sys.exit(main())
