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
- data.json now carries the Inner names too: `bazi_month.stem_inner` (e.g. "The Nurturing Garden"), `stem_inner_short`, `season` (e.g. "The Bare Ground") and `season_stage`.
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
- **Look (v2, 18 Oct; Stanley rejected v1 as "primary school"):** premium and dark. Deep indigo with a violet glow; the site's own Inner Constellation oil paintings (`tools/assets/art/inner-stems/<slug>.jpg` for the element's essence, `art/inner-branches/<slug>.jpg` for the season; the Classic sets in `art/stems` and `art/branches` are not used unless the lens is switched) for the month's element and season, framed with a thin gold line and a slow push-in; a blurred echo of the painting as atmosphere behind the type; Newsreader serif in soft white, gold kickers and hairline rules; gold dust. **No emoji, no cartoon icons, no stickers, no title cards.** Opens on the approved Sky & Season orbit shot; closes on a clean indigo page with the logo mark, gold wordmark and website.
- **Music:** a warm, bright bed of real sampled harp, piano and flute (`tools/monthly/music.py`, MIT samples, advert-safe). Never dark music. Stanley may swap in a trending sound in the app.

### Copy rules (v2, binding)
- **One lens, both halves (Stanley, 18 Oct: "If the heaven pillar is Inner Constellation, the earth branch also has to be Inner. If not it is confusing").** The reel, the stories and the body of the report use the **Inner Constellation lens for both the element and the season**: the stem's essence name and painting (Yin Earth = "The Nurturing Garden", `tools/assets/art/inner-stems/<slug>.jpg`) and the branch's season name and painting ("The Bare Ground", `tools/assets/art/inner-branches/<slug>.jpg`). **No animals, no stem-god names ("The Fertile Field"), no Chinese characters on screen.** The Classic names (pillar 己亥, The Fertile Field, the Pig, the twelve animals' relations) live only in the report's final section "The classic view, if you know the animals". The renderer reads `"lens"` from content.json and defaults to `inner`; `classic` exists only in case Stanley ever asks for that look, and then it must be classic on both halves.
- **Every concept is explained in the sentence it appears in.** "Yin Earth" is always followed by what it is in everyday words. The labels "The month's element · what we call the Sky" and "The month's animal · what we call the Season" are drawn under the names.
- **No ten-god / force names in the reel or stories** (no "The Steward", "The Muse"…). The reel's personal part is **five element groups** ("Wood people: a money month…"), which is honest because both yin and yang Day Masters of an element get the same family of force. The ten-force detail lives in the website report, and even there the plain meaning comes before the name ("a steady-money force, which we call The Steward").
- The word "Day Master" is not used on screen; it is "your element: the day you were born".

### Reel script blocks and character limits (schema v2)
| Time | Block | Contents |
| --- | --- | --- |
| 0–5.7 s | hook | 2 lines, each ≤ 30 characters |
| 5.7–10 s | intro | line1 ≤ 44 ("Every month has its own element."), line2 ≤ 44 ("November's is Yin Earth.") |
| 10–16 s | sky | sky_name ≤ 24 (the Inner essence name, e.g. "The Nurturing Garden"), sky_label ≤ 46, sky_plain ≤ 64 ("Yin Earth: soft, patient soil…") |
| 16–21 s | season | season_name ≤ 24 (the Inner season name, e.g. "The Bare Ground"), season_label ≤ 46, season_plain ≤ 64 |
| 21–27 s | meaning | image ≤ 45 (one picture line), meaning ≤ 96 |
| 27–40 s | themes | 3 × {area, headline ≤ 28, line ≤ 86} |
| 40–49 s | opportunity, challenge | each {headline ≤ 30, line ≤ 86, tip ≤ 48} |
| 49–56 s | elements | intro1 ≤ 46, intro2 ≤ 46, cards Wood/Fire/Earth/Metal/Water {people ≤ 14, line ≤ 62} |
| 56–60 s | close | exactly "Your month. Your element. Your path." and "Discover your personalised monthly reading at Sky & Season." |

### Stories
Instagram API stories cannot carry stickers.
1. **Teaser:** kicker, 2-line headline, a line, and a pointer to the reel on the feed.
2. **Question:** 4 options; people reply with the number. A `native_poll` version is also given so Stanley can add a real poll by hand if he wants.
3. **Conversion:** the five element groups with their plain month line, "Discover Your Monthly Energy", and "Free at the link in bio · skyandseason.com".

### content.json keys (schema v2)
`hook[2]`, `intro{line1, line2}`, `energy{sky_name, sky_plain, sky_label, season_name, season_plain, season_label, image, meaning}`, `themes[3]`, `opportunity`, `challenge`, `elements{intro1, intro2, cards{Wood, Fire, Earth, Metal, Water: {people, line}}}`, `close[2]`, `stories{teaser{kicker ≤ 34, headline[2 ≤ 24], line ≤ 80, pointer ≤ 40}, question{question ≤ 44, options[4 ≤ 18], reply_line ≤ 40, native_poll}, conversion{headline ≤ 34, line ≤ 96, invitation, link_line}}`, `reel_caption`, `alt_text`, `story_alt[3]`, `report_md`, `promotion`, `qa`.

- **report_md** is 1,600–2,300 words. Sections:
  0. "Start here: three words": Sky = the month's element; Season = the month's animal; Day Master = your element, from the day you were born (two lines each).
  1. Monthly energy overview.
  2. The month pillar (stem, branch, hidden stems).
  3. Solar-term dates (Gregorian vs BaZi, SGT, including the mid-month term).
  4. Five Element interactions (month stem vs branch, month vs year).
  5. Career and wealth.
  6. Relationships and personal development.
  7. Your element this month: the concept first, then the five element groups, then all ten with the plain meaning before the force name.
  8. Practical guidance (5–7 bullets).
  9. "The classic view, if you know the animals": the pillar, the stem god, the animal, hidden stems, the year pillar, and the twelve animals' relations (one line each).
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
8. **Review page:** publish `cover.jpg`, `story1-3.jpg` and a preview copy of the reel under 16 MB (`ffmpeg -i reel.mp4 -vf scale=720:1280 -c:v libx264 -crf 25 -c:a aac -b:a 128k -movflags +faststart`) under the page paths `monthly/M/...` (files only, omit capabilities). Then write doc `monthly/M`:
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
