# The Month Ahead with Sky & Season (monthly series, set up 18 Oct 2026)

Every task that makes, revises or posts this series reads this doc first. Stanley's rules here are binding.
(Master copy: project doc `claude/month-ahead-series.md`; this file in the repo is kept identical.)

## What it is
A separate, premium monthly series, built to reach new people (it may be boosted as a paid ad) and send them to skyandseason.com.

**Each month (quality over quantity):**
- 1 reel, about 60 s, 1080×1920.
- 3 stories.
- 1 website report.
- Captions, alt text and promotion notes.

## Timing (Stanley, 18 Oct)
- **Generated:** the Saturday night before the Sunday review, made by the scheduled task "Sky & Season: The Month Ahead package (monthly)". That task runs on **Fable**: Stanley asked for Fable for the monthly reels only.
  - The review Sunday S is the Sunday that falls **14–20 days before the end of its month**, so the review is always at least 2 weeks before month end.
  - The task runs every Saturday at 18:17 SGT and stops at once on other weeks.
- **Reviewed:** on the Daily Reflection review page (https://claude.ai/artifact/QpsCL6WLz6iWt8RuFtJJLG), in the "The Month Ahead" section at the top.
  - The page database has collection `monthly`, doc id = target month `YYYY-MM`.
  - Status is `review`, `approved`, `changes`, `hold` or `posted`.
- **Posted:** on the **last day of the month at 21:00 SGT** (1 day before the month starts): the reel, then stories 1–3.
  - Posting is done by GitHub Actions "Post The Month Ahead" (`.github/workflows/monthly.yml`, own concurrency group).
  - It posts **only when approved**. "Not reviewed" never posts, unlike the daily posts.
- **Repo files:**
  - Schedule: `schedule/monthly/<post-date>.json`.
  - Marker: `posted/monthly/<post-date>.json`.
  - These sit in sub-folders so the daily tasks never mistake them for a day's file.
- **Upcoming dates:**

  | Month | Made | Reviewed | Posts |
  | --- | --- | --- | --- |
  | November 2026 | 18 Oct | 18 Oct (first one, a day late) | Sat 31 Oct |
  | December 2026 | Sat 14 Nov | Sun 15 Nov | Mon 30 Nov |
  | January 2027 | Sat 12 Dec | Sun 13 Dec | Thu 31 Dec |

## Calendar rules
- The Gregorian month and the BaZi (solar) month are different. Always say both.
  - The BaZi month starts at its solar term, around the 4th–8th, with the exact minute in SGT.
  - The first days of the Gregorian month still belong to the previous BaZi month.
- **Sources:**
  - Pillars come from **lunar-lite**, the engine skyandseason.com uses.
  - The solar-term minute comes from **astronomy-engine** (`tools/monthly/month.py`).
  - Finding (18 Oct): lunar-lite only works in 2-hour blocks and switches months about 1–2 hours after the true solar term (Li Dong 2026: astronomical 17:52 SGT; the engine switches in its 19:00–21:00 block). For the minute, trust the astronomy.
- Only state relationships that are in data.json, or the standard five-element symbolism:
  - Water = wealth and flow.
  - Earth stores and contains.
  - Winter = storing and rest.
  - Present it all as traditional interpretation, never guaranteed events.

## Content rules
- **Plain English** a total beginner understands. Do not mix Classic and plain wording in one line (one named pillar such as 己亥 is fine).
- **Balanced** (the good and the catch). No fear-based or sensational claims, no "unlock / manifest / destiny".
- **Fresh hook every month**, specific and stranger-friendly in the first 3 s. Never repeat a script.
- **Singapore touches** where natural (11.11, bonus season, CNY prep…).
- **Captions:**
  - 600–1100 characters + 9–12 hashtags.
  - Must include #skyandseason and #innerconstellation.
  - End with a comment prompt.
  - At most one emoji per paragraph.
- **Look:**
  - Opens on the approved Sky & Season orbit shot (`tools/assets/monthly/hook-orbit.mp4`, from "The Birth of Sky & Season").
  - Then soft lavender/dawn pages with indigo type and gold accents.
  - Graphics are Noto emoji for elements and animals, the same style as the daily posts.
  - Closes on a clean indigo page with the logo, gold wordmark and website (no stickers, no childish end card).
- **Music:** a warm, bright bed of real sampled harp, piano and flute (`tools/monthly/music.py`, MIT samples, advert-safe). Never dark music. Stanley may swap in a trending sound in the app.

### Reel script blocks and character limits
| Time | Block | Contents |
| --- | --- | --- |
| 0–5.7 s | hook | 2 lines, each ≤ 30 characters |
| 5.7–17 s | energy | sky ≤ 40, season ≤ 40, image ≤ 45, meaning ≤ 80 |
| 17–34 s | themes | 3 themes (Career & money, Relationships, Personal growth), each {area, headline ≤ 28, line ≤ 80} |
| 34–46 s | opportunity, challenge | each {headline ≤ 30, line ≤ 80, tip ≤ 50} |
| 46–54 s | personal | line ≤ 60, plus day_master_lines for all 10 Day Masters (≤ 42 each, matching their month force) |
| 54–60 s | close | exactly "Your month. Your element. Your path." and "Discover your personalised monthly reading at Sky & Season." |

The renderer drops repeated labels: "Sky:" and "Season:" prefixes, "Yang Wood · The Steward:" prefixes, and numbers on the options.

### Stories
Instagram API stories cannot carry stickers.
1. **Teaser:** kicker, 2-line headline, a line, and a pointer to the reel on the feed.
2. **Question:** 4 options; people reply with the number. A `native_poll` version is also given so Stanley can add a real poll by hand if he wants.
3. **Conversion:** the 10 Day Masters with their month force, "Discover Your Monthly Energy", and "Free at the link in bio · skyandseason.com".

### content.json keys
`hook[2]`, `energy{sky, season, image, meaning}`, `themes[3]`, `opportunity`, `challenge`, `personal{line, day_master_lines{10}}`, `close[2]`, `stories{teaser, question{question, options[4], reply_line, native_poll}, conversion}`, `reel_caption`, `alt_text`, `story_alt[3]`, `report_md`, `promotion`, `qa`.

- **report_md** is 1,500–2,200 words. Sections:
  1. Monthly energy overview.
  2. The month pillar (stem, branch, hidden stems).
  3. Solar-term dates (Gregorian vs BaZi, SGT, including the mid-month term).
  4. Five Element interactions (month stem vs branch, month vs year).
  5. Career and wealth.
  6. Relationships and personal development.
  7. Twelve zodiac animals.
  8. Ten Day Masters.
  9. Practical guidance (5–7 bullets).
  10. A traditional-interpretation note and a link line.
- **qa** lists every factual claim with its data.json field.

## Making a package (the Fable task)
1. Set the target month M (the month after review Sunday S's month) and post date L (the last day of S's month).
2. Attach and clone `stanleychinyy-web/skyandseason-social` (add_repo, push access). If the push is refused, write the files to a project doc as a fallback and say so loudly.
3. Run `cd tools/reels && npm install`, then `pip install --break-system-packages astronomy-engine cairosvg pillow`.
4. Run `python3 tools/monthly/month.py M > monthly/M/data.json`. Check `checks.month_pillar_changes_around_term` is true.
5. Read the last two `monthly/*/content.json` files so the hook and themes don't repeat. Then write `monthly/M/content.json`, validating JSON and every limit.
6. Run `python3 tools/monthly/render.py M` (it also writes `media/L/monthly-*`). Look at frames at 2, 10, 20, 30, 40, 50 and 58 s and at all 3 stories. Fix anything cut off, then re-render.
7. Write `schedule/monthly/L.json` with `status: "review"` and the `monthly` and `stories` entries, then commit and push.
8. **Review page:** publish `monthly/M/reel.mp4`, `cover.jpg` and `story1-3.jpg` under the page paths `monthly/M/...` (files only, omit capabilities). Then write doc `monthly/M`:
   - `label` "Month name YYYY", `month`, `post_date` L, `status` "review", `note` "".
   - `reel`, `cover`, `stories[3]` (page paths).
   - `hook`, `pillar_line` (e.g. "己亥 · Yin Earth over the Pig · from Sat 7 Nov 5:52 PM SGT"), `facts` [[label, text]].
   - `caption`, `poll`, `report_md`, `report_words`, `promotion_md`.
9. Tell Stanley it is ready, with the hook, the post date and the review link.

## Approval, changes and posting
- **Sync:** the sync task (05:17, 12:17, 21:17 SGT) copies the page doc's status and caption into `schedule/monthly/L.json`.
- **Changes:** for a `changes` request it revises `content.json`, re-renders, republishes and sets status back to `review`.
- **Posted:** after posting it marks the doc `posted` with permalinks from `posted/monthly/L.json`.
- **Paid promotion:** never boost or commit a budget without Stanley's explicit OK. The package's promotion notes are a starting point.

## Limits (be honest about these)
- The API cannot add stickers (poll or link) or licensed trending music. Story 2 asks for replies; a native poll can be added by hand.
- The website report is in the package (`monthly/M/report.md` and on the review page). It is **not yet published on skyandseason.com**; that needs Stanley's go-ahead for a site change.
- Performance numbers (reach, watch time, saves) need the `instagram_business_manage_insights` permission, which the app does not have yet. Until it does, review performance in the Instagram app.
