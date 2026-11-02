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
    def __init__(self, stem, seed):
        self.el = STEMS[stem][1]; self.slug = STEM_SLUG[stem]; rnd = random.Random(seed)
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
            im = scene_bg(hook['img'], t / HOOK); d = ImageDraw.Draw(im)
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
            shadow_text(im, (70, 110), c['kicker'], F(42, 700), c.get('accent', GOLD))
            pop(im, 70, 165, c['title'], fit(d, c['title'], 132, W - 140, 1, floor=90), WHITE, lt, per=0.12)
            if lt > 0.25 and c.get('who'): shadow_text(im, (74, 320), c['who'], F(46, 500), WARM)
            if lt > 0.4 and c.get('pill'): pill(ImageDraw.Draw(im), 70, 395, c['pill'], F(42, 700), c.get('accent', GOLD), INK)
            card_panel(im, 1330, c['head'], c.get('body', ''), lt, 0.5, accent=c.get('accent'))
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
    if hk is None: raise SystemExit(f'no SCENE image in {A} for the hook; expected one of {[f"{k + 1:02d}-" for k in picks]}')
    hl = lines[hk]
    hook = dict(img=cards[hk]['img'], date=dt.strftime('%a %-d %b').upper(), lead=f"{hl['element']} people:",
                line=first_sentence(hl['line'])[0][0].lower() + first_sentence(hl['line'])[0][1:], note='Your element in 3 sec…')
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
    if not top.get('img'): raise SystemExit(f'no SCENE image for #1 in {A} (01-…)')
    title = ' '.join(sp['title'])
    hook = dict(img=top['img'], date=dt.strftime('%a %-d %b').upper(), lead='Which element is', line=title[0].lower() + title[1:], note='Counting down to #1…')
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
    first = next((c for c in cards if c.get('img')), None)
    if not first: raise SystemExit(f'no SCENE image in {A}')
    title = ' '.join(sp['title'])
    hook = dict(img=first['img'], date=dt.strftime('%a %-d %b').upper(), lead=title[0].upper() + title[1:], line=sp['tag_line'], note='Find yours in 3 sec…')
    close = dict(line='Which one are you?', sub='Your element is the day you were born.', head='skyandseason.com', body=sp.get('comment_line', 'Then comment your element below.'),
                 designed=Designed(day(dt)[0], f'{date}-sclose'))
    out = f'{ROOT}/media/{date}'
    render(hook, cards, close, f'{out}/series-reel.mp4', f'{out}/series-cover.jpg', card_len=1.5 * BAR)

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
    elif k == 'picks': picks(sys.argv[2])
    else: raise SystemExit('sky|ranking|series|clip|picks')
