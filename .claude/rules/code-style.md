---
paths:
  - "**/*.kt"
---

# 코드 스타일

목적: Kotlin 코드를 쓰기 전에 이 리포의 표기 규칙을 근거로 삼게 한다.

- `.kt` 파일을 새로 쓰거나 수정하기 전에 `docs/CODE_STYLE.md`를 읽고 그 규칙을 따른다.
- 계층 책임·모듈 의존·UseCase/Repository 추가는 `docs/ARCHITECTURE.md`, 화면 추가·이동은 `docs/NAVIGATION.md`, 새 API 연동은 `docs/NETWORKING.md`가 기준이다.
- 규칙과 주변 코드가 어긋나면 그 파일의 주변 코드를 따른다.

## 검증

- 패턴: `git ls-files '*.kt' | head`의 파일이 `paths` 의도와 일치하고, `.kt` 파일을 Read할 때 이 규칙이 로드되는지 확인한다.
- 내용: 최근 수정한 `.kt` 파일 하나가 `docs/CODE_STYLE.md`와 어긋나지 않는지 대조한다.
