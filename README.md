# Kokoro TTS for Home Assistant

Home Assistant용 로컬 Kokoro TTS 통합구성요소입니다. 개인 서버에서 실행 중인 Kokoro TTS HTTP API를 호출해 WAV 음성을 생성합니다.

## 설치

HACS → Integrations → Custom repositories에서 이 저장소 URL을 추가하고 `Integration` 유형으로 설치합니다. Home Assistant를 재시작한 뒤 **설정 → 기기 및 서비스 → 통합구성요소 추가 → Kokoro TTS**를 선택합니다.

## 설정

- API URL: Kokoro API 주소 (예: `http://tts-server:8090`)
- Persona: `assistant`, `announcer`, `friendly` 중 하나

## 자동화 예시

```yaml
action:
  - service: tts.speak
    target:
      entity_id: tts.kokoro_tts
    data:
      media_player_entity_id: media_player.living_room
      message: "현관문이 열렸습니다."
      options:
        persona: announcer
```

이 저장소에는 개인 IP, 토큰, 계정 정보, 생성 음성 파일을 포함하지 않습니다. API 서버는 개인 네트워크에서만 노출하세요.
