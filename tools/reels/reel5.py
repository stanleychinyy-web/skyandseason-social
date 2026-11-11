"""Reels, format v5 (from 4 Nov 2026): Sky & Season characters, bright, a MIX of picture types (Stanley, 2 Nov:
"do not use such graphic… appears very dark… incorporate Sky and Season or use ChatGPT"; "need not all be ChatGPT
image, it can be a mixture, to make it practical and not hit limit").

Each Day Master / ranking card shows the matching elemental form (Yang stems = Season, Yin stems = Sky):
  * SCENE card: a fresh ChatGPT image made from the approved reference sheet, at media/<date>/art5/<NN>-<slug>.png
    (morning) or media/<date>/art5e/<NN>-<slug>.png (evening). Used for the hook and the most dramatic cards (~3 per reel).
  * DESIGNED card (all other cards): the elemental form cut-out (tools/assets/forms/form_<stem>.png) floating on a bright
    element gradient with drifting element particles; layout, colours and particles vary by date so no two days match.
The hook uses the first SCENE card of the reel. Music only, no voice.

  python3 tools/reels/reel5.py sky <date>                       -> media/<date>/reel.mp4 + cover.jpg
  python3 tools/reels/reel5.py ranking tools/rankings/<slug>.json <date> -> media/<date>/series-reel.mp4 + series-cover.jpg
  python3 tools/reels/reel5.py series tools/series/<slug>.json <date>    -> media/<date>/series-reel.mp4 + series-cover.jpg
  python3 tools/reels/reel5.py clip <date> [reel|series|ranking]          -> media/<date>/story-clip.mp4
  python3 tools/reels/reel5.py picks <date>   # which cards should be SCENE cards (prints the ChatGPT prompts list)

Format v6 (from 18 Nov 2026; Stanley agreed the growth plan on 11 Nov): shorter reels that open on the viewer.
  python3 tools/reels/reel5.py situation tools/series/<slug>.json <date> -> media/<date>/series-reel.mp4 + series-cover.jpg
      five cards, one per element family (the Yang and the Yin line share a card), about 28 s
  python3 tools/reels/reel5.py form tools/forms/<slug>.json <date>       -> media/<date>/series-reel.mp4 + series-cover.jpg
      "Which of the ten are you?": hook, reveal, strength, catch, about 19 s
  python3 tools/reels/reel5.py animals <date>                             -> media/<date>/reel.mp4 + cover.jpg
      Sunday: the 12 animals in four cards grouped by how today treats them, about 24 s
  python3 tools/reels/reel5.py lines <date>                               -> media/<date>/story-lines1.jpg, story-lines2.jpg
      the ten per-element lines of the day as two story pages (the daily reading now lives in the 06:00 stories)
"""
import json, sys, os, subprocess, tempfile, shutil, datetime, math, random, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); NM = HERE + '/node_modules'
ROOT = os.path.abspath(os.path.join(HERE, '..', '..')); ASSETS = os.path.join(ROOT, 'tools', 'assets')
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'tools'))
from daytype import day, name, STEMS

W, H, FPS = 1080, 1920, 30
BAR = 4 * 60 / 112; CARD = 2 * BAR
INK = (34, 26, 58); GOLD = (255, 196, 70); WHITE = (255, 255, 255); MUTED = (95, 88, 120); WARM = (255, 240, 220)
STEM_SLUG = ['jia', 'yi', 'bing', 'ding', 'wu', 'ji', 'geng', 'xin', 'ren', 'gui']
WHO = ['Season · Wood form', 'Sky · Wood form', 'Season · Fire form', 'Sky · Fire form', 'Season · Earth form',
       'Sky · Earth form', 'Season · Metal form', 'Sky · Metal form', 'Season · Water form', 'Sky · Water form']
SHORT = {'Friend': 'friends', 'Rival': 'rivals', 'Joy': 'joy', 'Speak-up': 'speaking up', 'Insight': 'insight', 'Support': 'support',
         'Opportunity': 'opportunity', 'Steady-money': 'steady money', 'Pressure': 'pressure', 'Recognition': 'recognition'}
DRAMA = ['Pressure', 'Speak-up', 'Rival', 'Opportunity', 'Recognition', 'Insight', 'Joy', 'Steady-money', 'Support', 'Friend']
# bright two-stop gradients per element (top, bottom), plus a particle colour
GRAD = {'Wood': [((214, 245, 196), (120, 200, 120)), ((236, 250, 210), (96, 186, 150)), ((200, 238, 214), (150, 210, 90))],
        'Fire': [((255, 214, 170), (255, 120, 90)), ((255, 232, 190), (250, 140, 60)), ((255, 205, 200), (240, 110, 120))],
        'Earth': [((255, 236, 196), (222, 170, 100)), ((250, 226, 200), (205, 150, 110)), ((255, 244, 210), (230, 185, 90))],
        'Metal': [((236, 238, 252), (178, 184, 222)), ((240, 236, 250), (196, 176, 226)), ((232, 244, 250), (170, 196, 222))],
        'Water': [((206, 236, 255), (90, 160, 236)), ((214, 246, 250), (70, 180, 210)), ((222, 230, 255), (110, 140, 236))]}
PART = {'Wood': (90, 170, 80), 'Fire': (255, 150, 60), 'Earth': (190, 140, 80), 'Metal': (255, 255, 255), 'Water': (255, 255, 255)}


def F(s, w=700): return ImageFont.truetype(f'{NM}/@fontsource/fredoka/files/fredoka-latin-{w}-normal.woff', s)
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def eb(t):
    t = max(0.0, min(1.0, t)); c = 1.70158; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


# ---------- type ----------
def wrap(d, txt, f, maxw):
    out, line = [], ''
    for w in txt.split():
        t = (line + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: line = t
        else:
            if line: out.append(line)
            line = w
    return out + [line]

def fit(d, txt, size, maxw, lines, w=700, floor=48):
    while size > floor and len(wrap(d, txt, F(size, w), maxw)) > lines: size -= 4
    return F(size, w)

_WC = {}
def word_img(wd, f, fill):
    k = (wd, f.size, f.path, fill)
    if k not in _WC:
        tw = int(ImageDraw.Draw(Image.new('L', (1, 1))).textlength(wd, font=f)) + 40
        tmp = Image.new('RGBA', (tw, int(f.size * 1.4)), (0, 0, 0, 0))
        sh = Image.new('RGBA', tmp.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((3, 5), wd, font=f, fill=(10, 6, 30, 170))
        tmp.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5))); ImageDraw.Draw(tmp).text((0, 0), wd, font=f, fill=fill)
        _WC[k] = tmp
    return _WC[k]

def pop(im, x, y, txt, f, fill, t, per=0.08, start=0.0, lead=1.05, maxw=W - 140):
    d = ImageDraw.Draw(im); k = 0
    for line in wrap(d, txt, f, maxw):
        cx = x
        for wd in line.split():
            tw = d.textlength(wd + ' ', font=f); lt = t - start - k * per
            if lt > 0:
                s = eb(lt / 0.22); tmp = word_img(wd, f, fill)
                if abs(s - 1) < 0.01: im.alpha_composite(tmp, (int(cx), int(y)))
                else:
                    sw, shh = max(1, int(tmp.width * s)), max(1, int(tmp.height * s)); sc = tmp.resize((sw, shh))
                    im.alpha_composite(sc, (int(cx + (tmp.width - sw) / 2), int(y + (tmp.height - shh) / 2)))
            cx += tw; k += 1
        y += int(f.size * lead)
    return y

def shadow_text(im, xy, txt, f, fill):
    im.alpha_composite(word_img(txt, f, fill), (int(xy[0]), int(xy[1])))

def pill(d, x, y, txt, f, bgc, fg, h=88):
    tw = d.textlength(txt, font=f); d.rounded_rectangle([x, y, x + tw + 80, y + h], h // 2, fill=bgc)
    d.text((x + 40 + tw / 2, y + h / 2), txt, font=f, fill=fg, anchor='mm')

def card_panel(im, y, head, body, t, start, accent=None):
    """White reading card that slides up from the bottom."""
    p = ease((t - start) / 0.35)
    if p <= 0: return
    d = ImageDraw.Draw(im); fh = fit(d, head, 66, W - 220, 3, floor=50); fb = fit(d, body, 50, W - 220, 3, w=500, floor=40) if body else None
    hl = wrap(d, head, fh, W - 220); bl = wrap(d, body, fb, W - 220) if body else []
    hgt = 70 + len(hl) * int(fh.size * 1.18) + (16 + len(bl) * int(fb.size * 1.28) if body else 0) + 34
    y0 = min(y, H - 120 - hgt) + int(260 * (1 - p))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([60, y0 + 12, W - 60, y0 + hgt + 12], 48, fill=(20, 10, 40, 80))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle([60, y0, W - 60, y0 + hgt], 48, fill=(255, 255, 255, 246))
    if accent: d.rounded_rectangle([60, y0, 76, y0 + hgt], 8, fill=accent)
    yy = y0 + 52
    for l in hl: d.text((110, yy), l, font=fh, fill=INK); yy += int(fh.size * 1.18)
    yy += 16
    for l in bl: d.text((110, yy), l, font=fb, fill=MUTED); yy += int(fb.size * 1.28)


# ---------- backgrounds ----------
_ART = {}
def scene(path):
    if path not in _ART:
        im = Image.open(path).convert('RGB'); r = max(W / im.width, H / im.height) * 1.1
        _ART[path] = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    return _ART[path]

_TOP = None
def top_shade():
    global _TOP
    if _TOP is None:
        _TOP = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(_TOP)
        for y in range(0, 680, 4): d.rectangle([0, y, W, y + 4], fill=(22, 16, 44, int(150 * (1 - y / 680) ** 1.4)))
    return _TOP

def scene_bg(path, q):
    src = scene(path); z = 1.0 + 0.07 * q
    cw, ch = int(W / z), int(H / z); x0 = (src.width - cw) // 2; y0 = (src.height - ch) // 2
    im = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR).convert('RGBA')
    return Image.alpha_composite(im, top_shade())

_FORM = {}
def form(slug):
    if slug not in _FORM: _FORM[slug] = Image.open(f'{ASSETS}/forms/form_{slug}.png').convert('RGBA')
    return _FORM[slug]

class Designed:
    """Bright designed card for one elemental form; variation seeded by (date, card) so every day differs."""
    def __init__(self, stem, seed, el=None, fig=None):
        self.el = el or STEMS[stem][1]; self.slug = STEM_SLUG[stem] if stem is not None else None; rnd = random.Random(seed)
        top, bot = rnd.choice(GRAD[self.el])
        g = Image.new('RGB', (1, 256))
        for y in range(256):
            k = y / 255; g.putpixel((0, y), tuple(int(top[i] * (1 - k) + bot[i] * k) for i in range(3)))
        self.base = g.resize((W, H)).convert('RGBA')
        hd = ImageDraw.Draw(self.base)
        cx, cy = rnd.choice([W // 2, W // 2 - 60, W // 2 + 60]), rnd.choice([980, 1010, 950])
        halo = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(halo).ellipse([cx - 420, cy - 420, cx + 420, cy + 420], fill=(255, 255, 255, 110))
        self.base.alpha_composite(halo.filter(ImageFilter.GaussianBlur(60)))
        for _ in range(rnd.randint(3, 6)):   # soft bokeh rings
            r = rnd.randint(60, 180); x, y = rnd.randint(0, W), rnd.randint(500, 1700)
            ring = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(30, 60)))
            self.base.alpha_composite(ring.filter(ImageFilter.GaussianBlur(18)))
        self.base = Image.alpha_composite(self.base, top_shade())
        if fig is not None: f = fig; cy = 990
        else:
            f = form(self.slug); scale = rnd.uniform(1.25, 1.45); f = f.resize((int(f.width * scale), int(f.height * scale)), Image.LANCZOS)
            if rnd.random() < 0.5: f = f.transpose(Image.FLIP_LEFT_RIGHT)
        self.fig = f; self.cx, self.cy = cx, cy
        self.parts = [(rnd.uniform(0, W), rnd.uniform(500, H), rnd.uniform(6, 16), rnd.uniform(20, 70), rnd.uniform(0, 6.28)) for _ in range(26)]
        self.pc = PART[self.el]
    def frame(self, t):
        im = self.base.copy(); d = ImageDraw.Draw(im)
        for x, y, s, sp, ph in self.parts:   # drifting element particles
            yy = (y - sp * t * 3) % (H - 450) + 450; xx = x + 18 * math.sin(t * 1.3 + ph)
            a = int(150 + 80 * math.sin(t * 2 + ph))
            if self.el == 'Wood': d.ellipse([xx - s, yy - s / 2, xx + s, yy + s / 2], fill=self.pc + (a,))
            elif self.el in ('Metal', 'Water'): d.polygon([(xx, yy - s), (xx + s / 3, yy), (xx, yy + s), (xx - s / 3, yy)], fill=self.pc + (a,)); d.polygon([(xx - s, yy), (xx, yy - s / 3), (xx + s, yy), (xx, yy + s / 3)], fill=self.pc + (a,))
            else: d.ellipse([xx - s / 2, yy - s / 2, xx + s / 2, yy + s / 2], fill=self.pc + (a,))
        bob = 22 * math.sin(t * 2.2); sc = 1.0 + 0.03 * math.sin(t * 1.1)
        f = self.fig if abs(sc - 1) < 0.002 else self.fig.resize((int(self.fig.width * sc), int(self.fig.height * sc)))
        im.alpha_composite(f, (int(self.cx - f.width / 2), int(self.cy - f.height / 2 + bob)))
        return im


def rows_panel(im, y, rows, t, start, accent=None):
    """White reading card with labelled rows [(label, text)], sliding up from the bottom (v6 pair cards)."""
    p = ease((t - start) / 0.35)
    if p <= 0: return
    d = ImageDraw.Draw(im); fl = F(34, 700); size = 50
    while True:
        ft = F(size, 600); wrapped = [wrap(d, txt, ft, W - 220) for _, txt in rows]
        if all(len(w) <= 2 for w in wrapped) or size <= 40: break
        size -= 2
    hgt = 44 + sum(48 + len(w) * int(size * 1.22) + 22 for w in wrapped) + 14
    y0 = min(y, H - 120 - hgt) + int(260 * (1 - p))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([60, y0 + 12, W - 60, y0 + hgt + 12], 48, fill=(20, 10, 40, 80))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle([60, y0, W - 60, y0 + hgt], 48, fill=(255, 255, 255, 246))
    if accent: d.rounded_rectangle([60, y0, 76, y0 + hgt], 8, fill=accent)
    yy = y0 + 44
    for (lab, _), w in zip(rows, wrapped):
        d.text((110, yy), lab, font=fl, fill=accent or MUTED); yy += 48
        for l in w: d.text((110, yy), l, font=ft, fill=INK); yy += int(size * 1.22)
        yy += 22

DEEP = {'Wood': (45, 120, 75), 'Fire': (196, 71, 47), 'Earth': (150, 105, 30), 'Metal': (95, 98, 125), 'Water': (46, 90, 135)}
ELS = ['Wood', 'Fire', 'Earth', 'Metal', 'Water']

class Duo(Designed):
    """Designed card for one element family: Season's Yang form (left) and Sky's Yin form (right), bobbing out of step."""
    def __init__(self, el, seed):
        k = ELS.index(el); Designed.__init__(self, 2 * k, seed)
        rnd = random.Random(str(seed) + 'duo'); sc = rnd.uniform(1.0, 1.08)
        def rs(slug):
            f = form(slug); return f.resize((int(f.width * sc), int(f.height * sc)), Image.LANCZOS)
        self.a, self.b = rs(STEM_SLUG[2 * k]), rs(STEM_SLUG[2 * k + 1])
        self.cy = rnd.choice([930, 960, 900])
    def frame(self, t):
        fig, self.fig = self.fig, Image.new('RGBA', (2, 2), (0, 0, 0, 0)); im = Designed.frame(self, t); self.fig = fig
        im.alpha_composite(self.a, (int(285 - self.a.width / 2), int(self.cy - self.a.height / 2 + 20 * math.sin(t * 2.2))))
        im.alpha_composite(self.b, (int(795 - self.b.width / 2), int(self.cy + 30 - self.b.height / 2 + 20 * math.sin(t * 2.2 + 2.1))))
        return im


# ---------- engine ----------
def encode(frames, total, out):
    music = f'{frames}/tune.m4a'
    subprocess.run([sys.executable, f'{HERE}/music.py', music, '2', 'a', str(int(math.ceil(total / BAR)))], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{frames}/%05d.jpg', '-i', music, '-map', '0:v', '-map', '1:a', '-shortest',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', out], check=True)

def render(hook, cards, close, out_video, out_cover, card_len=CARD):
    """hook: {img, date, lead, line, note}; cards: [{img|designed, kicker, title, who, pill, head, body, accent?}]; close: {line, sub, head, body, img|designed}."""
    HOOK = 1.5 * BAR; CLOSE = 1.5 * BAR; n = len(cards); total = HOOK + n * card_len + CLOSE
    frames = tempfile.mkdtemp()
    for fr in range(int(total * FPS) + 1):
        t = fr / FPS
        if t < HOOK:
            im = scene_bg(hook['img'], t / HOOK) if hook.get('img') else hook['designed'].frame(t); d = ImageDraw.Draw(im)
            pill(d, 70, 120, hook['date'], F(34, 700), WHITE, INK, h=70)
            y = pop(im, 70, 230, hook['lead'], fit(d, hook['lead'], 118, W - 140, 2), GOLD, t, per=0.1)
            pop(im, 70, y + 4, hook['line'], fit(d, hook['line'], 96, W - 140, 3), WHITE, t, per=0.08, start=0.3)
            if t > 1.6:
                nw = d.textlength(hook['note'], font=F(44, 600))
                d.rounded_rectangle([60, 1600, 140 + nw, 1686], 43, fill=(255, 255, 255, 235)); d.text((100, 1620), hook['note'], font=F(44, 600), fill=INK)
        elif t < HOOK + n * card_len:
            i = int((t - HOOK) // card_len); lt = t - HOOK - i * card_len; c = cards[i]
            im = scene_bg(c['img'], lt / card_len) if c.get('img') else c['designed'].frame(lt + i)
            d = ImageDraw.Draw(im)
            if c.get('overlay'): c['overlay'](im, lt)
            shadow_text(im, (70, 110), c['kicker'], F(42, 700), c.get('kicker_fill', c.get('accent', GOLD)))
            tl = c.get('title_lines', 1)
            ty = pop(im, 70, 165, c['title'], fit(d, c['title'], 132, W - 140, tl, floor=90 if tl == 1 else 84), WHITE, lt, per=0.12)
            wy = 320 if tl == 1 else max(320, ty + 26)
            if lt > 0.25 and c.get('who'): shadow_text(im, (74, wy), c['who'], fit(d, c['who'], 46, W - 150, 1, w=500, floor=30), WARM)
            if lt > 0.4 and c.get('pill'): pill(ImageDraw.Draw(im), 70, wy + 75, c['pill'], F(42, 700), c.get('accent', GOLD), INK)
            if c.get('rows'): rows_panel(im, 1300, c['rows'], lt, 0.5, accent=c.get('accent_deep'))
            else: card_panel(im, 1330, c['head'], c.get('body', ''), lt, 0.5, accent=c.get('accent'))
        else:
            lt = t - HOOK - n * card_len; c = close
            im = scene_bg(c['img'], lt / CLOSE) if c.get('img') else c['designed'].frame(lt); d = ImageDraw.Draw(im)
            y = pop(im, 70, 200, c['line'], fit(d, c['line'], 96, W - 140, 3), WHITE, lt, per=0.07)
            if lt > 0.9: pop(im, 70, y + 20, c['sub'], F(62, 500), WARM, lt, per=0.07, start=0.9)
            card_panel(im, 1420, c['head'], c['body'], lt, 1.4)
        ImageDraw.Draw(im).rectangle([0, H - 14, int(W * t / total), H], fill=GOLD)
        if abs(t - 1.4) < 0.5 / FPS: im.convert('RGB').save(out_cover, quality=92)
        im.convert('RGB').save(f'{frames}/{fr:05d}.jpg', quality=90)
    encode(frames, total, out_video); shutil.rmtree(frames); print('v5', out_video, round(total, 1), 's')

def art(dirp, key):
    hits = sorted(glob.glob(f'{dirp}/{key}*.png')) + sorted(glob.glob(f'{dirp}/{key}*.jpg'))
    return hits[0] if hits else None

def first_sentence(line):
    parts = line.split('. ', 1); return parts[0] + ('.' if len(parts) > 1 else ''), (parts[1] if len(parts) > 1 else '')

PROPER = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'I', "I'm", "I'll", 'MRT', 'CNY'}
def hook_case(txt):
    """Lower-case the first letter after 'X people:' unless the first word is a proper noun (weekday, MRT...)."""
    w = txt.split(' ', 1)[0].rstrip('.,;:!?')
    return txt if w in PROPER else txt[0].lower() + txt[1:]

def slug_of(nm): return nm.lower().replace(' ', '-')


def sky_picks(date):
    """The 3 most dramatic cards (by day-type) get ChatGPT SCENE images; the first of them is also the hook."""
    lines = json.load(open(f'{ROOT}/media/{date}/lines.json', encoding='utf-8'))
    order = sorted(range(len(lines)), key=lambda k: DRAMA.index(lines[k]['type']))
    return lines, order[:3]

def sky(date):
    dt = datetime.date.fromisoformat(date); s, b = day(dt); idx = {name(i): i for i in range(10)}
    lines, picks = sky_picks(date); A = f'{ROOT}/media/{date}/art5'
    cards = []
    for k, l in enumerate(lines):
        si = idx[l['element']]; key = f'{k + 1:02d}-'; img = art(A, key)
        head, body = first_sentence(l['line'])
        c = dict(kicker=f'{k + 1} / {len(lines)}', title=l['element'].upper(), who=WHO[si], pill=f'Today: {SHORT[l["type"]]}', head=head, body=body)
        if img: c['img'] = img
        else: c['designed'] = Designed(si, f'{date}-{k}')
        cards.append(c)
    hk = next((k for k in picks if cards[k].get('img')), None)
    if hk is None: hk = picks[0]; print(f'WARNING: no SCENE image in {A}; designed hook (fallback)')
    hl = lines[hk]
    hook = dict(img=cards[hk].get('img'), designed=cards[hk].get('designed'), date=dt.strftime('%a %-d %b').upper(), lead=f"{hl['element']} people:",
                line=hook_case(first_sentence(hl['line'])[0]), note='Your element in 3 sec…')
    close = dict(line='Your element is the day you were born.', sub='Find it free in 60 seconds.', head='skyandseason.com', body='Then comment your element below.',
                 designed=Designed(s, f'{date}-close'))
    out = f'{ROOT}/media/{date}'
    render(hook, cards, close, f'{out}/reel.mp4', f'{out}/cover.jpg')

def ranking(spec_path, date):
    dt = datetime.date.fromisoformat(date); s, b = day(dt); idx = {name(i): i for i in range(10)}
    sp = json.load(open(spec_path, encoding='utf-8')); ranks = sp['rank'][:5]; A = f'{ROOT}/media/{date}/art5e'
    cards = []
    for k, r in enumerate(reversed(ranks)):    # #5 first, #1 last
        rank = len(ranks) - k; si = idx[r['element']]; img = art(A, f'{rank:02d}-')
        c = dict(kicker=f'#{rank}' + ('  ·  THE WINNER' if rank == 1 else ''), title=r['element'].upper(), who=WHO[si], pill='',
                 head=r['line'], body=('The upside: ' + r['plus']) if r.get('plus') else '', accent=(255, 170, 60) if rank == 1 else GOLD)
        if img: c['img'] = img
        else: c['designed'] = Designed(si, f'{date}-r{rank}')
        cards.append(c)
    top = cards[-1]
    if not top.get('img'): print(f'WARNING: no SCENE image for #1 in {A}; designed hook (fallback)')
    title = ' '.join(sp['title'])
    hook = dict(img=top.get('img'), designed=top.get('designed'), date=dt.strftime('%a %-d %b').upper(), lead='Which element is', line=title[0].lower() + title[1:], note='Counting down to #1…')
    close = dict(line='Agree?', sub=sp.get('comment_line', 'Tag your #1 below.'), head='skyandseason.com', body='Your element is the day you were born. Free.',
                 designed=Designed(idx[ranks[0]['element']], f'{date}-rclose'))
    out = f'{ROOT}/media/{date}'
    render(hook, cards, close, f'{out}/series-reel.mp4', f'{out}/series-cover.jpg')

def series(spec_path, date):
    dt = datetime.date.fromisoformat(date); sp = json.load(open(spec_path, encoding='utf-8')); A = f'{ROOT}/media/{date}/art5e'
    cards = []
    for i in range(10):
        img = art(A, f'{i + 1:02d}-')
        c = dict(kicker=f'{i + 1} / 10', title=name(i).upper(), who=WHO[i], pill='', head=sp['items'][name(i)], body='')
        if img: c['img'] = img
        else: c['designed'] = Designed(i, f'{date}-s{i}')
        cards.append(c)
    first = {'img': art(A, 'hook')} if art(A, 'hook') else next((c for c in cards if c.get('img')), None)
    if not first: print(f'WARNING: no SCENE image in {A}; designed hook (fallback)'); first = {'designed': Designed(day(dt)[0], f'{date}-shook')}
    title = ' '.join(sp['title'])
    hook = dict(img=first.get('img'), designed=first.get('designed'), date=dt.strftime('%a %-d %b').upper(), lead=title[0].upper() + title[1:], line=sp['tag_line'], note='Find yours in 3 sec…')
    close = dict(line='Which one are you?', sub='Your element is the day you were born.', head='skyandseason.com', body=sp.get('comment_line', 'Then comment your element below.'),
                 designed=Designed(day(dt)[0], f'{date}-sclose'))
    out = f'{ROOT}/media/{date}'
    render(hook, cards, close, f'{out}/series-reel.mp4', f'{out}/series-cover.jpg', card_len=1.5 * BAR)

def tiles(path, cols=3, rows=2, size=640):
    """Cut a ChatGPT grid picture (equal tiles) into rounded, white-framed portraits for the animal cards."""
    im = Image.open(path).convert('RGB'); tw, th = im.width / cols, im.height / rows; out = []
    for r in range(rows):
        for c in range(cols):
            t = im.crop((int(c * tw + tw * .03), int(r * th + th * .03), int((c + 1) * tw - tw * .03), int((r + 1) * th - th * .03)))
            s = min(t.size); t = t.crop(((t.width - s) // 2, (t.height - s) // 2, (t.width + s) // 2, (t.height + s) // 2)).resize((size, size), Image.LANCZOS)
            fr = Image.new('RGBA', (size + 36, size + 36), (0, 0, 0, 0)); m = Image.new('L', (size, size), 0)
            ImageDraw.Draw(fr).rounded_rectangle([0, 0, size + 35, size + 35], 70, fill=(255, 255, 255, 255))
            ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], 56, fill=255); fr.paste(t, (18, 18), m)
            sh = Image.new('RGBA', (size + 120, size + 120), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([42, 54, size + 78, size + 90], 70, fill=(20, 10, 40, 90))
            sh = sh.filter(ImageFilter.GaussianBlur(16)); sh.alpha_composite(fr, (42, 42)); out.append(sh)
    return out

def season(date):
    """Sunday: the 12 animals meet today's animal. Hook = a ChatGPT scene (art5/hook.png); animal cards = tiles cut from
    two ChatGPT grid pictures (art5/animals-a.png: Rat Ox Tiger / Rabbit Dragon Snake, art5/animals-b.png: Horse Goat Monkey /
    Rooster Dog Pig) on bright designed backgrounds. 3 ChatGPT images per Sunday."""
    from reel import relation
    from daytype import BRANCH_ANIMAL, BRANCH_EL
    dt = datetime.date.fromisoformat(date); s, b = day(dt); A = f'{ROOT}/media/{date}/art5'
    tips = json.load(open(f'{ROOT}/tools/days/{date}.json', encoding='utf-8'))['animal_tips']
    if not (art(A, 'animals-a') and art(A, 'animals-b')): raise SystemExit(f'Sunday needs {A}/animals-a.png and animals-b.png (ChatGPT grids)')
    ts = tiles(art(A, 'animals-a')) + tiles(art(A, 'animals-b')); clash = (b + 6) % 12; an = BRANCH_ANIMAL[clash]
    cards = []
    for a in range(12):
        lab = relation(a, b)[0].split(' · ')[0].replace('-', ' ').lower().capitalize()
        yrs = ' · '.join(str(y) for y in range(1948 + a, 2021, 12)[-4:])
        cards.append(dict(kicker=f'{a + 1} / 12', title=BRANCH_ANIMAL[a].upper(), who=f'Born {yrs}', pill=lab, head=tips[BRANCH_ANIMAL[a]],
                          body='Born in Jan or early Feb? Use the animal before yours.', designed=Designed(None, f'{date}-a{a}', el=BRANCH_EL[a], fig=ts[a])))
    hook = dict(img=art(A, 'hook'), designed=Designed(s, f'{date}-hook'), date=f"{dt.strftime('%a %-d %b').upper()} · {BRANCH_ANIMAL[b].upper()} DAY",
                lead=f"Born in {'an' if an[0] in 'AEIOU' else 'a'} {an} year?", line=tips[an], note='All 12 animals, one by one…')
    close = dict(line='Your animal is your Season.', sub='Your element is your Sky. Both free.', head='skyandseason.com', body='Then comment your animal below.',
                 designed=Designed(s, f'{date}-close'))
    out = f'{ROOT}/media/{date}'
    render(hook, cards, close, f'{out}/reel.mp4', f'{out}/cover.jpg', card_len=1.5 * BAR)

# ---------- format v6 (from 18 Nov 2026) ----------
def pairs_of(sp):
    """{element: (yang line, yin line)} from a v6 spec ("pairs") or an older ten-line spec ("items")."""
    if sp.get('pairs'): return {el: (sp['pairs'][el]['yang'], sp['pairs'][el]['yin']) for el in ELS}
    return {el: (sp['items'][f'Yang {el}'], sp['items'][f'Yin {el}']) for el in ELS}

def situation(spec_path, date):
    """Situation reel, five cards: one per element family, Season's Yang line and Sky's Yin line together."""
    dt = datetime.date.fromisoformat(date); sp = json.load(open(spec_path, encoding='utf-8')); A = f'{ROOT}/media/{date}/art5e'
    pairs = pairs_of(sp); cards = []
    for i, el in enumerate(ELS):
        img = art(A, f'{i + 1:02d}-')
        c = dict(kicker=f'{i + 1} / 5', title=el.upper(), who='Season is Yang · Sky is Yin', pill='',
                 rows=[(f'YANG {el.upper()}', pairs[el][0]), (f'YIN {el.upper()}', pairs[el][1])], accent_deep=DEEP[el])
        if img: c['img'] = img
        else: c['designed'] = Duo(el, f'{date}-p{i}')
        cards.append(c)
    title = ' '.join(sp['title']); hk = sp.get('hook') or [title[0].upper() + title[1:], sp['tag_line']]
    first = {'img': art(A, 'hook')} if art(A, 'hook') else None
    if not first: print(f'WARNING: no SCENE image in {A}/hook.png; designed hook (fallback)'); first = {'designed': Duo(sp.get('cover_element', 'Fire'), f'{date}-phook')}
    hook = dict(img=first.get('img'), designed=first.get('designed'), date=dt.strftime('%a %-d %b').upper(), lead=hk[0], line=hk[1], note='Find yours in 3 sec…')
    close = dict(line='Which one are you?', sub='Your element is the day you were born.', head='skyandseason.com', body=sp.get('comment_line', 'Then comment your element below.'),
                 designed=Duo(sp.get('cover_element', 'Fire'), f'{date}-pclose'))
    out = f'{ROOT}/media/{date}'; os.makedirs(out, exist_ok=True)
    render(hook, cards, close, f'{out}/series-reel.mp4', f'{out}/series-cover.jpg')

def form_reel(spec_path, date):
    """'Which of the ten are you?': hook (a behaviour people recognise), reveal (the essence name), the strength, the catch.
    Inner Constellation names on screen; the classical name (Yang Wood, Jia) belongs in the caption."""
    dt = datetime.date.fromisoformat(date); sp = json.load(open(spec_path, encoding='utf-8')); A = f'{ROOT}/media/{date}/art5e'
    si = {name(i): i for i in range(10)}[sp['stem']]; el = STEMS[si][1]; ess = sp['essence'].upper()
    side = f"{el}, {'bold' if si % 2 == 0 else 'gentle'}"
    spec = [('YOU MAY BE', sp['reveal'], '', '01-'), ('THE STRENGTH', sp['strength'][0], sp['strength'][1], '02-'), ('THE CATCH', sp['catch'][0], sp['catch'][1], '03-')]
    cards = []
    for k, (kick, head, body, key) in enumerate(spec):
        c = dict(kicker=kick, title=ess, title_lines=2, who=WHO[si], pill=side if k == 0 else '', head=head, body=body)
        img = art(A, key)
        if img: c['img'] = img
        else: c['designed'] = Designed(si, f'{date}-f{k}')
        cards.append(c)
    first = {'img': art(A, 'hook')} if art(A, 'hook') else None
    if not first: print(f'WARNING: no SCENE image in {A}/hook.png; designed hook (fallback)'); first = {'designed': Designed(si, f'{date}-fhook')}
    hook = dict(img=first.get('img'), designed=first.get('designed'), date='WHICH OF THE TEN ARE YOU?', lead=sp['hook'][0], line=sp['hook'][1], note='Which of the ten…')
    close = dict(line='There are ten.', sub='Find yours free in 60 seconds.', head='skyandseason.com', body=sp.get('comment_line', 'Comment the one that sounds like you.'),
                 designed=Designed(si, f'{date}-fclose'))
    out = f'{ROOT}/media/{date}'; os.makedirs(out, exist_ok=True)
    render(hook, cards, close, f'{out}/series-reel.mp4', f'{out}/series-cover.jpg')

GROUPS = [('GO EASY', 'CLASH DAY', 'clash', (226, 84, 60)), ('SMALL FRICTION', 'SMALL-FRICTION DAY', 'friction', (255, 170, 60)),
          ('STEADY DAY', 'STEADY DAY', 'steady', GOLD), ('BEST DAY', None, 'best', (120, 220, 140))]

def animal_groups(b):
    """The 12 animals sorted by how today's animal b treats them (reel.relation): clash, friction, steady, best."""
    from reel import relation
    g = {'clash': [], 'friction': [], 'steady': [], 'best': []}
    for a in range(12):
        lab = relation(a, b)[0]
        g['clash' if lab.startswith('CLASH') else 'friction' if lab.startswith('SMALL') else 'steady' if lab.startswith('STEADY') else 'best'].append(a)
    g['best'].sort(key=lambda a: (a != b, a))   # today's own animal first
    return g

def animals(date):
    """Sunday, v6: four cards instead of twelve. Needs the two ChatGPT grids (art5/animals-a.png, animals-b.png) and,
    in tools/days/<date>.json, group_tips {clash, friction, steady, best} (falls back to animal_tips)."""
    from daytype import BRANCH_ANIMAL, BRANCH_EL
    dt = datetime.date.fromisoformat(date); s, b = day(dt); A = f'{ROOT}/media/{date}/art5'
    spec = json.load(open(f'{ROOT}/tools/days/{date}.json', encoding='utf-8')); tips = spec.get('animal_tips', {}); gt = spec.get('group_tips', {})
    if not (art(A, 'animals-a') and art(A, 'animals-b')): raise SystemExit(f'Sunday needs {A}/animals-a.png and animals-b.png (ChatGPT grids)')
    ts = tiles(art(A, 'animals-a')) + tiles(art(A, 'animals-b')); g = animal_groups(b); cards = []
    def overlay_for(members):
        n = len(members); cols = 1 if n == 1 else 2 if n <= 4 else 3; rows = math.ceil(n / cols)
        size = 620 if n == 1 else 470 if n == 2 else 380 if cols == 2 else 330 if rows <= 2 else 300
        small = [ts[a].resize((size, size), Image.LANCZOS) for a in members]
        gap = int(size * 0.02); gw = cols * size + (cols - 1) * gap; gh = rows * size + (rows - 1) * gap
        x0 = (W - gw) // 2; y0 = 500 + (760 - gh) // 2
        def draw(im, lt):
            for k, t in enumerate(small):
                p = eb((lt - 0.12 * k) / 0.3)
                if p <= 0: continue
                r, c = divmod(k, cols); n_row = min(cols, n - r * cols); off = (cols - n_row) * (size + gap) // 2
                tt = t if abs(p - 1) < 0.01 else t.resize((max(1, int(size * p)), max(1, int(size * p))))
                im.alpha_composite(tt, (x0 + off + c * (size + gap) + (size - tt.width) // 2, y0 + r * (size + gap) + (size - tt.height) // 2 + int(10 * math.sin(lt * 2 + k))))
        return draw
    order = [x for x in GROUPS if g[x[2]]]
    for k, (title, _, key, accent) in enumerate(order):
        members = g[key]; names = [BRANCH_ANIMAL[a] for a in members]
        tip = gt.get(key) or tips.get(names[0], '')
        cards.append(dict(kicker=f'{k + 1} / {len(order)}', kicker_fill=WHITE, title=title, who=' · '.join(names), pill='', accent=accent, head=tip,
                          body='Born in Jan or early Feb? Use the animal before yours.' if k == 0 else '',
                          designed=Designed(None, f'{date}-g{k}', el=BRANCH_EL[members[0]], fig=Image.new('RGBA', (2, 2), (0, 0, 0, 0))), overlay=overlay_for(members)))
    clash = (b + 6) % 12; an = BRANCH_ANIMAL[clash]
    hook = dict(img=art(A, 'hook'), designed=Designed(s, f'{date}-hook'), date=f"{dt.strftime('%a %-d %b').upper()} · {BRANCH_ANIMAL[b].upper()} DAY",
                lead=f"Born in {'an' if an[0] in 'AEIOU' else 'a'} {an} year?", line=gt.get('clash') or tips[an], note='All 12 animals in 20 sec…')
    close = dict(line='Your animal is your Season.', sub='Your element is your Sky. Both free.', head='skyandseason.com', body='Then comment your animal below.',
                 designed=Designed(s, f'{date}-close'))
    out = f'{ROOT}/media/{date}'
    render(hook, cards, close, f'{out}/reel.mp4', f'{out}/cover.jpg')

def lines_story(date):
    """The day's ten per-element lines as two story pages (five each), with the Sky & Season forms.
    Needs media/<date>/lines.json (render.py daily). -> media/<date>/story-lines1.jpg, story-lines2.jpg"""
    dt = datetime.date.fromisoformat(date); s, b = day(dt); idx = {name(i): i for i in range(10)}
    lines = json.load(open(f'{ROOT}/media/{date}/lines.json', encoding='utf-8')); out = f'{ROOT}/media/{date}'
    top, bot = GRAD[STEMS[s][1]][0]
    for page in range(2):
        g = Image.new('RGB', (1, 256))
        for y in range(256):
            k = y / 255; g.putpixel((0, y), tuple(int(top[i] * (1 - k) + bot[i] * k) for i in range(3)))
        im = g.resize((W, H)).convert('RGBA'); d = ImageDraw.Draw(im)
        d.text((W // 2, 230), dt.strftime('TODAY · %a %-d %b').upper(), font=F(38, 600), fill=INK, anchor='mm')
        d.text((W // 2, 318), 'Your element today', font=F(74, 700), fill=INK, anchor='mm')
        d.text((W // 2, 392), f'{page + 1} of 2 · find the element of the day you were born', font=F(32, 500), fill=MUTED, anchor='mm')
        y = 452
        for l in lines[page * 5: page * 5 + 5]:
            si = idx[l['element']]; el = STEMS[si][1]
            d.rounded_rectangle([50, y, W - 50, y + 226], 44, fill=(255, 255, 255, 244))
            f = form(STEM_SLUG[si]); r = min(176 / f.width, 176 / f.height); f = f.resize((int(f.width * r), int(f.height * r)), Image.LANCZOS)
            im.alpha_composite(f, (70 + (176 - f.width) // 2, y + 25 + (176 - f.height) // 2))
            d.text((266, y + 24), l['element'].upper(), font=F(34, 700), fill=DEEP[el])
            tw = d.textlength(l['element'].upper() + '  ', font=F(34, 700))
            d.text((266 + tw, y + 27), f"· {SHORT[l['type']]}", font=F(30, 500), fill=MUTED)
            size = 38
            while size > 30 and len(wrap(d, l['line'], F(size, 500), W - 50 - 266 - 36)) > 3: size -= 2
            for j, t in enumerate(wrap(d, l['line'], F(size, 500), W - 50 - 266 - 36)[:3]): d.text((266, y + 74 + j * int(size * 1.24)), t, font=F(size, 500), fill=INK)
            y += 242
        if page == 1:
            d.text((W // 2, y + 26), 'Not sure which is yours? skyandseason.com · free', font=F(36, 600), fill=INK, anchor='mm')
        else:
            d.text((W // 2, y + 26), 'Tap for the other five', font=F(36, 600), fill=INK, anchor='mm')
        im.convert('RGB').save(f'{out}/story-lines{page + 1}.jpg', quality=90)
    print('lines stories', out)


def clip(date, source='reel'):
    """9pm video story: the hook + first card(s), then an end card sending people to the full reel."""
    out = f'{ROOT}/media/{date}'; dt = datetime.date.fromisoformat(date); s, b = day(dt)
    src = f'{out}/series-reel.mp4' if source in ('series', 'ranking') else f'{out}/reel.mp4'
    cut = 1.5 * BAR + (CARD if source == 'ranking' else 1.5 * BAR if source == 'series' else 2 * CARD)
    head, body = {'ranking': ('Who is #1?', "The full countdown is in tonight's reel on our page."),
                  'series': ('Which one are you?', "All 10 elements are in tonight's reel on our page."),
                  'reel': ('Did you find yours?', "All 10 Day Masters are in today's reel on our page.")}[source]
    im = Designed(s, f'{date}-clip').frame(0.3); d = ImageDraw.Draw(im)
    shadow_text(im, (70, 120), 'TONIGHT', F(40, 700), GOLD)
    pop(im, 70, 200, head, F(116, 700), WHITE, 9)
    card_panel(im, 1380, body, '@theskyandseason · skyandseason.com', 9, 0)
    end = f'{out}/_clip_end.jpg'; im.convert('RGB').save(end, quality=92)
    tail = 3.5; tot = cut + tail
    fc = (f'[0:v]trim=0:{cut:.3f},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p[a];[1:v]fps={FPS},format=yuv420p,fade=t=in:st=0:d=0.3[e];'
          f'[a][e]concat=n=2:v=1:a=0[v];[0:a]atrim=0:{tot:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={tot - 1.2:.3f}:d=1.2[au]')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-loop', '1', '-t', str(tail), '-i', end, '-filter_complex', fc, '-map', '[v]', '-map', '[au]',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart',
                    f'{out}/story-clip.mp4'], check=True)
    os.remove(end); print('clip', f'{out}/story-clip.mp4', round(tot, 1), 's', source)

def picks(date):
    lines, p = sky_picks(date); idx = {name(i): i for i in range(10)}
    for k in p:
        l = lines[k]; print(f"{k + 1:02d}-{slug_of(l['element'])}  {WHO[idx[l['element']]]}  [{l['type']}]  {l['line']}")


if __name__ == '__main__':
    k = sys.argv[1]
    if k == 'sky': sky(sys.argv[2])
    elif k == 'ranking': ranking(sys.argv[2], sys.argv[3])
    elif k == 'series': series(sys.argv[2], sys.argv[3])
    elif k == 'clip': clip(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'reel')
    elif k == 'season': season(sys.argv[2])
    elif k == 'picks': picks(sys.argv[2])
    elif k == 'situation': situation(sys.argv[2], sys.argv[3])
    elif k == 'form': form_reel(sys.argv[2], sys.argv[3])
    elif k == 'animals': animals(sys.argv[2])
    elif k == 'lines': lines_story(sys.argv[2])
    else: raise SystemExit('sky|season|ranking|series|clip|picks|situation|form|animals|lines')
