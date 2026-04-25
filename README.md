# Graphic Design Production

Codex plugin for graphic designers who use Photoshop and Illustrator.

## Skills

- `$graphic-brief-production`: clarify rough visual ideas into production briefs, focused questions, image prompts, and work directions.
- `$graphic-delivery-audit`: inspect delivery folders for naming risks, file metadata, manifests, export dimensions, and handoff risks.

## Structure

```text
.codex-plugin/plugin.json
skills/
  graphic-brief-production/
  graphic-delivery-audit/
```

## Install

Clone or copy this repository into your local Codex plugin folder:

```powershell
git clone https://github.com/youandh01/graphic-design-production.git "$env:USERPROFILE\.codex\plugins\graphic-design-production"
```

For the most reliable automatic skill triggering, also copy the two skills into your user skill folder:

```powershell
Copy-Item "$env:USERPROFILE\.codex\plugins\graphic-design-production\skills\graphic-brief-production" "$env:USERPROFILE\.codex\skills\graphic-brief-production" -Recurse -Force
Copy-Item "$env:USERPROFILE\.codex\plugins\graphic-design-production\skills\graphic-delivery-audit" "$env:USERPROFILE\.codex\skills\graphic-delivery-audit" -Recurse -Force
```

Restart Codex or start a new chat after installing.

## Usage

Use `$graphic-brief-production` for rough ideas:

```text
장애인의 날 포스터용 캐리커처 제작 브리프로 정리해줘.
```

Use `$graphic-delivery-audit` for real files or folders:

```text
이 납품 폴더를 검수하고 파일명, 사이즈, manifest를 확인해줘: C:\path\to\delivery
```

## Development

Treat this repository as the source of truth. The copies under `~/.codex/skills` are local registration copies for better automatic triggering.

After editing files in this repository, sync the local skill copies:

```powershell
.\scripts\sync-local-skills.ps1
```

## Notes

The delivery audit scripts are best-effort metadata tools. PSD, PSB, AI, EPS, TIFF, INDD, and IDML files are marked as limited inspection unless a specialized parser is available.
