# Sky & Season · Daily Reflection

Automatic daily Instagram posting for [@theskyandseason](https://www.instagram.com/theskyandseason/).

- `schedule/<date>.json` holds each day's caption, approval status and media paths. Claude writes these after Stanley's Sunday review.
- `media/<date>/` holds the reel (`reel.mp4`) and three stories (`story1-3.jpg`).
- **Post Daily Reflection** (GitHub Actions) publishes today's reel and stories at **06:00 Singapore time** through Instagram's official API, then records the result in `posted/<date>.json`. Instagram's API can't schedule posts, and GitHub often starts scheduled jobs hours late, so the job starts early (01:00 and 03:00), uploads everything, waits, and publishes at exactly 06:00. Just before publishing it re-checks the newest schedule, so a late hold or caption edit still counts. A safety-net run at 06:30 posts immediately if nothing went out; a day is never skipped. A manual run (Actions → Run workflow) publishes immediately.
- **Refresh Instagram token** runs weekly and keeps the token alive.

Status values: `pending` / `approved` post on the day; `hold` and `changes` do not.

Secrets (Settings → Secrets and variables → Actions): `IG_ACCESS_TOKEN` (required), `GH_PAT` (optional, lets the weekly refresh save a renewed token).
