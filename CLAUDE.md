# CLAUDE.md

## 프로젝트 사실

- 기본 브랜치: `master`
- 작업 브랜치: `feature/<주제>`
- 컴파일 명령: `"/Applications/IntelliJ IDEA.app/Contents/plugins/Kotlin/kotlinc/bin/kotlinc" src/*.kt -d out` (IntelliJ 번들 kotlinc, PATH에 없음)
- 빌드 명령: 컴파일 명령과 같음
- 커밋 제목: `^(Feat|Fix|Refactor|Chore|Docs|Test): `
- 계약: 다른 파일에서 호출되는 public 함수·클래스 시그니처
- 스펙 위치: `specs/`

## 프로젝트

- IntelliJ IDEA Kotlin/JVM 단일 모듈 프로젝트(Gradle 없음). 소스는 `src/`, 진입점 `src/Main.kt`.
- 하네스는 my-claude-code 플러그인이 제공한다. 이 리포의 `.claude/`에는 플러그인이 쓰는 상태 파일(`FEEDBACK.md`·`model-review.txt`)만 둔다.
