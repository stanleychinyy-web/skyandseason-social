# Sky & Season · Daily Reflection

Automatic daily Instagram posting for [@theskyandseason](https://www.instagram.com/theskyandseason/).

- `schedule/<date>.json` holds each day's caption, approval status and media paths. Claude writes these after Stanley's Sunday review.
- `media/<date>/` holds the reel (`reel.mp4`) and three stories (`story1-3.jpg`).
- **Post Daily Reflection** (GitHub Actions) runs at about 05:50 Singapore time, with a retry at 08:20. It posts today's reel and stories through Instagram's official API, then records the result in `posted/<date>.json`.
- **Refresh Instagram token** runs weekly and keeps the token alive.

Status values: `pending` / `approved` post on the day; `hold` and `changes` do not.

Secrets (Settings → Secrets and variables → Actions): `IG_ACCESS_TOKEN` (required), `GH_PAT` (optional, lets the weekly refresh save a renewed token).
