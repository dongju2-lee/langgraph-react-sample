# 가전제품 기기를 제어할 수 있도록 테스트하는 목서버

## 가전제품 상태 확인 API

각 가전제품은 상태 확인을 위한 API를 제공합니다. 상태 확인 API는 일반적으로 다음과 같은 정보를 제공합니다:
- 전원 상태
- 현재 작동 상태
- 세부 설정 정보
- 사용자 친화적인 상태 메시지

## 냉장고
냉장고 전체 상태 조회 (식재료, 디스플레이, 요리 상태 등 전체 정보)
```
curl -X GET "http://localhost:10000/refrigerator/status"
```
응답 예시:
```json
{
  "food_items_count": 7,
  "food_categories": {"육류": 1, "채소": 2, "유제품": 2, "기타": 2},
  "food_items": [
    {"name": "계란", "quantity": "10개", "category": "기타"},
    {"name": "소고기", "quantity": "500g", "category": "육류"}
  ],
  "display_state": "on",
  "display_content": "오늘의 추천 요리: 비프 스테이크",
  "cooking_state": "대기중",
  "door_status": "closed",
  "temperature": {"fridge": 3, "freezer": -18},
  "message": "현재 7개 식재료(육류 1개, 채소 2개, 유제품 2개, 기타 2개)가 보관 중입니다. 디스플레이가 켜져 있고 '오늘의 추천 요리: 비프 스테이크'를 표시 중입니다. 요리가 대기 중입니다."
}
```

냉장고 디스플레이 요리 상태 조회
```
curl -X GET "http://localhost:10000/refrigerator/cooking-state"
```

냉장고 디스플레이에 레시피 정보 설정
```
curl -X POST "http://localhost:10000/refrigerator/cooking-state" -H "Content-Type: application/json" -d '{"step_info":"계란을 삶아서 껍질을 벗깁니다."}'
```

## 전자레인지
전자레인지 상태 조회
```
curl -X GET "http://localhost:10000/api/microwave/status"
```
응답 예시:
```json
{
  "power": true,
  "cooking": true,
  "remaining_seconds": 45,
  "message": "조리 중: 남은 시간 45초"
}
```
또는 (조리 중이 아닌 경우):
```json
{
  "power": true,
  "cooking": false,
  "message": "전원이 켜져 있으나 조리 중이 아닙니다."
}
```

전자레인지 켜기
```
curl -X POST "http://localhost:10000/microwave/power/state" -H "Content-Type: application/json" -d '{"power_state":"on"}'

```

전자레인지 모드 확인
```
curl -X GET "http://localhost:10000/microwave/mode"
```

전자레인지 가능한 모드 목록 조회
```
curl -X GET "http://localhost:10000/microwave/mode/list"
```

전자레인지 모드 변경 (microwave 모드)
```
curl -X POST "http://localhost:10000/microwave/mode" -H "Content-Type: application/json" -d '{"mode":"microwave"}'
```

전자레인지 모드 변경 (baking 모드)
```
curl -X POST "http://localhost:10000/microwave/mode" -H "Content-Type: application/json" -d '{"mode":"baking"}'
```

전자레인지 모드 변경 (grilling 모드)
```
curl -X POST "http://localhost:10000/microwave/mode" -H "Content-Type: application/json" -d '{"mode":"grilling"}'
```

전자레인지 모드 변경 (oven 모드)
```
curl -X POST "http://localhost:10000/microwave/mode" -H "Content-Type: application/json" -d '{"mode":"oven"}'
```

전자레인지 레시피 스텝 정보 설정
```
curl -X POST "http://localhost:10000/microwave/step-info" -H "Content-Type: application/json" -d '{"step_info":"cut flank steak in thin slices"}'
```

전자레인지 조리 시작 (타이머 설정)
```
curl -X POST "http://localhost:10000/microwave/start-cooking" -H "Content-Type: application/json" -d '{"timer":30}'
```

전자레인지 끄기
```
curl -X POST "http://localhost:10000/microwave/power/state" -H "Content-Type: application/json" -d '{"power_state":"off"}'
```

## 인덕션
인덕션 상태 조회
```
curl -X GET "http://localhost:10000/api/induction/status"
```
응답 예시:
```json
{
  "power": true,
  "cooking": true,
  "heat_level": "HIGH",
  "message": "인덕션이 강불로 조리 중입니다."
}
```
또는 (전원이 꺼진 경우):
```json
{
  "power": false,
  "cooking": false,
  "heat_level": null,
  "message": "인덕션 전원이 꺼져 있습니다."
}
```

인덕션 켜기
```
curl -X POST "http://localhost:10000/induction/power/state" -H "Content-Type: application/json" -d '{"power_state":"on"}'
```

인덕션 조리 시작 (타이머 설정)
```
curl -X POST "http://localhost:10000/induction/start-cooking" -H "Content-Type: application/json" -d '{"timer":30}'
```

인덕션 끄기
```
curl -X POST "http://localhost:10000/induction/power/state" -H "Content-Type: application/json" -d '{"power_state":"off"}'
```

## TV
TV 상태 조회
```
curl -X GET "http://localhost:10000/tv/status"
```
응답 예시:
```json
{
  "power": true,
  "current_channel": "EBC",
  "volume": 7,
  "message": "TV가 켜져 있으며 EBC 채널을 시청 중입니다. 볼륨은 7입니다."
}
```

TV 전원 켜기/끄기
```
curl -X POST "http://localhost:10000/tv/power" -H "Content-Type: application/json" -d '{"power_state":"on"}'
```

TV 채널 변경
```
curl -X POST "http://localhost:10000/tv/channel" -H "Content-Type: application/json" -d '{"channel":"EBC"}'
```

TV 볼륨 조절
```
curl -X POST "http://localhost:10000/tv/volume" -H "Content-Type: application/json" -d '{"level":10}'
```

TV 채널 목록 조회
```
curl -X GET "http://localhost:10000/tv/channels"
```

## 조명
조명 상태 조회
```
curl -X GET "http://localhost:10000/light/status"
```
응답 예시:
```json
{
  "power": true,
  "brightness": 75,
  "color": "warm",
  "mode": "relaxation",
  "message": "조명이 켜져 있으며, 밝기 75%, 따뜻한 색상, 휴식 모드입니다."
}
```

조명 전원 켜기/끄기
```
curl -X POST "http://localhost:10000/light/power" -H "Content-Type: application/json" -d '{"power_state":"on"}'
```

조명 밝기 조절
```
curl -X POST "http://localhost:10000/light/brightness" -H "Content-Type: application/json" -d '{"level":80}'
```

조명 색상 변경
```
curl -X POST "http://localhost:10000/light/color" -H "Content-Type: application/json" -d '{"color":"warm"}'
```

조명 모드 변경
```
curl -X POST "http://localhost:10000/light/mode" -H "Content-Type: application/json" -d '{"mode":"study"}'
```

## 커튼
커튼 상태 조회
```
curl -X GET "http://localhost:10000/curtain/status"
```
응답 예시:
```json
{
  "is_open": true,
  "position": 50,
  "power_state": "open",
  "scheduled_action": {"time": "08:00", "action": "open"},
  "message": "커튼이 50% 열려 있습니다. 08:00에 자동으로 열리도록 설정되어 있습니다."
}
```

커튼 열기/닫기
```
curl -X POST "http://localhost:10000/curtain/power" -H "Content-Type: application/json" -d '{"power_state":"open"}'
```

커튼 위치 조절
```
curl -X POST "http://localhost:10000/curtain/position" -H "Content-Type: application/json" -d '{"percent":50}'
```

커튼 스케줄 설정
```
curl -X POST "http://localhost:10000/curtain/schedule" -H "Content-Type: application/json" -d '{"time":"08:00", "action":"open"}'
```

## 오디오
오디오 상태 조회
```
curl -X GET "http://localhost:10000/audio/status"
```
응답 예시 (재생 중):
```json
{
  "playing": true,
  "volume": 7,
  "current_playlist": "명상",
  "current_song": "잔잔음악",
  "playlist_info": {"songs_count": 5, "total_duration": "25분"},
  "song_info": {"duration": "5:30", "artist": "힐링아티스트"},
  "power": "on",
  "message": "현재 '명상' 플레이리스트의 '잔잔음악'을 재생 중입니다. 볼륨: 7"
}
```
응답 예시 (재생 중이 아닌 경우):
```json
{
  "playing": false,
  "volume": 5,
  "current_playlist": "명상",
  "current_song": null,
  "playlist_info": {"songs_count": 5, "total_duration": "25분"},
  "song_info": null,
  "power": "on",
  "message": "'명상' 플레이리스트가 선택되었지만 재생 중이 아닙니다."
}
```
응답 예시 (전원이 꺼진 경우):
```json
{
  "playing": false,
  "volume": 0,
  "current_playlist": null,
  "current_song": null,
  "playlist_info": null,
  "song_info": null,
  "power": "off",
  "message": "오디오 전원이 꺼져 있습니다."
}
```

오디오 전원 켜기/끄기
```
curl -X POST "http://localhost:10000/audio/power" -H "Content-Type: application/json" -d '{"power_state":"on"}'
```
또는 
```
curl -X POST "http://localhost:10000/audio/power" -H "Content-Type: application/json" -d '{"power_state":"off"}'
```
응답 예시:
```json
{
  "result": "success",
  "message": "오디오 전원을 켰습니다."
}
```
또는
```json
{
  "result": "success",
  "message": "오디오 전원을 끄고 재생을 중지했습니다."
}
```

음악/플레이리스트/특정 곡 재생
```
curl -X POST "http://localhost:10000/audio/play" -H "Content-Type: application/json" -d '{"playlist":"명상"}'
```
또는
```
curl -X POST "http://localhost:10000/audio/play" -H "Content-Type: application/json" -d '{"song":"잔잔음악"}'
```

음악 정지
```
curl -X POST "http://localhost:10000/audio/stop" -H "Content-Type: application/json" -d '{}'
```

오디오 볼륨 조절
```
curl -X POST "http://localhost:10000/audio/volume" -H "Content-Type: application/json" -d '{"level":7}'
```

플레이리스트 선택
```
curl -X POST "http://localhost:10000/audio/playlist" -H "Content-Type: application/json" -d '{"playlist":"명상"}'
```

가능한 플레이리스트 목록 조회
```
curl -X GET "http://localhost:10000/audio/playlists"
```

플레이리스트 내 곡 목록 조회
```
curl -X GET "http://localhost:10000/audio/playlists/명상/songs"
```

## 푸드 매니저
냉장고 내 식재료 목록 조회
```
curl -X GET "http://localhost:10000/food-manager/ingredients"
```

식재료 기반 레시피 조회
```
curl -X GET "http://localhost:10000/food-manager/recipe" -H "Content-Type: application/json" -d '{"ingredients":["egg","beef"]}'
```

## 세션 관리
새 세션 생성
```
curl -X POST "http://localhost:10000/sessions/" -H "Content-Type: application/json" -d '{}'
```

세션 조회
```
curl -X GET "http://localhost:10000/sessions/세션ID"
```

세션 목록 조회
```
curl -X GET "http://localhost:10000/sessions/"
```

세션 업데이트 (메시지 추가)
```
curl -X PUT "http://localhost:10000/sessions/세션ID" -H "Content-Type: application/json" -d '{"messages":[{"type":"HumanMessage","content":"안녕하세요","name":"사용자","additional_kwargs":{}},{"type":"AIMessage","content":"안녕하세요! 무엇을 도와드릴까요?","name":"어시스턴트","additional_kwargs":{}}],"next":null}'
```

세션 삭제
```
curl -X DELETE "http://localhost:10000/sessions/세션ID"
```

전체 대화 흐름 테스트 (세션 생성부터 삭제까지)
```
# 1. 새 세션 생성하고 ID 저장
SESSION_ID=$(curl -s -X POST "http://localhost:10000/sessions/" | grep -o '"session_id":"[^"]*' | cut -d'"' -f4)

# 2. 세션 ID 출력
echo "생성된 세션 ID: $SESSION_ID"

# 3. 첫 번째 메시지 추가 (사용자 질문)
curl -X PUT "http://localhost:10000/sessions/$SESSION_ID" -H "Content-Type: application/json" -d "{\"messages\":[{\"type\":\"HumanMessage\",\"content\":\"냉장고에 있는 식재료를 알려줘\",\"name\":\"사용자\",\"additional_kwargs\":{}}],\"next\":null}"

# 4. 두 번째 메시지 추가 (AI 응답)
curl -X PUT "http://localhost:10000/sessions/$SESSION_ID" -H "Content-Type: application/json" -d "{\"messages\":[{\"type\":\"HumanMessage\",\"content\":\"냉장고에 있는 식재료를 알려줘\",\"name\":\"사용자\",\"additional_kwargs\":{}},{\"type\":\"AIMessage\",\"content\":\"냉장고에는 다음 식재료가 있습니다: 계란, 빵, 소고기, 양파, 당근, 우유, 치즈\",\"name\":\"식품관리자\",\"additional_kwargs\":{}}],\"next\":null}"

# 5. 세션 내용 확인
curl -X GET "http://localhost:10000/sessions/$SESSION_ID"

# 6. 세션 삭제
curl -X DELETE "http://localhost:10000/sessions/$SESSION_ID"
```

## 루틴
루틴 등록
```
curl -X POST "http://localhost:10000/routine/register" -H "Content-Type: application/json" -d "{\"routine_name\": \"cooking_mode\", \"routine_flow\": [\"1. 냉장고에서 계란을 꺼낸다\", \"2. 전자레인지를 켠다\", \"3. 인덕션을 켠다\"]}"
```

루틴 목록 조회
```
curl -X GET "http://localhost:10000/routine/list"
```

루틴 삭제
```
curl -X POST "http://localhost:10000/routine/delete" -H "Content-Type: application/json" -d "{\"routine_name\": \"cooking_mode\"}"
```

## 사용자
사용자 개인화 정보 조회
```
curl -X GET "http://localhost:10000/user/personalization"
```

사용자 개인화 정보 추가
```
curl -X POST "http://localhost:10000/user/personalization" -H "Content-Type: application/json" -d '{"info":"좋아하는 음식은 김치찌개"}'
```

사용자 캘린더 정보 조회
```
curl -X GET "http://localhost:10000/user/calendar"
```

사용자 캘린더 이벤트 추가
```
curl -X POST "http://localhost:10000/user/calendar" -H "Content-Type: application/json" -d '{"day":"day15","time":"14:00","info":"가족 고기파티 모임"}'
```

사용자 메시지 정보 조회
```
curl -X GET "http://localhost:10000/user/message"
```

사용자 메시지 추가
```
curl -X POST "http://localhost:10000/user/message" -H "Content-Type: application/json" -d '{"message_name":"카드 결제 알림","data":"2025-04-20:15:30:00","message_body":"25일 오후 6시에 한국카드 사용요금인 125만원이 출금될 예정입니다. 통장에 충분한 돈을 넣어놓으시기 바랍니다"}'
```
