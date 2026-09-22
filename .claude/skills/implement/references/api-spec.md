# API 스펙 확인 (AI 세션용)

목적: 새 API 연동·DTO 검토 전에 실제 응답 스키마를 얻는 방법을 정한다. implement ①·② 또는 code-reviewer가 DTO를 다룰 때 읽는다. 사람용 규칙(`required` 미신뢰, 기본값)은 `docs/NETWORKING.md`의 "스펙 확인" 절이 정본이며 여기서 복제하지 않는다.

## swagger MCP 도구를 호출하지 않습니다

두 가지 이유입니다.

1. 이 MCP 서버의 도구는 **요청 파라미터만 노출하고 응답 스키마를 노출하지 않습니다.** 도구 설명을 읽어도 응답 필드를 알 수 없습니다.
2. **호출하면 실제 dev 서버에 요청이 나갑니다.** 결제·예약·회원 삭제 계열은 실제 변경을 일으킵니다. `.claude/settings.json`의 `permissions.deny`가 swagger 서버의 모든 도구를 차단합니다.

## OpenAPI 문서를 직접 파싱합니다

URL의 정본은 `.mcp.json`의 `API_SPEC_URL` 하나입니다 — 여기에 URL을 적지 않고 읽어서 씁니다. 300KB가 넘으므로 전문을 읽지 말고 대상 경로만 뽑습니다.

```bash
python3 - <<'PY'
import json, urllib.request
url = json.load(open('.mcp.json'))['mcpServers']['swagger']['env']['API_SPEC_URL']
spec = json.load(urllib.request.urlopen(url))
print(json.dumps(spec['paths']["/api/v1/대상/경로"], indent=2, ensure_ascii=False)[:4000])
PY
```

결과 코드의 의미는 `components.schemas."kr.iamground.global.http.ErrorCode".enum`에 `[코드] 메시지` 형태로 들어 있습니다. 엔드포인트별 `description`에는 결과 코드가 없으므로 이 enum이 단일 소스입니다.

