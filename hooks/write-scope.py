#!/usr/bin/env python3
# 목적: 에이전트 frontmatter hooks(PreToolUse Edit|Write)에서 허용 경로 밖 파일 수정을 막는다.
#   인수: 허용 경로 정규식(프로젝트 루트 기준 상대 경로에 search). 하나라도 매치하면 통과.
#   `!정규식` 인수는 제외 패턴 — 매치하면 허용 패턴과 무관하게 차단.
# 판정 불가 시(file_path 없음, JSON 파싱 실패): 통과. 이 훅은 경계 강제이지 도구 검증이 아니다.
# 검증: `echo '{"tool_input":{"file_path":"<허용 밖 경로>"}}' | .claude/hooks/write-scope.py '<허용 정규식>'`가 exit 2, 허용 경로가 exit 0인지 확인한다.
import json
import os
import re
import sys


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    path = (payload.get("tool_input") or {}).get("file_path")
    if not path:
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    allow = [a for a in sys.argv[1:] if not a.startswith("!")]
    deny = [a[1:] for a in sys.argv[1:] if a.startswith("!")]
    if any(re.search(d, rel) for d in deny) or not any(re.search(a, rel) for a in allow):
        print("허용 범위 밖 파일 수정: %s — 이 에이전트의 수정 범위는 %s 이다. 범위 밖 변경은 보고만 한다."
              % (rel, ", ".join(allow)), file=sys.stderr)
        return 2
    return 0


sys.exit(main())
