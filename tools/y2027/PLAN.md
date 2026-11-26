# The 2027 Fire Goat series (7pm Mon / Wed / Fri / Sat, 27 Nov 2026 – 31 Mar 2027)

Stanley, 26 Nov 2026: "for the 7pm reels, I want the upcoming 4 months reels to focus on the 2027 fortune, to gain attraction … do it professionally and sell our website for them to check their own year mark." Situation reels and the weekly "Which of the ten are you?" reel are paused until April 2027. Tue/Thu/Sun 7pm stay with the character reels (The Ten Mirrors). Viewable plan for Stanley: https://claude.ai/artifact/HBhyH8g6xMtKFcFmfRzE9P

## How every reel sells the site
The last card (built into `reel5.py y27`, not in the spec) is always the same three steps:
1. STEP 1 · FREE — Get your chart at skyandseason.com
2. STEP 2 — Open Calendar and go to February 2027
3. STEP 3 — See your 2027 mark: Good, Steady or Care

This is a real, live feature: the site's Calendar tints the year pillar Good / Steady / Care for a signed-in person (free account), per question (general, work, money, love, study, health). Guests see the pillar untinted, so the free account is the ask. The caption repeats it in one fixed sentence (see the Saturday batch prompt).

## Fact sheet (checked 26 Nov 2026; use only these, never invent)
- 2027 = Ding Wei: Yin Fire (a candle / lamp, warm and focused) over the Goat (Wei, warm late-summer earth; hidden Yin Earth, Yin Fire, Yin Wood).
- The year starts at the start of spring (Li Chun): **Thu 4 Feb 2027, 09:46 SGT** (astronomy-engine, solar longitude 315°). Chinese New Year: **Sat 6 Feb 2027**. People born 1 Jan to the start of spring take the previous year's animal (e.g. born 20 Jan 1991 = Horse, not Goat).
- 2026 = Bing Wu (Yang Fire Horse, the sun). Horse + Goat are a classic pair (Wu–Wei), so 2027 finishes what 2026 started. Bing Wu and Ding Wei share the hidden "sound" element (nayin) Heavenly River Water.
- The Goat and the 12 animals in 2027: Goat own year (sits with the Tai Sui); Ox clash (Chou–Wei); Rat harm (Zi–Wei); Dog punishment + break (Xu–Wei; the Ox–Dog–Goat punishment trio); Horse best partner (Wu–Wei); Rabbit and Pig team (Hai–Mao–Wei); Tiger, Dragon, Snake, Monkey, Rooster steady. Goat, Ox, Rat, Dog = the four "meeting the Tai Sui".
- Birth years: Rat 1960/72/84/96/2008 · Ox 1961/73/85/97/2009 · Tiger 1962/74/86/98/2010 · Rabbit 1963/75/87/99/2011 · Dragon 1964/76/88/2000/2012 · Snake 1965/77/89/2001/2013 · Horse 1966/78/90/2002/2014 · Goat 1967/79/91/2003/2015 · Monkey 1968/80/92/2004/2016 · Rooster 1969/81/93/2005/2017 · Dog 1958/70/82/94/2006 · Pig 1959/71/83/95/2007.
- Ding (the year's fire) against each day element (the force of 2027, Ten Mirrors names): Yang Wood Speak-up · Yin Wood Joy · Yang Fire Rival · Yin Fire Friend · Yang Earth Support · Yin Earth Insight · Yang Metal Recognition · Yin Metal Pressure · Yang Water Steady money (plus the Ding–Ren pairing: partnerships, love) · Yin Water Opportunity.
- Months of 2027 (solar months, from about the 4th–8th): Feb Ren Yin · Mar Gui Mao · Apr Jia Chen · May Yi Si · Jun Bing Wu · Jul Ding Wei · Aug Wu Shen · Sep Ji You · Oct Geng Xu · Nov Xin Hai · Dec Ren Zi · Jan 2028 Gui Chou (the Ox month clashes the year). Fire peaks Jun–Jul.
- Home in 2027 (the site's home compass, from 4 Feb 2027): annual centre star 9; heavy ground (5) North; tired ground (2) West; three cold winds West; Tai Sui Southwest; its shadow (Sui Po) Northeast. General placement advice only; no renovation advice beyond "don't start drilling/renovating there"; no fear language.
- Last Ding Wei year: 1967. Singapore issued its first own currency notes on 12 Jun 1967; ASEAN was founded on 8 Aug 1967 in Bangkok. Use as "building foundations", never as a prediction.

## Rules
- Classic names on screen (Yin Fire, the Goat), always explained in plain words. No Chinese characters on the visuals or in captions.
- Balanced: every clash or catch comes with its upside. No fear words (disaster, bad luck, danger).
- Economy / money: "tradition links…"; caption carries "Traditional view, not financial advice."; never predict markets, prices or sectors' performance. Economy and "ask" reels wait for Stanley's Approve reel.
- Bright Sky & Season look, one fresh ChatGPT hook scene per reel, music only, no title cards, no episode numbers.

## Spec shape (`tools/y2027/<slug>.json`, rendered by `python3 tools/reels/reel5.py y27 <spec> <date>`)
```
{"tag": "YOUR ANIMAL IN 2027 · OX",            # pill on the hook, ≤ 30 chars, upper case
 "hook": ["Born in an Ox year?", "Here's your 2027."],   # ≤ 34 / ≤ 40 chars
 "note": "Ox years: 1961 · 1973 · 1985 · 1997 · 2009",
 "cover_form": "Yin Earth",                    # form for the designed hook/close
 "cards": [{"kicker": "1 / 4 · THE CLASH", "title": "OX VS GOAT", "who": "opposite each other in the zodiac",
            "animal": "Ox", "el": "Earth",     # or "form": "Yang Wood"
            "head": "2027 pushes the Ox to move.", "body": "Expect change: home, work or travel."}, ...],
 "cta": {"line": "Ox, what's YOUR 2027 mark?", "sub": "The clash lands differently on every chart."},
 "caption": "..."}
```
Cards: 3–4. Title ≤ 14 characters (or `"title_lines": 2`). head ≤ 46, body ≤ 60. Optional `card_len` (default 4.3 s). Scene images: `media/<date>/art5e/hook.png` (and optional `01-…png` for card 1 etc.).

## Calendar
`tools/y2027/queue.json` (built by `build_queue.py`): one entry per Mon/Wed/Fri/Sat slot with series, slug, hook, angle and facts; specials pinned (3 Feb "before 4 Feb", 6 Feb Goat New Year). 8 "flex" slots in late March for repeats of the best performers.
Written and rendered on 26 Nov: what-is-2027 (27 Nov), 2027-starts-4-feb (28 Nov), sun-to-candle (30 Nov). Written, to render in the 28 Nov batch: heavenly-river (2 Dec), four-meet-tai-sui (4 Dec), three-words (5 Dec), animal-ox (7 Dec).
