---
paths:
  - "docs/*.md"
  - "docs/**/*.md"
  - "README.md"
  - "**/README.md"
---

# 문서 작성

목적: `docs/**`와 `README.md`를 쓰기 전에 이 리포의 문서 작성 근거를 잡게 한다.

- 문서를 새로 쓰거나 수정하기 전에 <문서 인덱스 경로>의 운영 규칙을 읽고 따른다.
- 작성 기준은 대상마다 다르다 — `docs/*.md`는 <문서 작성 가이드 경로>, `docs/specs/**`는 my-claude-code 플러그인 implement 스킬의 `references/plan.md`, `README.md`는 운영 규칙의 README 항목이 기준이다.

## 검증

- 패턴: `git ls-files 'docs/*.md' '*README.md'`의 파일이 `paths` 의도와 일치하고, 그 파일을 Read할 때 이 규칙이 로드되는지 확인한다.
- 내용: 최근 수정한 `docs/*.md` 하나가 문서 작성 가이드와 어긋나지 않는지 대조한다.
