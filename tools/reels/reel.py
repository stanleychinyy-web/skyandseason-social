"""Sky & Season daily reels and the daily story (1080x1920, light pastel style, 112 bpm).
Everything is about the day it posts.
  cd tools/reels && npm install          (once: emoji, font, instrument samples)
  python3 tools/reels/reel.py sky    <date>   -> media/<date>/reel.mp4 + cover.jpg   (needs media/<date>/lines.json from render.py daily)
  python3 tools/reels/reel.py season <date>   -> media/<date>/reel.mp4 + cover.jpg   (needs animal_tips in tools/days/<date>.json)
  python3 tools/reels/reel.py story  <date>   -> media/<date>/story1-6.jpg           (needs day_line in tools/days/<date>.json)
  python3 tools/reels/reel.py series tools/series/<slug>.json <date> -> media/<date>/series-reel.mp4 + series-cover.jpg (Mon/Wed/Fri 19:00)
Lens: the daily posts use the Classic lens on both halves (stem gods + zodiac animals); never Inner season names here.
Run from the repository root. Each card stays on screen for 2 bars (about 4.3 s) so it can be read."""
import json, sys, os, io, subprocess, tempfile, shutil, datetime, textwrap
import cairosvg
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); NM = HERE + '/node_modules'
ROOT = os.path.abspath(os.path.join(HERE, '..', '..')); ASSETS = os.path.join(ROOT, 'tools', 'assets')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from daytype import day, daytype, name, STEMS, BRANCH_ANIMAL
from week import ANIMAL_ICON, ANIMAL_EL, SEASON, GOD, SLUG, FORCE
from daytype import BRANCH_EL
def BRANCH_EL_OF(b): return BRANCH_EL[b]
W, H, FPS = 1080, 1920, 30
BEAT = 60 / 112; BAR = 4 * BEAT; CARD = 2 * BAR
INK = (35, 28, 60); MUTED = (95, 88, 120); CREAM = (255, 250, 240); RED = (226, 84, 60); GREEN = (50, 140, 85)
BG = {'Water': (196, 224, 250), 'Earth': (250, 226, 180), 'Wood': (200, 236, 200), 'Fire': (255, 205, 190), 'Metal': (228, 228, 240)}
DEEP = {'Water': (46, 90, 135), 'Earth': (150, 105, 30), 'Wood': (45, 120, 75), 'Fire': (196, 71, 47), 'Metal': (95, 98, 115)}
GLOSS = {'The Sovereign': 'confidence', 'The Shadow': 'competition', 'The Muse': 'ideas & fun', 'The Rebel': 'speaking up',
         'The Steward': 'steady money', 'The Visionary': 'lucky breaks', 'The Guardian': 'recognition', 'The Crucible': 'pressure',
         'The Sage': 'help & learning', 'The Mystic': 'intuition'}
HOW = {'Friend': 'Today is your own element', 'Rival': 'Today is your own element', 'Joy': 'You feed today\'s element',
       'Speak-up': 'You feed today\'s element', 'Insight': 'Today\'s element feeds you', 'Support': 'Today\'s element feeds you',
       'Opportunity': 'You shape today\'s element', 'Steady-money': 'You shape today\'s element',
       'Pressure': 'Today\'s element shapes you', 'Recognition': 'Today\'s element shapes you'}
ANIMAL_NOTE = {'Water': 'a Water animal: deep, quiet and flowing', 'Earth': 'an Earth animal: steady, patient and grounded', 'Wood': 'a Wood animal: growing, bold and restless',
               'Fire': 'a Fire animal: warm, bright and quick', 'Metal': 'a Metal animal: sharp, precise and cool'}
HARMONY = {0: 1, 1: 0, 2: 11, 11: 2, 3: 10, 10: 3, 4: 9, 9: 4, 5: 8, 8: 5, 6: 7, 7: 6}
HARM = {0: 7, 7: 0, 1: 6, 6: 1, 2: 5, 5: 2, 3: 4, 4: 3, 8: 11, 11: 8, 9: 10, 10: 9}
def relation(a, b):
    """How birth-year animal a meets today's animal b: (label, plain why, colour)."""
    A, B = BRANCH_ANIMAL[a], BRANCH_ANIMAL[b]
    if a == b: return 'HOME-TURF DAY', f"Today is {'an' if B[0] in 'AEIOU' else 'a'} {B} day, your own animal", GREEN
    if HARMONY[a] == b: return 'BEST-FRIEND DAY', f'{A} and {B} are a perfect pair', GREEN
    if (b - a) % 12 in (4, 8): return 'TEAM DAY', f'{A} and {B} are on the same team', GREEN
    if (a + 6) % 12 == b: return 'CLASH DAY · GO EASY', f'{A} and {B} sit opposite each other', RED
    if HARM[a] == b: return 'SMALL-FRICTION DAY', f'{A} and {B} rub each other a little', (200, 120, 40)
    return 'STEADY DAY', f'Nothing pulls on the {A} today', MUTED

def F(s, w=600): return ImageFont.truetype(f'{NM}/@fontsource/fredoka/files/fredoka-latin-{w}-normal.woff', s)
_ICONS = None
def emoji(key, size):
    global _ICONS
    _ICONS = _ICONS or json.load(open(f'{NM}/@iconify-json/noto/icons.json'))
    ic = _ICONS['icons'][key]; w = ic.get('width', _ICONS.get('width', 128)); h = ic.get('height', _ICONS.get('height', 128))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{size}" height="{size}">{ic["body"]}</svg>'
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
def medallion(slug, size):
    im = Image.open(f'{ASSETS}/stems/{slug}.jpg').convert('RGBA').resize((size, size), Image.LANCZOS)
    m = Image.new('L', (size * 4, size * 4), 0); ImageDraw.Draw(m).ellipse([0, 0, size * 4, size * 4], fill=255)
    im.putalpha(m.resize((size, size), Image.LANCZOS))
    ring = Image.new('RGBA', (size + 24, size + 24), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse([0, 0, size + 23, size + 23], fill=(255, 255, 255))
    ring.alpha_composite(im, (12, 12)); return ring
def ease_back(t):
    t = max(0, min(1, t)); c = 1.7; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def ease(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3
def ctext(d, y, txt, f, fill): d.text((W // 2, y), txt, font=f, fill=fill, anchor='mm')
def scaled(im, src, cx, cy, s):
    if s <= 0.01: return
    t = src.resize((max(1, int(src.width * s)), max(1, int(src.height * s))), Image.LANCZOS)
    im.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))
def pill(d, cx, y, txt, f, bg, fg, padx=44, h=96):
    w = d.textlength(txt, font=f) + 2 * padx
    d.rounded_rectangle([cx - w / 2, y, cx + w / 2, y + h], h // 2, fill=bg); d.text((cx, y + h / 2), txt, font=f, fill=fg, anchor='mm')
def wrap(d, txt, f, maxw):
    out, cur = [], ''
    for w in txt.split():
        x = (cur + ' ' + w).strip()
        if d.textlength(x, font=f) <= maxw: cur = x
        else: out.append(cur); cur = w
    return out + [cur]
def para(d, x, y, txt, size, maxw, fill, w=500, lead=1.3, center=False, max_lines=4):
    while True:
        f = F(size, w); lines = wrap(d, txt, f, maxw)
        if len(lines) <= max_lines or size <= 34: break
        size -= 2
    for i, l in enumerate(lines):
        if center: d.text((W // 2, y + i * size * lead), l, font=f, fill=fill, anchor='ma')
        else: d.text((x, y + i * size * lead), l, font=f, fill=fill)
    return y + len(lines) * size * lead
def dots(d, n, i):
    for k in range(n):
        x = W // 2 - (n - 1) * 30 + k * 60
        d.ellipse([x - 9, 231, x + 9, 249], fill=INK if k == i else (255, 255, 255))
def dlabel(dt): return dt.strftime('%A %-d %B')

def facts(date):
    dt = datetime.date.fromisoformat(date); s, b = day(dt)
    spec_p = os.path.join(ROOT, 'tools', 'days', f'{date}.json')
    spec = json.load(open(spec_p, encoding='utf-8')) if os.path.exists(spec_p) else {}
    return dt, s, b, spec

# ---------- stories (6 frames, all about the day) ----------
STEM_ICON = ['deciduous-tree', 'herb', 'sun-with-face', 'candle', 'mountain', 'sheaf-of-rice', 'axe', 'gem-stone', 'water-wave', 'cloud-with-rain']
EL_ICON = {'Wood': 'deciduous-tree', 'Fire': 'fire', 'Earth': 'mountain', 'Metal': 'gem-stone', 'Water': 'droplet'}
STEM_INFO = [  # nature (from the site's stem gods), good for, watch out
    ('Growth, structure, standing tall.', 'starting long projects, planning ahead', 'being stubborn'),
    ('Flexible and social; always finds a way round.', 'networking, gentle persuasion, teamwork', 'people-pleasing'),
    ('Warm, generous and seen by everyone.', 'launching, presenting, showing up', 'overpromising and burning out'),
    ('Focused warmth: a small light that goes deep.', 'deep talks, careful work, learning', 'overthinking at night'),
    ('Steady, reliable, protective.', 'commitments, admin, home matters', 'refusing to budge'),
    ('Nurturing, practical, patient.', 'caring for people, cooking, budgeting', 'worrying too much'),
    ('Decisive, direct, brave.', 'hard decisions, decluttering, exercise', 'words that cut too sharp'),
    ('Refined, precise, elegant.', 'polishing details, self-care, design', 'perfectionism'),
    ('Big, free-flowing, adventurous.', 'big ideas, travel, learning', 'scattered focus'),
    ('Quiet, intuitive, adaptable.', 'reflection, research, rest', 'moodiness'),
]
# The site's 12 seasons (branch-stage-map.js): landscape line and months
LANDSCAPE = ['A seed lies buried below the frost line, waiting.', 'Snowmelt seeps down toward the buried seed.',
             'The first shoot breaks through thawing soil.', 'A tender seedling stands unshielded in spring rain.',
             'A staked sapling is pruned and trained upright.', 'A young tree stretches toward open sun, branches spreading.',
             'The canopy is full, fruit ripening in high summer.', 'Fruit hangs heavy on the branch as daylight starts to shorten.',
             'The first leaves turn as early frost tests the canopy.', 'The leaves fall, the tree stands bare against the sky.',
             'Fallen leaves settle into the earth, becoming next year’s soil.', 'Bare ground under frost, nothing visible above the soil.']
HOURS = ['11pm–1am', '1–3am', '3–5am', '5–7am', '7–9am', '9–11am', '11am–1pm', '1–3pm', '3–5pm', '5–7pm', '7–9pm', '9–11pm']
COLOUR = {'Wood': 'green', 'Fire': 'red or pink', 'Earth': 'yellow or beige', 'Metal': 'white or silver', 'Water': 'navy or black'}
DIRECTION = {'Wood': 'East', 'Fire': 'South', 'Earth': 'the centre of the room', 'Metal': 'West', 'Water': 'North'}
PROD = {'Wood': 'Fire', 'Fire': 'Earth', 'Earth': 'Metal', 'Metal': 'Water', 'Water': 'Wood'}
CTRL = {'Wood': 'Earth', 'Earth': 'Water', 'Water': 'Fire', 'Fire': 'Metal', 'Metal': 'Wood'}
def element_link(top, bottom):
    """How the day's Sky element (top) and Season element (bottom) relate: (quiz question, options, answer, explanation)."""
    if PROD[bottom] == top: return (f'Which element feeds {top}?', bottom, f'{bottom} feeds {top}. Today {top} sits on {bottom}: well fed and strong.')
    if PROD[top] == bottom: return (f'What does {top} feed?', bottom, f'{top} feeds {bottom}. Today {top} pours its energy into the {bottom} below it: generous, but tiring.')
    if CTRL[top] == bottom: return (f'Which element does {top} keep in check?', bottom, f'{top} keeps {bottom} in check. Today {top} is the boss of the ground it stands on.')
    if CTRL[bottom] == top: return (f'Which element keeps {top} in check?', bottom, f'{bottom} keeps {top} in check. Today {top} is under pressure from below: steady wins.')
    return (f'Which element is the same as {top}?', bottom, f'Today {top} sits on {top}: double strength, for better and worse.')
def options(answer):
    order = ['Wood', 'Fire', 'Earth', 'Metal', 'Water']; i = order.index(answer)
    return sorted({answer, order[(i + 2) % 5], order[(i + 4) % 5]}, key=order.index)

def frame(el, date, k, n):
    im = Image.new('RGBA', (W, H), BG[el]); d = ImageDraw.Draw(im)
    d.text((W // 2, 230), date.strftime('TODAY · %a %-d %b').upper(), font=F(38, 600), fill=INK, anchor='mm')
    for j in range(n if n > 1 else 0):
        x = W // 2 - (n - 1) * 22 + j * 44
        d.rounded_rectangle([x - 16, 270, x + 16, 278], 4, fill=INK if j == k else (255, 255, 255))
    return im, d
def card(d, y0, y1): d.rounded_rectangle([80, y0, W - 80, y1], 48, fill=(255, 255, 255))

def stories(date):
    dt, s, b, spec = facts(date)
    sky_el, sea_el = STEMS[s][1], BRANCH_EL_OF(b)
    sky_icon, sea_icon = emoji(STEM_ICON[s], 300), emoji(ANIMAL_ICON[b], 300)
    out = os.path.join(ROOT, 'media', date); os.makedirs(out, exist_ok=True); N = 6; files = []
    def save(im, k):
        p = f'{out}/story{k + 1}.jpg'; im.convert('RGB').save(p, quality=90); files.append(p)
    # 1. cover
    im, d = frame(sky_el, dt, 0, 3)
    ctext(d, 360, "Today's Sky & Season", F(76, 700), INK)
    for cx, kind in [(290, 'SKY'), (790, 'SEASON')]:
        d.rounded_rectangle([cx - 230, 430, cx + 230, 1010], 48, fill=(255, 255, 255))
        art = emoji(STEM_ICON[s], 260) if kind == 'SKY' else emoji(ANIMAL_ICON[b], 260)
        im.alpha_composite(art, (cx - 130, 465))
        d.text((cx, 770), kind, font=F(32, 700), fill=RED if kind == 'SKY' else GREEN, anchor='mm')
        d.text((cx, 835), name(s) if kind == 'SKY' else BRANCH_ANIMAL[b], font=F(56, 700), fill=INK, anchor='mm')
        d.text((cx, 900), GOD[s] if kind == 'SKY' else f'{BRANCH_EL[b]} animal', font=F(36, 500), fill=MUTED, anchor='mm')
        d.text((cx, 955), "the day's element" if kind == 'SKY' else "the day's animal", font=F(30, 400), fill=MUTED, anchor='mm')
    para(d, 0, 1080, spec.get('day_line') or f'{GOD[s]} meets the {BRANCH_ANIMAL[b]}.', 60, W - 180, INK, w=600, center=True, max_lines=3)
    ctext(d, 1560, 'Little luck & a quiz at 12:30pm', F(44, 600), RED)
    save(im, 0)
    # 2. the Sky
    nature, good, watch = STEM_INFO[s]
    im, d = frame(sky_el, dt, 1, 3)
    ctext(d, 350, "TODAY'S SKY", F(40, 700), RED)
    scaled(im, sky_icon, W // 2, 560, 1)
    ctext(d, 780, name(s), F(92, 700), INK); ctext(d, 860, GOD[s], F(48, 500), MUTED)
    card(d, 930, 1560)
    y = para(d, 130, 970, nature, 50, W - 260, INK, w=600, max_lines=2)
    d.text((130, y + 30), 'GOOD FOR', font=F(34, 700), fill=GREEN); y = para(d, 130, y + 80, good.capitalize() + '.', 48, W - 260, INK, max_lines=2)
    d.text((130, y + 30), 'WATCH OUT FOR', font=F(34, 700), fill=RED); para(d, 130, y + 80, watch.capitalize() + '.', 48, W - 260, INK, max_lines=2)
    save(im, 1)
    # 3. the Season
    hm, tr, cl = BRANCH_ANIMAL[HARMONY[b]], [BRANCH_ANIMAL[(b + 4) % 12], BRANCH_ANIMAL[(b + 8) % 12]], BRANCH_ANIMAL[(b + 6) % 12]
    im, d = frame(sea_el, dt, 2, 3)
    ctext(d, 350, "TODAY'S SEASON", F(40, 700), GREEN)
    scaled(im, sea_icon, W // 2, 560, 1)
    ctext(d, 780, f'{BRANCH_ANIMAL[b]} day', F(92, 700), INK); ctext(d, 860, f'{BRANCH_EL[b]} animal', F(48, 500), MUTED)
    card(d, 930, 1600)
    y = para(d, 130, 970, f'The {BRANCH_ANIMAL[b]} is {ANIMAL_NOTE[BRANCH_EL[b]]}.', 46, W - 260, INK, w=500, max_lines=2)
    rows = [('BEST FRIEND TODAY', hm, GREEN), ('SAME TEAM', ' & '.join(tr), GREEN), ('GO EASY', cl, RED)]
    for lab, val, col in rows:
        d.text((130, y + 34), lab, font=F(34, 700), fill=col); d.text((W - 130, y + 26), val, font=F(50, 700), fill=INK, anchor='ra'); y += 100
    para(d, 130, y + 30, f'Born in a {cl} year? Keep today light.', 42, W - 260, MUTED, max_lines=2)
    save(im, 2)
    # 4. lucky colour / hours / direction
    im, d = frame(sky_el, dt, 0, 2)
    ctext(d, 360, "Today's little luck", F(76, 700), INK)
    lucky = [((b + 4) % 12), HARMONY[b], ((b + 8) % 12)]
    lucky = sorted(set(lucky), key=lambda x: (x - 3) % 12)  # morning first
    rows = [('artist-palette', 'COLOUR', f'Wear {COLOUR[sky_el]} to go with today’s {sky_el}.'),
            ('alarm-clock', 'BEST HOURS', ', '.join(f'{HOURS[h]} ({BRANCH_ANIMAL[h]})' for h in lucky)),
            ('compass', 'DIRECTION', f'Sit facing {DIRECTION[sky_el]} for focus.')]
    y = 470
    for icon, lab, txt in rows:
        card(d, y, y + 300); im.alpha_composite(emoji(icon, 130), (120, y + 85))
        d.text((290, y + 50), lab, font=F(36, 700), fill=RED)
        para(d, 290, y + 105, txt, 44, W - 420, INK, w=500, max_lines=3); y += 340
    para(d, 0, y + 20, 'For everyone today. Your own lucky hours are in your free chart.', 38, W - 220, MUTED, center=True, max_lines=2)
    save(im, 3)
    # 5. quiz
    q, ans, why = element_link(sky_el, sea_el)
    im, d = frame(sea_el, dt, 1, 2)
    scaled(im, emoji('red-question-mark', 220), W // 2, 470, 1)
    ctext(d, 660, 'Quick quiz', F(84, 700), INK)
    para(d, 0, 760, q, 60, W - 200, INK, w=600, center=True, max_lines=2)
    y = 960
    for o in options(ans):
        card(d, y, y + 150); im.alpha_composite(emoji(EL_ICON[o], 100), (150, y + 25)); d.text((290, y + 75), o, font=F(60, 700), fill=INK, anchor='lm'); y += 180
    ctext(d, y + 60, 'Guess now. The answer drops at 9pm.', F(42, 600), RED)
    save(im, 4)
    # 6. answer + call to action
    im, d = frame(sea_el, dt, 0, 1)
    ctext(d, 290, "THIS AFTERNOON'S QUIZ", F(36, 700), MUTED)
    para(d, 0, 330, q, 40, W - 240, MUTED, w=500, center=True, max_lines=2)
    ctext(d, 470, f'Answer: {ans}', F(84, 700), GREEN)
    scaled(im, emoji(EL_ICON[ans], 170), W // 2 - 130, 630, 1); scaled(im, emoji(EL_ICON[sky_el], 170), W // 2 + 130, 630, 1)
    para(d, 0, 760, why, 48, W - 200, INK, w=500, center=True, max_lines=4)
    card(d, 1060, 1560)
    para(d, 0, 1110, 'What does today mean for YOUR element?', 54, W - 260, INK, w=700, center=True, max_lines=2)
    para(d, 0, 1260, "Your element is the day you were born. Find it free, with today's reading for you.", 40, W - 280, MUTED, center=True, max_lines=3)
    pill(d, W // 2, 1420, 'skyandseason.com · free', F(46, 700), INK, CREAM, h=104)
    save(im, 5)
    print('stories', len(files), out)

# ---------- reels ----------
def render(kind, date):
    dt, s, b, spec = facts(date)
    if kind == 'sky':
        L = json.load(open(os.path.join(ROOT, 'media', date, 'lines.json'), encoding='utf-8'))
        items = [dict(dm=name(i), element=STEMS[i][1], god=GOD[i], art=SLUG[i], type=daytype(i, s), line=L[i]['line']) for i in range(10)]
        intro = 2   # hook + how-it-works
    else:
        tips = spec.get('animal_tips') or {}
        missing = [a for a in BRANCH_ANIMAL if not tips.get(a)]
        if missing: raise SystemExit(f'animal_tips missing in tools/days/{date}.json for {missing}')
        items = [dict(name=BRANCH_ANIMAL[a], icon=ANIMAL_ICON[a], element=ANIMAL_EL[a], season=SEASON[a],
                      years=' · '.join(map(str, range(1960 + a, 2012, 12))), rel=relation(a, b), tip=tips[BRANCH_ANIMAL[a]]) for a in range(12)]
        intro = 1
    n = len(items); bars = intro * 2 + n * 2 + 3; total = bars * BAR; start = intro * CARD
    if kind == 'sky':
        big = [emoji(STEM_ICON[i], 380) for i in range(10)]; today_art = emoji(STEM_ICON[s], 420); small_today = emoji(STEM_ICON[s], 240)
    else:
        big = [emoji(a['icon'], 420) for a in items]; today_art = emoji(ANIMAL_ICON[b], 440)
    mark = Image.open(f'{ASSETS}/brand/logo-mark-256.png').convert('RGBA').resize((80, 80))
    out = os.path.join(ROOT, 'media', date); os.makedirs(out, exist_ok=True); tmp = tempfile.mkdtemp()
    hook_bg = BG[STEMS[s][1]] if kind == 'sky' else BG[ANIMAL_EL[b]]
    cover_t = 2.0
    for fr in range(int(total * FPS) + 1):
        t = fr / FPS
        if t < CARD:   # hook: today
            im = Image.new('RGBA', (W, H), hook_bg); d = ImageDraw.Draw(im); p = ease(t / 0.4); dy = 30 * (1 - p)
            ctext(d, 250 + dy, 'TODAY · ' + dt.strftime('%a %-d %b').upper(), F(40, 600), INK)
            if kind == 'sky':
                ctext(d, 340 + dy, "Today's Sky is", F(68, 600), INK)
                ctext(d, 440 + dy, name(s).upper(), F(116, 700), DEEP[STEMS[s][1]])
                ctext(d, 530 + dy, GOD[s], F(52, 500), MUTED)
                scaled(im, today_art, W // 2, 860, ease_back((t - 0.3) / 0.4))
                if t > 1.2: para(d, 0, 1130, spec.get('day_line', ''), 50, W - 200, INK, w=600, center=True, max_lines=3)
                if t > 2.2: ctext(d, 1480, "What it means for YOUR Day Master", F(48, 600), RED); ctext(d, 1545, "Pause on yours", F(40, 500), MUTED)
            else:
                ctext(d, 340 + dy, "Today is", F(68, 600), INK)
                ctext(d, 450 + dy, f"{'AN' if BRANCH_ANIMAL[b][0] in 'AEIOU' else 'A'} {BRANCH_ANIMAL[b].upper()} DAY", F(120, 700), DEEP[ANIMAL_EL[b]])
                scaled(im, today_art, W // 2, 800, ease_back((t - 0.3) / 0.4))
                if t > 1.2:
                    pill(d, W // 2, 1050, f"{BRANCH_EL[b]} animal", F(40, 600), (255, 255, 255), INK, padx=40, h=84)
                    para(d, 0, 1180, f"Every day has an animal. Today's {BRANCH_ANIMAL[b]} meets the animal of the year you were born.", 44, W - 200, INK, center=True, max_lines=3)
                if t > 2.4: ctext(d, 1480, "What it means for YOUR animal", F(50, 600), RED); ctext(d, 1545, "Pause on yours", F(40, 500), MUTED)
        elif kind == 'sky' and t < 2 * CARD:   # how it works
            lt = t - CARD; im = Image.new('RGBA', (W, H), CREAM); d = ImageDraw.Draw(im)
            ctext(d, 300, "How to read this", F(72, 700), INK)
            lx, rx = W // 2 - 270, W // 2 + 270
            im.alpha_composite(small_today, (lx - small_today.width // 2, 420))
            d.text((lx, 700), "Today's Sky", font=F(38, 600), fill=INK, anchor='mm')
            d.text((W // 2, 542), "meets", font=F(44, 500), fill=MUTED, anchor='mm')
            d.ellipse([rx - 122, 420, rx + 122, 664], fill=(255, 255, 255), outline=INK, width=4)
            d.text((rx, 542), "you", font=F(64, 700), fill=INK, anchor='mm')
            d.text((rx, 700), "Your Day Master", font=F(38, 600), fill=INK, anchor='mm')
            if lt > 0.5: para(d, 0, 800, "Your Day Master is the element of the day you were born.", 50, W - 200, INK, center=True, max_lines=2)
            if lt > 1.3: para(d, 0, 990, "When today's element meets yours, it creates one of 10 forces, like The Muse (ideas & fun) or The Crucible (pressure).", 46, W - 200, INK, center=True, max_lines=3)
            if lt > 2.3: para(d, 0, 1260, "Here is the force each Day Master gets today.", 46, W - 200, RED, w=600, center=True, max_lines=2)
        elif t < start + CARD * n:
            i = int((t - start) // CARD); lt = t - start - i * CARD; a = items[i]
            im = Image.new('RGBA', (W, H), BG[a['element']]); d = ImageDraw.Draw(im); dots(d, n, i)
            p = ease((lt - 0.08) / 0.3); dy = 40 * (1 - p)
            scaled(im, big[i], W // 2, 500, ease_back(lt / 0.3))
            if kind == 'sky':
                ctext(d, 760 + dy, a['dm'].upper(), F(100, 700), INK)
                ctext(d, 840 + dy, a['god'], F(46, 500), MUTED)
                force = FORCE[a['type']]
                pill(d, W // 2, 900 + dy, f"Today: {force} · {GLOSS[force]}", F(42, 700), DEEP[a['element']], CREAM, padx=40, h=90)
                ctext(d, 1030 + dy, HOW[a['type']], F(36, 500), INK)
                nl = len(wrap(d, a['line'], F(54, 500), W - 280))
                d.rounded_rectangle([90, 1090 + dy, W - 90, 1090 + dy + 80 + nl * 70], 44, fill=(255, 255, 255))
                para(d, 140, 1130 + dy, a['line'], 54, W - 280, INK, w=500, max_lines=5)
            else:
                ctext(d, 740 + dy, a['name'].upper(), F(108, 700), INK)
                ctext(d, 820 + dy, a['years'], F(38, 500), MUTED)
                pill(d, W // 2, 865 + dy, f"{a['element']} animal", F(34, 600), (255, 255, 255), INK, padx=34, h=68)
                lab, why, col = a['rel']
                nl = len(wrap(d, a['tip'], F(54, 600), W - 280))
                d.rounded_rectangle([90, 975 + dy, W - 90, 1250 + dy + nl * 70], 44, fill=(255, 255, 255))
                d.text((140, 1010 + dy), lab, font=F(52, 700), fill=col)
                para(d, 140, 1090 + dy, why + '.', 40, W - 280, MUTED, w=500, max_lines=2)
                para(d, 140, 1210 + dy, a['tip'], 54, W - 280, INK, w=600, max_lines=4)
        else:
            lt = t - start - CARD * n
            im = Image.new('RGBA', (W, H), hook_bg); d = ImageDraw.Draw(im)
            def beat(k, fn):
                if lt > k * 0.6: fn(20 * (1 - ease((lt - k * 0.6) / 0.35)))
            if kind == 'sky':
                beat(0, lambda o: (ctext(d, 400 + o, "Your Day Master is your", F(60, 500), INK), ctext(d, 495 + o, "SKY", F(130, 700), RED)))
                beat(1, lambda o: para(d, 0, 640 + o, "It's the element of the day you were born, not your zodiac animal.", 48, W - 200, INK, center=True, max_lines=2))
            else:
                beat(0, lambda o: (ctext(d, 400 + o, "Your animal is your", F(60, 500), INK), ctext(d, 495 + o, "SEASON", F(120, 700), INK)))
                beat(1, lambda o: para(d, 0, 640 + o, "The element of the day you were born is your SKY. Together: Sky & Season.", 48, W - 200, INK, center=True, max_lines=2))
            if lt > 1.6:
                pill(d, W // 2, 900, "Find yours free · skyandseason.com", F(44, 600), INK, CREAM, h=110)
                ctext(d, 1100, "Comment yours below" if kind == 'season' else "Comment your Day Master below", F(46, 500), INK)
                im.alpha_composite(mark, (W // 2 - 40, 1180))
        if abs(t - cover_t) < 0.5 / FPS: im.convert('RGB').save(f'{out}/cover.jpg', quality=90)
        im.convert('RGB').save(f'{tmp}/{fr:05d}.jpg', quality=90)
    music = f'{tmp}/tune.m4a'
    subprocess.run([sys.executable, f'{HERE}/music.py', music] + (['0', 'a'] if kind == 'season' else ['-3', 'b']) + [str(bars)], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', music,
                    '-map', '0:v', '-map', '1:a', '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', '-r', str(FPS),
                    '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', f'{out}/reel.mp4'], check=True)
    shutil.rmtree(tmp); print(kind, f'{out}/reel.mp4', round(total, 1), 's')

# ---------- series reel (Mon/Wed/Fri 19:00): "The 10 elements on the MRT" ----------
def series_reel(spec_path, date):
    sp = json.load(open(spec_path, encoding='utf-8'))
    col = DEEP[sp.get('cover_element', 'Fire')]; bgc = BG[sp.get('cover_element', 'Fire')]
    items = [(name(i), STEMS[i][1], sp['items'][name(i)]) for i in range(10)]
    SCARD = 1.5 * BAR; n = 10; bars = 2 + 1.5 * n + 2.5; total = bars * BAR; start = CARD
    big = [emoji(STEM_ICON[i], 360) for i in range(10)]
    mark = Image.open(f'{ASSETS}/brand/logo-mark-256.png').convert('RGBA').resize((80, 80))
    out = os.path.join(ROOT, 'media', date); os.makedirs(out, exist_ok=True); tmp = tempfile.mkdtemp()
    title = ' '.join(sp['title'])
    for fr in range(int(total * FPS) + 1):
        t = fr / FPS
        if t < CARD:   # cover
            im = Image.new('RGBA', (W, H), col); d = ImageDraw.Draw(im); p = ease(t / 0.4); dy = 30 * (1 - p)
            y = 520
            for l in sp['title']: y = para(d, 0, y + dy, l, 112, W - 140, CREAM, w=700, center=True, max_lines=1, lead=1.05)
            if t > 1.0: para(d, 0, y + 60, sp['tag_line'], 50, W - 200, (255, 240, 230), w=600, center=True, max_lines=2)
            if t > 2.0: ctext(d, 1560, 'Pause on yours', F(44, 600), CREAM)
            im.alpha_composite(mark, (W // 2 - 40, 1700))
        elif t < start + SCARD * n:
            i = int((t - start) // SCARD); lt = t - start - i * SCARD; nm, el, line = items[i]
            im = Image.new('RGBA', (W, H), BG[el]); d = ImageDraw.Draw(im); dots(d, n, i)
            p = ease((lt - 0.08) / 0.3); dy = 40 * (1 - p)
            scaled(im, big[i], W // 2, 520, ease_back(lt / 0.3))
            ctext(d, 780 + dy, nm.upper(), F(104, 700), INK)
            d.rounded_rectangle([90, 900 + dy, W - 90, 900 + dy + 100 + 76 * len(wrap(d, line, F(60, 600), W - 280))], 44, fill=(255, 255, 255))
            para(d, 140, 950 + dy, line, 60, W - 280, INK, w=600, max_lines=4, lead=1.25)
        else:
            lt = t - start - SCARD * n
            im = Image.new('RGBA', (W, H), bgc); d = ImageDraw.Draw(im)
            if lt > 0.1: ctext(d, 480, "Which one", F(130, 700), INK); ctext(d, 610, "are you?", F(130, 700), INK)
            if lt > 0.8: para(d, 0, 760, "Your element comes from the day you were born. Find it free in 60 seconds.", 46, W - 200, INK, center=True, max_lines=3)
            if lt > 1.5:
                pill(d, W // 2, 1000, "skyandseason.com", F(46, 700), INK, CREAM, h=110)
                ctext(d, 1180, sp.get('comment_line', "Then comment your element below."), F(42, 600), col)
                im.alpha_composite(mark, (W // 2 - 40, 1280))
        if abs(t - 1.6) < 0.5 / FPS: im.convert('RGB').save(f'{out}/series-cover.jpg', quality=90)
        im.convert('RGB').save(f'{tmp}/{fr:05d}.jpg', quality=90)
    music = f'{tmp}/tune.m4a'
    subprocess.run([sys.executable, f'{HERE}/music.py', music, '2', 'a', str(int(bars + 0.999))], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', music,
                    '-map', '0:v', '-map', '1:a', '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', '-r', str(FPS),
                    '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', f'{out}/series-reel.mp4'], check=True)
    shutil.rmtree(tmp); print('series', f'{out}/series-reel.mp4', round(total, 1), 's', title)

# ---------- 9pm video story: a clip of the day's reel + an end card ----------
def story_clip(date, source='reel'):
    """media/<date>/story-clip.mp4: the first cards of today's reel (or tonight's series reel),
    then a 3.5 s end card sending people to the full reel."""
    dt, s, b, spec = facts(date); out = os.path.join(ROOT, 'media', date)
    series = source == 'series'
    src = f'{out}/series-reel.mp4' if series else f'{out}/reel.mp4'
    sunday = dt.weekday() == 6
    cut = (CARD + 2 * 1.5 * BAR) if series else 3 * CARD
    el = STEMS[s][1] if not sunday else BRANCH_EL_OF(b)
    im = Image.new('RGBA', (W, H), BG[el]); d = ImageDraw.Draw(im)
    ctext(d, 300, 'TONIGHT', F(38, 700), RED)
    scaled(im, emoji('sparkles', 240), W // 2, 520, 1)
    if series:
        head, body = 'Which one are you?', "All 10 elements are in tonight's reel on our page."
    elif sunday:
        head, body = 'Found your animal?', "All 12 zodiac animals are in today's reel on our page."
    else:
        head, body = 'Did you find yours?', "All 10 Day Masters are in today's reel on our page."
    para(d, 0, 720, head, 92, W - 160, INK, w=700, center=True, max_lines=2)
    para(d, 0, 900, body, 54, W - 220, INK, w=500, center=True, max_lines=3)
    pill(d, W // 2, 1180, '@theskyandseason', F(52, 700), INK, CREAM, h=112)
    para(d, 0, 1340, 'Your element is the day you were born. Find yours free at skyandseason.com', 40, W - 260, MUTED, center=True, max_lines=3)
    end = f'{out}/_clip_end.jpg'; im.convert('RGB').save(end, quality=92)
    tail = 3.5; tot = cut + tail
    fc = (f'[0:v]trim=0:{cut:.3f},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p[a];'
          f'[1:v]fps={FPS},format=yuv420p,fade=t=in:st=0:d=0.3[e];[a][e]concat=n=2:v=1:a=0[v];'
          f'[0:a]atrim=0:{tot:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={tot - 1.2:.3f}:d=1.2[au]')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-loop', '1', '-t', str(tail), '-i', end,
                    '-filter_complex', fc, '-map', '[v]', '-map', '[au]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21',
                    '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', f'{out}/story-clip.mp4'], check=True)
    os.remove(end); print('clip', f'{out}/story-clip.mp4', round(tot, 1), 's', source)

if __name__ == '__main__':
    k, date = sys.argv[1], sys.argv[2]
    if k == 'series': series_reel(sys.argv[2], sys.argv[3])
    elif k == 'clip': story_clip(date, sys.argv[3] if len(sys.argv) > 3 else 'reel')
    else: stories(date) if k == 'story' else render(k, date)
