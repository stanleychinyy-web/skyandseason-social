"""Weekly Sky & Season reels (1080x1920, 112 bpm, about 17 s).
  cd tools/reels && npm ci   (once: emoji, font, instrument samples)
  python3 tools/reels/reel.py sky    tools/reels/weeks/<monday>.json <post-date>   -> media/<post-date>/reel.mp4 + cover.jpg
  python3 tools/reels/reel.py season tools/reels/weeks/<monday>.json <post-date>
Run from the repository root. Every tip in the week file must be filled first."""
import json, sys, os, io, subprocess, tempfile, shutil
import cairosvg
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); NM = HERE + '/node_modules'
ASSETS = os.path.join(HERE, '..', 'assets')
W, H, FPS = 1080, 1920, 30
BEAT = 60 / 112; HOOK = 4 * BEAT; CARD = 2 * BEAT
INK = (35, 28, 60); MUTED = (95, 88, 120); CREAM = (255, 250, 240); RED = (226, 84, 60); GREEN = (50, 140, 85)
BG = {'Water': (196, 224, 250), 'Earth': (250, 226, 180), 'Wood': (200, 236, 200), 'Fire': (255, 205, 190), 'Metal': (228, 228, 240)}
HOOK_BG = {'sky': (210, 228, 255), 'season': (255, 236, 190)}
GLOSS = {'The Sovereign': 'confidence', 'The Shadow': 'competition', 'The Muse': 'ideas & fun', 'The Rebel': 'speaking up',
         'The Steward': 'steady money', 'The Visionary': 'lucky breaks', 'The Guardian': 'recognition', 'The Crucible': 'pressure',
         'The Sage': 'help & learning', 'The Mystic': 'intuition'}

def F(s, w=600): return ImageFont.truetype(f'{NM}/@fontsource/fredoka/files/fredoka-latin-{w}-normal.woff', s)
ICONS = None
def emoji(key, size):
    global ICONS
    ICONS = ICONS or json.load(open(f'{NM}/@iconify-json/noto/icons.json'))
    ic = ICONS['icons'][key]; w = ic.get('width', ICONS.get('width', 128)); h = ic.get('height', ICONS.get('height', 128))
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
def fit(d, txt, size, maxw, w=500):
    while d.textlength(txt, font=F(size, w)) > maxw and size > 30: size -= 2
    return F(size, w)
def dots(d, n, i):
    for k in range(n):
        x = W // 2 - (n - 1) * 30 + k * 60
        d.ellipse([x - 9, 231, x + 9, 249], fill=INK if k == i else (255, 255, 255))
def boxes(d, y, dy, lucky_label, lucky_day, lucky_tip, easy_label, easy_day, easy_tip):
    d.rounded_rectangle([90, y + dy, W - 90, y + 240 + dy], 44, fill=(255, 255, 255))
    d.text((140, y + 26 + dy), lucky_label, font=fit(d, lucky_label, 32, W - 280, 600), fill=GREEN)
    d.text((140, y + 70 + dy), lucky_day, font=F(66, 700), fill=INK)
    d.text((140, y + 165 + dy), lucky_tip, font=fit(d, lucky_tip, 44, W - 280), fill=INK)
    y2 = y + 260
    d.rounded_rectangle([90, y2 + dy, W - 90, y2 + 220 + dy], 44, fill=(255, 255, 255, 175))
    if easy_day:
        d.text((140, y2 + 24 + dy), easy_label, font=fit(d, easy_label, 30, W - 280, 600), fill=RED)
        d.text((140, y2 + 66 + dy), easy_day.upper(), font=F(52, 700), fill=INK)
        d.text((140, y2 + 150 + dy), easy_tip, font=fit(d, easy_tip, 42, W - 280), fill=INK)
    else:
        d.text((140, y2 + 24 + dy), "GO EASY", font=F(30, 600), fill=RED)
        d.text((140, y2 + 90 + dy), easy_tip or "No clash day. Smooth week!", font=F(46, 600), fill=INK)

def check(items, kind):
    empty = [x.get('dm') or x.get('name') for x in items if not x['lucky_tip'] or (x['easy'] and not x['easy_tip'])]
    if empty: raise SystemExit(f'{kind}: tips missing for {empty}')

def render(kind, spec, date):
    S = json.load(open(spec, encoding='utf-8')); items = S[kind]; check(items, kind)
    n = len(items); end = (8 * 4 * BEAT) - HOOK - CARD * n; total = HOOK + CARD * n + end
    if kind == 'season':
        big = [emoji(a['icon'], 500) for a in items]; small = [emoji(a['icon'], 150) for a in items]
    else:
        big = [medallion(a['art'], 430) for a in items]; small = [medallion(a['art'], 150) for a in items]
    mark = Image.open(f'{ASSETS}/brand/logo-mark-256.png').convert('RGBA').resize((80, 80))
    out = f'media/{date}'; os.makedirs(out, exist_ok=True); tmp = tempfile.mkdtemp(); cover_t = HOOK - 0.3
    for fr in range(int(total * FPS) + 1):
        t = fr / FPS
        if t < HOOK:
            im = Image.new('RGBA', (W, H), HOOK_BG[kind]); d = ImageDraw.Draw(im); p = ease(t / 0.35); dy = 30 * (1 - p)
            if kind == 'season':
                ctext(d, 320 + dy, "Your zodiac animal's", F(72, 600), INK)
            else:
                ctext(d, 320 + dy, "Your Day Master's", F(72, 600), INK)
            ctext(d, 425 + dy, "LUCKY DAY", F(150, 700), RED)
            ctext(d, 535 + dy, "this week", F(72, 600), INK)
            pill(d, W // 2, 615, S['range'], F(42, 600), INK, CREAM)
            cols = 4 if n == 12 else 5; gap = 240 if n == 12 else 190
            for i in range(n):
                r, c = divmod(i, cols); cx = W // 2 - (cols - 1) * gap / 2 + c * gap; cy = 900 + r * 230
                scaled(im, small[i], cx, cy, ease_back((t - 0.25 - i * 0.07) / 0.3) * (1 if n == 12 else 0.95))
            if kind == 'season':
                ctext(d, 1580, "Pause on yours", F(54, 600), INK)
                ctext(d, 1650, "Born in Jan or early Feb? Use the animal before.", F(34, 400), MUTED)
            else:
                ctext(d, 1400, "Your Day Master = the element", F(44, 500), INK)
                ctext(d, 1460, "of the DAY you were born. Pause on yours.", F(44, 500), INK)
                ctext(d, 1560, "Don't know it? Find it free at the end.", F(36, 400), MUTED)
        elif t < HOOK + CARD * n:
            i = int((t - HOOK) // CARD); lt = t - HOOK - i * CARD; a = items[i]
            im = Image.new('RGBA', (W, H), BG[a['element']]); d = ImageDraw.Draw(im); dots(d, n, i)
            p = ease((lt - 0.06) / 0.25); dy = 40 * (1 - p)
            if kind == 'season':
                scaled(im, big[i], W // 2, 520, ease_back(lt / 0.28))
                ctext(d, 820 + dy, a['name'].upper(), F(112, 700), INK)
                ctext(d, 905 + dy, a['years'], F(38, 500), MUTED)
                pill(d, W // 2, 945 + dy, f"Your Season: {a['season']}", F(34, 600), (255, 255, 255), INK, padx=34, h=68)
                boxes(d, 1040, dy, "LUCKY DAY", a['lucky'], a['lucky_tip'], "GO EASY", a['easy'], a['easy_tip'])
            else:
                scaled(im, big[i], W // 2, 520, ease_back(lt / 0.28))
                ctext(d, 820 + dy, a['dm'].upper(), F(104, 700), INK)
                ctext(d, 905 + dy, a['god'], F(48, 500), MUTED)
                boxes(d, 990, dy, f"LUCKY DAY · {a['lucky_force'].upper()} ({GLOSS[a['lucky_force']]})", a['lucky'], a['lucky_tip'],
                      f"GO EASY · {a['easy_force'].upper()} ({GLOSS.get(a['easy_force'], '')})", a['easy'], a['easy_tip'])
        else:
            lt = t - HOOK - CARD * n
            im = Image.new('RGBA', (W, H), HOOK_BG[kind]); d = ImageDraw.Draw(im)
            def beat(k, fn):
                if lt > k * 0.45:
                    fn(20 * (1 - ease((lt - k * 0.45) / 0.3)))
            if kind == 'season':
                beat(0, lambda o: (ctext(d, 430 + o, "Your animal is your", F(64, 500), INK), ctext(d, 525 + o, "SEASON", F(120, 700), INK)))
                beat(1, lambda o: (ctext(d, 680 + o, "The element of your birth DAY", F(56, 500), INK), ctext(d, 770 + o, "is your SKY.", F(120, 700), RED)))
                beat(2, lambda o: ctext(d, 930 + o, "Together: Sky & Season.", F(56, 600), INK))
            else:
                beat(0, lambda o: (ctext(d, 430 + o, "Your Day Master is your", F(64, 500), INK), ctext(d, 525 + o, "SKY", F(130, 700), RED)))
                beat(1, lambda o: (ctext(d, 680 + o, "Your zodiac animal is your", F(56, 500), INK), ctext(d, 770 + o, "SEASON.", F(120, 700), INK)))
                beat(2, lambda o: ctext(d, 930 + o, "Tomorrow 7pm: your animal's lucky day", F(44, 600), RED))
            if lt > 1.35:
                pill(d, W // 2, 1040, "Find yours free · skyandseason.com", F(44, 600), INK, CREAM, h=110)
                ctext(d, 1240, "Comment yours below" if kind == 'season' else "Comment your Day Master below", F(44, 500), INK)
                im.alpha_composite(mark, (W // 2 - 40, 1320))
        if abs(t - cover_t) < 0.5 / FPS: im.convert('RGB').save(f'{out}/cover.jpg', quality=90)
        im.convert('RGB').save(f'{tmp}/{fr:04d}.jpg', quality=92)
    music = f'{tmp}/tune.m4a'
    subprocess.run([sys.executable, f'{HERE}/music.py', music] + (['0', 'a'] if kind == 'season' else ['-3', 'b']), check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%04d.jpg', '-i', music,
                    '-map', '0:v', '-map', '1:a', '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-r', str(FPS),
                    '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', f'{out}/reel.mp4'], check=True)
    shutil.rmtree(tmp); print(kind, f'{out}/reel.mp4', round(total, 1), 's')

if __name__ == '__main__': render(*sys.argv[1:4])
