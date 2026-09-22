# my-claude-code

Claude Code 플러그인. 프로젝트 하네스(`.claude/**`)를 만들고 관리하는 데 필요한 범용 부분만 담는다. 프로젝트 고유 절차(구현·병합·이슈 트래커)는 각 프로젝트의 `.claude/`에 둔다.

## 구성

| 구성요소 | 역할 |
|---|---|
| `skills/harness` | 하네스 구성요소(스킬·에이전트·훅·rules·settings·CLAUDE.md) 작성 원칙·배치 기준·종류별 작성법과 템플릿 |
| `skills/feedback` | 하네스 결함 사례를 프로젝트 `.claude/FEEDBACK.md`에 기록 |
| `skills/diagnose` | 증상(Crashlytics·제보)에서 원인을 특정해 보고 |
| `hooks/model-review.py` | SessionStart — 모델 별칭이 가리키는 모델이 바뀌면 하네스 재검토를 요청. 상태는 프로젝트 `.claude/model-review.txt` |
| `hooks/skill-required.py` | PreToolUse — 지정 스킬을 로드하지 않은 도구 호출 차단 (플러그인에서는 crashlytics → diagnose) |
| `hooks/write-scope.py` | 에이전트 frontmatter 훅용 — 허용 경로 밖 Edit/Write 차단 |

`skill-required.py`·`write-scope.py`는 프로젝트 settings.json·에이전트 frontmatter에서도 쓰는데, 그 자리에서는 `${CLAUDE_PLUGIN_ROOT}`가 풀리지 않는다. 프로젝트 `.claude/hooks/`에 복사해 쓰고, 이 리포를 정본으로 유지한다.

## 설치

```
claude plugin marketplace add ronsze/MyClaudeCode      # 또는 로컬 클론 경로
claude plugin install my-claude-code@my-claude-code
```

로컬 클론 경로로 추가하면 플러그인이 그 자리에서 로드되어 편집이 다음 세션(또는 `/reload-plugins`)에 바로 반영된다.

## 검증

```
claude plugin validate .
```

훅 스크립트별 검증 명령은 각 스크립트 최상단 주석에 있다.
