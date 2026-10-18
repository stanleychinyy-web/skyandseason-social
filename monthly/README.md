# The Month Ahead with Sky & Season (monthly flagship series)

Set up 18 Oct 2026 at Stanley's request. One premium reel (about 60 s) and 3 stories a month, plus a website report.
The project doc `claude/month-ahead-series.md` holds the full brief and rules; this file is the quick technical map.

## Timing (Stanley's rules)
- **Made:** the Saturday before review Sunday S, where S is the Sunday that falls 14–20 days before the end of S's month.
  The scheduled task "The Month Ahead package" (model Fable) runs every Saturday 18:17 SGT and exits on other weeks.
- **Reviewed:** on Sunday S, on the Daily Reflection review page (section "The Month Ahead"), at least 2 weeks before month end.
- **Posted:** on the last day of the month at 21:00 SGT (the day before the month starts): the reel, then the 3 stories.
  It only posts when the review status is `approved`.

## Lens
Inner Constellation on both halves (essence painting + season painting). See SERIES.md.

## Files
- `monthly/<YYYY-MM>/data.json`: validated facts from `tools/monthly/month.py` (lunar-lite pillars, astronomy-engine solar-term minute, SGT).
- `monthly/<YYYY-MM>/content.json`: the script, stories, captions, report and promotion notes (written by the Fable task).
- `monthly/<YYYY-MM>/reel.mp4`, `cover.jpg`, `story1-3.jpg`, `report.md`, `promotion.md`: rendered by `tools/monthly/render.py`.
- `media/<post-date>/monthly-*`: the copies that get posted.
- `schedule/monthly/<post-date>.json`: `{date, status: review|approved|hold|changes, kind: "month-ahead", month, monthly: {type: "reel", video, cover, caption}, stories: [3]}`.
- `posted/monthly/<post-date>.json`: written by the workflow.
- `.github/workflows/monthly.yml`: "Post The Month Ahead", daily crons 17:00 / 19:00 / 21:30 SGT, publishes at 21:00, own concurrency group.

## Commands (repo root)
```
cd tools/reels && npm install && cd ../..
pip install --break-system-packages astronomy-engine cairosvg pillow
python3 tools/monthly/month.py 2026-12 > monthly/2026-12/data.json
python3 tools/monthly/render.py 2026-12            # reel + stories (about 2 minutes)
python3 tools/monthly/render.py 2026-12 stories    # stories only
```
