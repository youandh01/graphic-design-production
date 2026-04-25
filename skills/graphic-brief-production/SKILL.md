---
name: graphic-brief-production
description: Convert rough graphic design ideas into clarified production briefs, focused questions, image-generation prompts, and Photoshop/Illustrator work directions without inventing missing details. Use for posters, SNS graphics, banners, thumbnails, character illustrations, caricatures, campaign visuals, brand graphics, and other visual concepts before design production.
---

# Graphic Brief Production

## Core Rule

Do not silently complete missing brief details. Separate confirmed information from missing information. If missing information affects representation, composition, style, medium, size, text, deliverables, or accessibility, ask concise clarification questions before final production directions.

If the user asks for a draft anyway, proceed in fast draft mode and label unresolved details as options or confirmation needed.

When the user writes in Korean, respond in Korean unless they ask for another language.

## Response Modes

- Clarification mode: Use when missing details block a reliable brief. Ask only 3-5 high-impact questions.
- Fast draft mode: Use when the user says "draft", "rough", "quick", "for now", "일단", "초안", or similar. Produce a useful draft with unresolved details marked.
- Production brief mode: Use when enough information exists to create work directions for a designer.
- Prompt mode: Use when the user specifically needs an image-generation prompt.

If multiple modes apply, start with the user's explicit need.

## Workflow

1. Extract only confirmed details.
2. Identify missing details that affect production.
3. Choose the response mode.
4. Load `references/media-templates.md` for medium-specific questions and deliverables.
5. Load `references/representation-risk-checks.md` only when people, identity, culture, occupation, public issues, or sensitive social context appears.
6. Load `references/image-prompting.md` only when image-generation prompts are useful or requested.
7. Add accessibility text only when the output is public-facing, web/SNS, report, or presentation material.

## Output Shapes

Clarification:

```text
확정된 정보
- ...

확인이 필요한 정보
- ...

질문
1. ...
2. ...
3. ...
```

Fast draft:

```text
확정된 정보
- ...

미확정 항목
- ...

초안 방향
- 구도:
- 스타일 선택지:
- 작업 메모:

다음 결정
1. ...
2. ...
3. ...
```

Production brief:

```text
제작 브리프
- 목적:
- 대상:
- 매체:
- 구성:
- 스타일:
- 텍스트:
- 기술 메모:

작업 지시
- Photoshop:
- Illustrator:

프롬프트
- Korean:
- English:

접근성 문구
- ...
```

## Guardrails

- Do not invent demographics, body type, ethnicity, age, gender, role, cultural markers, color palette, medium, or size.
- Do not assume "caricature" means ridicule; ask for exaggeration level.
- Do not turn public or social topics into pity, shock, comedy, propaganda, or exaggerated tragedy unless clearly requested and appropriate.
- Do not finalize print or SNS specs without medium-specific requirements.
