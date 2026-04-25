---
name: graphic-delivery-audit
description: Audit real graphic design delivery folders and final files for file naming, dimensions, formats, source/export coverage, manifest creation, and Photoshop/Illustrator handoff risks. Use when the user provides a folder or asks to inspect, check, validate, package, export, hand off, or prepare final design files for delivery.
---

# Graphic Delivery Audit

## Scope

Use this skill for actual file/folder checks and delivery readiness. Do not use it for early creative brief discussion; use `$graphic-brief-production` for that.

When the user writes in Korean, respond in Korean unless they ask for another language.

## Workflow

1. Identify the delivery context: print, web/SNS, source handoff, client preview, or mixed package.
2. If a folder path is provided, run the relevant bundled scripts.
3. If expected sizes are provided, compare actual exports against them.
4. Summarize findings as risks and next actions, not as a raw dump.
5. Mark unknown or uninspectable items clearly instead of treating them as passed.

## Scripts

Use scripts without reading them unless behavior needs to change.

- `scripts/inspect_assets.py <folder> --csv`: Inspect image, SVG, PDF, PSD/PSB, AI/EPS, TIFF, and common delivery files. Some formats are listed as inspection-limited.
- `scripts/check_naming.py <folder> --csv`: Check filename risks. Add `--fail-on-issues` when automation should fail on flagged files.
- `scripts/make_delivery_manifest.py <folder>`: Create `manifest.csv` inside the inspected folder by default.
- `scripts/compare_export_sizes.py <folder> --expect expected-sizes.csv --csv`: Compare actual export dimensions to expected sizes.

Expected sizes CSV format:

```csv
path,width,height
instagram-feed.png,1080,1080
story.png,1080,1920
```

## Output Shape

```text
검수 범위
- ...

실행한 검사
- ...

문제 가능성
- ...

확인 필요
- ...

권장 조치
1. ...
2. ...
3. ...
```

## Guardrails

- Do not claim a source file passed visual/layer/font checks if the script only inspected metadata.
- Do not infer print compliance without printer specs.
- Do not infer platform compliance without expected dimensions or platform placement.
- Treat PSD, PSB, AI, EPS, and TIFF metadata as limited inspection unless a specialized parser is available.
