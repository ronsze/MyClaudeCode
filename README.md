# my-claude-code

Claude Code 플러그인. 코드 변경·병합·진단·리뷰·테스트·문서 동기화 절차와 하네스 작성 규율을 프로젝트에 무관한 형태로 담는다. 프로젝트 고유 값은 각 프로젝트의 CLAUDE.md `## 프로젝트 사실` 절과 `.claude/` 오버레이 파일에 둔다.

## 구성

| 구성요소 | 역할 |
|---|---|
| `skills/implement` | 코드 변경 요청을 수준(탐색·경미·경계 내·표준·복합)에 맞는 단계 조합으로 수행. 복합 계획 파일 형식은 `references/plan.md` |
| `skills/merge` | `/merge` — 브랜치 병합과 사전 검사·빌드·테스트·문서 정합성 게이트. 프로젝트 고유 게이트는 `.claude/merge-gates.md` |
| `skills/diagnose` | 증상(Crashlytics·제보)에서 원인을 특정해 보고 |
| `skills/trello` | Trello 보드 카드·댓글 작업. 보드 규약은 `.claude/trello.md` |
| `skills/harness` | 하네스 구성요소 작성 원칙·배치 기준·종류별 작성법과 템플릿 |
| `skills/feedback` | 하네스 결함 사례를 프로젝트 `.claude/FEEDBACK.md`에 기록 |
| `agents/code-reviewer` | 변경 코드를 6기준으로 점검해 발견 목록 보고 (읽기 전용) |
| `agents/test-engineer` | 지정 범위의 단위 테스트 실행·작성·보수 (테스트 소스만 수정) |
| `agents/docs-sync` | 문서–코드–하네스 정합성 검토, 사실 불일치는 문서 수정 (문서만 수정) |
| `agents/figma-matcher` | Figma 시안 요소를 기존 UI 컴포넌트와 대조해 재사용·확장·신규 판정 |
| `hooks/model-review.py` | SessionStart — 모델 별칭이 가리키는 모델이 바뀌면 하네스 재검토를 요청. 상태는 프로젝트 `.claude/model-review.txt` |
| `hooks/skill-required.py` | PreToolUse — 지정 스킬을 로드하지 않은 도구 호출 차단 (crashlytics → diagnose, trello → trello) |
| `hooks/write-scope.py` | PreToolUse Edit\|Write — 에이전트별 허용 경로 밖 수정 차단 (docs-sync·test-engineer). 범위 변경은 `.claude/write-scope.json` |
| `templates/rules/` | 프로젝트 `.claude/rules/`에 복사해 채우는 경로 규칙 (플러그인은 rules를 실을 수 없다) |

## 프로젝트 쪽에 두는 것

| 파일 | 내용 | 형식 |
|---|---|---|
| `CLAUDE.md` `## 프로젝트 사실` | 기본 브랜치, 컴파일·빌드·테스트 명령, 커밋 제목 형식, 계약 정의, 문서 경로 등 | `skills/harness/references/claude-md.md`의 항목 표 |
| `.claude/trello.md` | 보드·멤버·라벨 id, 카드·댓글 형식 | `skills/trello/references/trello.md` |
| `.claude/merge-gates.md` | 프로젝트 고유 병합 사전 검사 | `skills/merge/references/merge-gates.md` |
| `.claude/write-scope.json` | 에이전트별 수정 허용 경로 재정의 (선택) | `{"test-engineer": ["<정규식>", "!<제외>"]}` |
| `.claude/FEEDBACK.md` | 하네스 결함 기록 | feedback 스킬이 템플릿에서 만든다 |
| `.claude/rules/*.md` | 경로 규칙 | `templates/rules/`에서 복사 |

구성요소는 필요한 항목이 없으면 추측하지 않고 묻는다.

`skill-required.py`·`write-scope.py`를 프로젝트 settings.json·프로젝트 에이전트 frontmatter에서 쓰려면 `${CLAUDE_PLUGIN_ROOT}`가 풀리지 않으므로 `.claude/hooks/`에 복사해 쓰고, 이 리포를 정본으로 유지한다.

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
