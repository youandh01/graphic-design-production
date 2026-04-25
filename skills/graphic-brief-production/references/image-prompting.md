# Image Prompting

Build prompts only from confirmed details. If a useful prompt element is missing, ask or present options.

Do not invent:

- medium or platform
- age, gender, ethnicity, body type
- color palette
- camera angle or composition
- historical/cultural symbols
- identity, culture, occupation, accessibility, or disability markers
- text content
- brand elements

## Prompt Fields

- Subject
- Action
- Setting/background
- Mood
- Style/medium
- Composition
- Color/lighting, only if confirmed
- Constraints

## Template

```text
[Style/medium] of [confirmed subject] [confirmed action], [confirmed expression],
[confirmed composition/background], [confirmed mood],
[technical or delivery constraints]. Avoid [confirmed exclusions].
```

When the user works in Korean, provide Korean for review and English for image tools unless asked otherwise.

If details are missing:

```text
프롬프트를 확정하려면 확인이 필요합니다.
- 스타일: 선택 필요
- 비율/구도: 선택 필요
- 인물 세부 설정: 선택 필요
```
