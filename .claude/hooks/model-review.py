#!/usr/bin/env python3
# 목적: 별칭(opus·sonnet·haiku·fable)이 가리키는 모델이 바뀌었으면 하네스 재검토를 범위와 함께 요청한다.
#   - 별칭→모델 표는 환경변수 ANTHROPIC_DEFAULT_<계열>_MODEL, 없으면 Claude Code 바이너리에서 추출한다.
#   - opus 교체: 하네스 전체 재검토.
#   - 그 외 교체: `.claude/agents/*.md` 중 `model:`이 그 계열인 에이전트만. 대상이 없으면 알림 없이 reviewed.
#   - 표 추출 실패 시: 그 사실을 한 줄 알리고 세션 모델의 계열만 검사한다.
# 판정 불가 시(모델 식별 실패 등): 통과. SessionStart는 차단 대상이 아니다.
# 상태 파일: `<계열> <모델ID> <pending|reviewed>` 한 줄씩.
# 검증: model-review.txt를 백업한 뒤 `echo '{}' | ANTHROPIC_DEFAULT_<계열>_MODEL=<바뀐 모델ID> .claude/hooks/model-review.py`로
#   알림 문구와 pending 전이를 확인하고 백업을 되돌린다. stdin의 model 필드는 별칭 표가 잡히면 쓰이지 않아 교체 시늉이 되지 않는다.
import glob
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, os.pardir, "model-review.txt")
AGENTS = os.path.join(HERE, os.pardir, "agents", "*.md")
FAMILIES = ("opus", "sonnet", "haiku", "fable")
TAIL = "harness 스킬의 '모델 교체 재검토' 절을 사용자에게 먼저 제안한다. 사용자가 미루면 그대로 진행하고 이번 세션에서 다시 꺼내지 않는다."


def normalize(model):
    if isinstance(model, dict):
        model = model.get("id") or model.get("display_name")
    if not isinstance(model, str):
        return None
    # `claude-opus-5[1m]` 등 컨텍스트 변형 접미사는 같은 모델로 본다.
    model = re.sub(r"\[[^\]]*\]$", "", model.strip()).strip()
    return model or None


def family_of(model):
    for family in FAMILIES:
        if re.search(r"(^|-)%s(-|$)" % family, model):
            return family
    return None


def cli_binary():
    path = shutil.which("claude")
    if path:
        return os.path.realpath(path)
    versions = glob.glob(os.path.expanduser("~/.local/share/claude/versions/*"))
    return max(versions, key=os.path.getmtime) if versions else None


def alias_table():
    # 바이너리 안의 `{fable:"claude-...",opus:"claude-...",sonnet:"claude-...",haiku:"claude-..."}` 표를 읽는다.
    table = {}
    path = cli_binary()
    if path:
        try:
            with open(path, "rb") as f:
                data = f.read()
            m = re.search(rb'\{((?:(?:opus|sonnet|haiku|fable):"claude-[a-z0-9-]+",?){4})\}', data)
            if m:
                for k, v in re.findall(rb'(opus|sonnet|haiku|fable):"(claude-[a-z0-9-]+)"', m.group(1)):
                    table[k.decode()] = v.decode()
        except OSError:
            pass
    for family in FAMILIES:
        env = normalize(os.environ.get("ANTHROPIC_DEFAULT_%s_MODEL" % family.upper()))
        if env:
            table[family] = env
    return table


def agents_using(family, model):
    # frontmatter의 `model:`이 계열 별칭이거나 그 계열의 전체 ID인 에이전트.
    found = []
    for path in sorted(glob.glob(AGENTS)):
        try:
            with open(path, encoding="utf-8") as f:
                head = f.read(4096)
        except OSError:
            continue
        m = re.search(r"^model:\s*(\S+)", head, re.M)
        if not m:
            continue
        value = m.group(1)
        if value == family or value == model or family_of(value) == family:
            found.append(os.path.basename(path))
    return found


def model_from_transcripts(transcript_path):
    # SessionStart 페이로드에 model 필드가 없는 빌드가 있어, 직전 세션 기록에서 읽는다.
    if not transcript_path:
        return None
    directory = os.path.dirname(transcript_path)
    try:
        files = [os.path.join(directory, n) for n in os.listdir(directory) if n.endswith(".jsonl")]
    except OSError:
        return None
    files = [f for f in files if os.path.abspath(f) != os.path.abspath(transcript_path)]
    for path in sorted(files, key=os.path.getmtime, reverse=True)[:5]:
        try:
            with open(path, "rb") as f:
                f.seek(0, os.SEEK_END)
                f.seek(max(0, f.tell() - 262144))
                chunk = f.read().decode("utf-8", "ignore")
        except OSError:
            continue
        for line in reversed(chunk.splitlines()):
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            model = normalize((entry.get("message") or {}).get("model"))
            if model:
                return model
    return None


def read_state():
    # 반환: {계열: (모델, 상태)}. 구형식(`<모델> <상태>`)은 계열을 유도해 옮긴다.
    state = {}
    try:
        with open(STATE, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    for line in lines:
        parts = line.split()
        if len(parts) == 3:
            state[parts[0]] = (parts[1], parts[2])
        elif len(parts) == 2:
            family = family_of(parts[0])
            if family and (family not in state or state[family][1] == "pending"):
                state[family] = (parts[0], parts[1])
    return state


def write_state(state):
    with open(STATE, "w", encoding="utf-8") as f:
        for family in sorted(state):
            f.write("%s %s %s\n" % (family, state[family][0], state[family][1]))


def emit(lines):
    json.dump(
        {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(lines)}},
        sys.stdout,
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    session = normalize(payload.get("model")) or model_from_transcripts(payload.get("transcript_path"))
    table = alias_table()
    notes = []
    if not table:
        notes.append("모델 별칭 표를 Claude Code 바이너리에서 추출하지 못했다. 세션 모델 기준으로만 검사한다.")
        if session and family_of(session):
            table = {family_of(session): session}
    if not table:
        return

    state = read_state()
    if state is None:
        # 최초 실행: 현재 별칭 표를 하네스가 작성된 기준으로 보고 기록만 한다.
        write_state({f: (m, "reviewed") for f, m in table.items()})
        return
    for family, model in table.items():
        if family not in state or state[family][0] != model:
            state[family] = (model, "pending")

    pending = [f for f in FAMILIES if f in state and state[f][1] == "pending"]
    for family in pending:
        model = state[family][0]
        if family == "opus":
            notes.append("하네스 재검토 미완료: opus → %s. 범위: 하네스 전체." % model)
            continue
        agents = agents_using(family, model)
        if not agents:
            state[family] = (model, "reviewed")
            continue
        notes.append("하네스 재검토 미완료: %s → %s. 범위: model이 %s인 에이전트만 — %s."
                     % (family, model, family, ", ".join(agents)))
    write_state(state)
    if any(n.startswith("하네스 재검토 미완료") for n in notes):
        notes.append(TAIL)
    if notes:
        emit(notes)


main()
