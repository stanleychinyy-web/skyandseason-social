"""Render "The Month Ahead with Sky & Season": reel (1080x1920, 60 s, 84 bpm) + 3 stories.
  python3 tools/monthly/render.py 2026-11            # reel + stories
  python3 tools/monthly/render.py 2026-11 stories    # stories only
Reads monthly/<ym>/data.json (month.py) and content.json (schema v2, see monthly/SERIES.md); writes monthly/<ym>/reel.mp4,
cover.jpg, story1-3.jpg and copies them to media/<post_date>/monthly-*.  Run from the repo root after `cd tools/reels && npm install`.

Lens (18 Oct): the Inner Constellation lens on BOTH halves (stem essence painting + season stage painting), never the Classic
stem-god / animal paintings, so the two halves match. Set "lens": "classic" in content.json only if Stanley asks for that look.
Look (v2, 18 Oct, after Stanley rejected the emoji version): premium and dark. Deep indigo, the site's own oil paintings of the
month's element and animal (tools/assets/art, the same art the website shows), slow Ken Burns on every painting, gold dust,
Newsreader serif in soft white with gold accents, thin gold rules. Opens on the approved Sky & Season orbit shot, closes on a
clean indigo page with the logo and wordmark. No emoji, no cartoon icons, no stickers."""
import json, sys, os, math, random, subprocess, tempfile, shutil, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
A = os.path.join(ROOT, 'tools', 'assets')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
W, H, FPS = 1080, 1920, 30
BPM = 84; BAR = 240 / BPM
INK0, INK1 = (18, 13, 43), (46, 32, 96)                       # background gradient
WHITE, SOFT, MUTED = (250, 247, 240), (214, 208, 232), (164, 156, 196)
GOLD, GOLD_L, GOLD_D = (212, 176, 106), (236, 212, 158), (160, 126, 62)
SLUG = {'Yang Wood': 'jia', 'Yin Wood': 'yi', 'Yang Fire': 'bing', 'Yin Fire': 'ding', 'Yang Earth': 'wu', 'Yin Earth': 'ji',
        'Yang Metal': 'geng', 'Yin Metal': 'xin', 'Yang Water': 'ren', 'Yin Water': 'gui'}
EL_SLUG = {'Wood': 'jia', 'Fire': 'bing', 'Earth': 'wu', 'Metal': 'geng', 'Water': 'ren'}
BR_SLUG = {'Rat': 'zi', 'Ox': 'chou', 'Tiger': 'yin', 'Rabbit': 'mao', 'Dragon': 'chen', 'Snake': 'si', 'Horse': 'wu', 'Goat': 'wei',
           'Monkey': 'shen', 'Rooster': 'you', 'Dog': 'xu', 'Pig': 'hai'}
EL_TINT = {'Wood': (96, 160, 110), 'Fire': (226, 120, 80), 'Earth': (214, 176, 106), 'Metal': (190, 196, 214), 'Water': (110, 150, 226)}

def serif(s, w=500, it=False): return ImageFont.truetype(f'{A}/fonts/newsreader-latin-{w}-{"italic" if it else "normal"}.woff', s)
def sans(s, w=400): return ImageFont.truetype(f'{A}/fonts/source-sans-3-latin-{w}-normal.woff', s)
def ease(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3
def fadein(t, start, dur=0.7): return ease((t - start) / dur)
def wrap(d, txt, f, maxw):
    out, cur = [], ''
    for w in txt.split():
        x = (cur + ' ' + w).strip()
        if d.textlength(x, font=f) <= maxw: cur = x
        else: out.append(cur); cur = w
    return out + [cur]
def block(d, y, txt, f, fill, maxw=W - 200, lead=1.3, align='c', x=None, alpha=1.0):
    col = fill + (int(255 * alpha),)
    lines = wrap(d, txt, f, maxw)
    for i, l in enumerate(lines):
        if align == 'c': d.text((W // 2, y + i * f.size * lead), l, font=f, fill=col, anchor='ma')
        else: d.text((x, y + i * f.size * lead), l, font=f, fill=col)
    return y + len(lines) * f.size * lead
def fit(d, txt, size, maxw, mk, minsize=30):
    while d.textlength(txt, font=mk(size)) > maxw and size > minsize: size -= 2
    return mk(size)

_BG = None
def night():
    global _BG
    if _BG is None:
        g = Image.new('RGB', (W, H)); dd = ImageDraw.Draw(g)
        for yy in range(H):
            k = yy / H; dd.line([(0, yy), (W, yy)], fill=tuple(int(INK0[i] + (INK1[i] - INK0[i]) * k) for i in range(3)))
        glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse([-300, -500, W + 300, 700], fill=90)
        g = Image.composite(Image.new('RGB', (W, H), (92, 64, 160)), g, glow.filter(ImageFilter.GaussianBlur(220)))
        _BG = g.convert('RGBA')
    return _BG.copy()
random.seed(11); DUST = [(random.random() * W, random.random() * H, random.uniform(1.5, 4), random.uniform(0.25, 1.0), random.random() * 6.28) for _ in range(90)]
def dust(im, t, alpha=1.0):
    d = ImageDraw.Draw(im, 'RGBA')
    for x, y, r, sp, ph in DUST:
        yy = (y - t * 18 * sp) % H; xx = x + 12 * math.sin(t * 0.5 + ph); a = int((80 + 90 * math.sin(t * 1.1 + ph)) * alpha)
        if a > 0: d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=GOLD_L + (a,))
def rule(d, y, w=120, alpha=1.0): d.line([(W // 2 - w // 2, y), (W // 2 + w // 2, y)], fill=GOLD + (int(255 * alpha),), width=2)
def kicker(d, y, txt, alpha=1.0, col=GOLD): d.text((W // 2, y), txt, font=sans(30, 700), fill=col + (int(255 * alpha),), anchor='mm')

_ART = {}
def art(kind, slug):
    k = (kind, slug)
    if k not in _ART: _ART[k] = Image.open(f'{A}/art/{kind}/{slug}.jpg').convert('RGB')
    return _ART[k]
def painting_panel(im, src, y0, h, t, dur, alpha=1.0, w=W - 120, zoom=0.07):
    """A framed painting with a slow push-in, plus a blurred, darkened echo of it behind as the page's atmosphere."""
    p = min(1, t / max(dur, 0.01)); s = 1 + zoom * p
    pw, ph = w, int(w * src.height / src.width)
    if ph > h: ph = h; pw = int(h * src.width / src.height)
    big = src.resize((int(pw * s), int(ph * s)), Image.LANCZOS)
    cx, cy = big.width // 2, big.height // 2; crop = big.crop((cx - pw // 2, cy - ph // 2, cx - pw // 2 + pw, cy - ph // 2 + ph)).convert('RGBA')
    echo = src.resize((W, int(W * src.height / src.width)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(60))
    echo = ImageEnhance.Brightness(echo).enhance(0.45).convert('RGBA')
    fe = Image.new('L', echo.size, 0); fd = ImageDraw.Draw(fe); eh = echo.height
    for yy in range(eh):
        k = min(yy, eh - 1 - yy) / (eh * 0.35); fd.line([(0, yy), (W, yy)], fill=int(140 * alpha * min(1, k)))
    echo.putalpha(fe); ey = y0 + ph // 2 - echo.height // 2; im.alpha_composite(echo, (0, ey))
    mask = Image.new('L', (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], 28, fill=int(255 * alpha))
    crop.putalpha(mask); x0 = (W - pw) // 2; im.alpha_composite(crop, (x0, y0))
    d = ImageDraw.Draw(im, 'RGBA'); d.rounded_rectangle([x0 - 6, y0 - 6, x0 + pw + 6, y0 + ph + 6], 32, outline=GOLD + (int(150 * alpha),), width=2)
    return y0 + ph
def atmosphere(im, src, cy, alpha=0.5):
    """A faint, blurred, darkened echo of a painting low on the page: colour and depth behind the type."""
    echo = src.resize((W + 200, int((W + 200) * src.height / src.width)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(70))
    echo = ImageEnhance.Brightness(echo).enhance(0.75).convert('RGBA'); eh = echo.height
    fe = Image.new('L', echo.size, 0); fd = ImageDraw.Draw(fe)
    for yy in range(eh):
        k = min(yy, eh - 1 - yy) / (eh * 0.4); fd.line([(0, yy), (echo.width, yy)], fill=int(230 * alpha * min(1, k)))
    echo.putalpha(fe); im.alpha_composite(echo, (-100, cy - eh // 2))
def medallion(src, size, tint=None):
    c = min(src.size); x0 = (src.width - c) // 2; y0 = (src.height - c) // 2
    im = src.crop((x0, y0, x0 + c, y0 + c)).resize((size, size), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', (size * 4, size * 4), 0); ImageDraw.Draw(m).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255); im.putalpha(m.resize((size, size), Image.LANCZOS))
    ring = Image.new('RGBA', (size + 12, size + 12), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse([0, 0, size + 11, size + 11], outline=(tint or GOLD) + (220,), width=3)
    ring.alpha_composite(im, (6, 6)); return ring

def tidy(C):
    e = C['energy']
    for k in ('sky_name', 'season_name'): e[k] = re.sub(r'^\s*(sky|season)\s*[:·-]\s*', '', e[k], flags=re.I)
    C['stories']['question']['options'] = [re.sub(r'^\s*\d+\s*[·.)-]\s*', '', o) for o in C['stories']['question']['options']]
    return C

# ---------- reel ----------
def render(ym):
    folder = os.path.join(ROOT, 'monthly', ym)
    D = json.load(open(f'{folder}/data.json', encoding='utf-8')); C = tidy(json.load(open(f'{folder}/content.json', encoding='utf-8')))
    bm = D['bazi_month']; month = D['gregorian_month']; mname = month.split()[0]
    lens = C.get('lens', 'inner'); ST, BR = ('stems', 'branches') if lens == 'classic' else ('inner-stems', 'inner-branches')
    sky_art = art(ST, SLUG[bm['stem']]); sea_art = art(BR, BR_SLUG[bm['branch']])
    sky_md, sea_md = medallion(sky_art, 150), medallion(sea_art, 150)
    el_md = {el: medallion(art(ST, EL_SLUG[el]), 118, EL_TINT[el]) for el in ['Wood', 'Fire', 'Earth', 'Metal', 'Water']}
    mark = Image.open(f'{A}/brand/logo-mark-256.png').convert('RGBA').resize((140, 140))
    word = Image.open(f'{A}/brand/logo-wordmark-1200w.png').convert('RGBA'); word = word.resize((720, int(720 * word.height / word.width)))
    wa = word.getchannel('A'); word = Image.new('RGBA', word.size, GOLD_L + (255,)); word.putalpha(wa)
    hook_dir = tempfile.mkdtemp()
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'{A}/monthly/hook-orbit.mp4', '-vf', f'fps={FPS},scale={W}:{H}', f'{hook_dir}/%04d.jpg'], check=True)
    hook_frames = sorted(os.listdir(hook_dir))
    end_bg = Image.open(f'{A}/monthly/end-still.jpg').convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(14))
    end_bg = Image.blend(end_bg, Image.new('RGB', (W, H), INK0), 0.55).convert('RGBA')
    # section → (start bar, end bar)
    S = [('hook', 0, 2), ('intro', 2, 3.5), ('sky', 3.5, 5.5), ('season', 5.5, 7.5), ('meaning', 7.5, 9.5), ('t0', 9.5, 11), ('t1', 11, 12.5),
         ('t2', 12.5, 14), ('opp', 14, 15.5), ('chal', 15.5, 17), ('elements', 17, 19.5), ('close', 19.5, 21)]
    bars = 21; total = bars * BAR
    tmp = tempfile.mkdtemp(); start_txt = D['starts']['sgt'].replace(' SGT', '')
    for fr in range(int(total * FPS)):
        t = fr / FPS; sec, a0, a1 = next(s for s in S if s[1] * BAR <= t < s[2] * BAR); lt = t - a0 * BAR; dur = (a1 - a0) * BAR
        if sec == 'hook':
            im = Image.open(f'{hook_dir}/{hook_frames[min(fr, len(hook_frames) - 1)]}').convert('RGBA')
            sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([0, 0, W, 980], fill=(8, 5, 26, 150)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(90)))
            d = ImageDraw.Draw(im, 'RGBA'); kicker(d, 250, f'THE MONTH AHEAD · {month.upper()}', col=GOLD_L)
            hf = fit(d, max(C['hook'], key=len), 92, W - 140, lambda s: serif(s, 500))
            for i, l in enumerate(C['hook']):
                a = fadein(lt, 0.3 + i * 1.0, 0.9); d.text((W // 2, 360 + i * int(hf.size * 1.3) + 18 * (1 - a)), l, font=hf, fill=WHITE + (int(255 * a),), anchor='ma')
            if lt > dur - 0.7: k = ease((lt - (dur - 0.7)) / 0.7); bg = night(); bg.putalpha(int(255 * k)); im.alpha_composite(bg)
        elif sec == 'close':
            im = end_bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); dust(im, t, 0.6)
            im.alpha_composite(mark, (W // 2 - 70, 470))
            for i, l in enumerate(C['close'][0].split('. ')):
                l = l if l.endswith('.') else l + '.'
                b = fadein(lt, 0.3 + i * 0.6); d.text((W // 2, 690 + i * 108), l, font=serif(86, 600, True), fill=WHITE + (int(255 * b),), anchor='ma')
            c = fadein(lt, 2.3); block(d, 1080, C['close'][1], sans(44, 400), SOFT, maxw=W - 240, alpha=c)
            if lt > 2.7:
                w2 = word.copy(); w2.putalpha(w2.getchannel('A').point(lambda v: int(v * fadein(lt, 2.7)))); im.alpha_composite(w2, (W // 2 - w2.width // 2, 1300))
                d.text((W // 2, 1440), 'skyandseason.com', font=sans(40, 600), fill=GOLD_L + (int(255 * fadein(lt, 2.9)),), anchor='mm')
        else:
            im = night(); d = ImageDraw.Draw(im, 'RGBA')
            if sec == 'intro':
                atmosphere(im, sky_art, 1500, 0.8); d = ImageDraw.Draw(im, 'RGBA'); dust(im, t)
                a = fadein(lt, 0.1); f1 = fit(d, C['intro']['line1'], 64, W - 160, lambda z: serif(z, 400)); y = block(d, 740, C['intro']['line1'], f1, SOFT, maxw=W - 160, alpha=a)
                b = fadein(lt, 1.0); f2 = fit(d, C['intro']['line2'], 100, W - 140, lambda z: serif(z, 500)); y = block(d, y + 40, C['intro']['line2'], f2, WHITE, maxw=W - 140, alpha=b)
                rule(d, y + 50, 140, b); d.text((W // 2, y + 120), f'From {start_txt}', font=sans(36, 600), fill=GOLD + (int(255 * b),), anchor='mm')
            elif sec in ('sky', 'season'):
                e = C['energy']; src = sky_art if sec == 'sky' else sea_art
                a = fadein(lt, 0.05, 0.8); y = painting_panel(im, src, 300, 820, lt, dur, alpha=a); dust(im, t, 0.5)
                d = ImageDraw.Draw(im, 'RGBA'); kicker(d, 240, 'THE SKY' if sec == 'sky' else 'THE SEASON', a)
                d.text((W // 2, y + 70), e['sky_label' if sec == 'sky' else 'season_label'], font=sans(32, 600), fill=MUTED + (int(255 * a),), anchor='mm')
                nm = e['sky_name' if sec == 'sky' else 'season_name']; nf = fit(d, nm, 104, W - 120, lambda z: serif(z, 500), 60)
                b = fadein(lt, 0.6); yy = block(d, y + 120, nm, nf, WHITE, maxw=W - 120, alpha=b)
                c = fadein(lt, 1.4); rule(d, yy + 30, 120, c); block(d, yy + 60, e['sky_plain' if sec == 'sky' else 'season_plain'], serif(52, 400, True), SOFT, maxw=W - 180, alpha=c)
            elif sec == 'meaning':
                e = C['energy']; dust(im, t)
                a = fadein(lt, 0.05); kicker(d, 240, 'TOGETHER', a)
                im.alpha_composite(sky_md, (W // 2 - 300, 330)); im.alpha_composite(sea_md, (W // 2 + 140, 330))
                for cx, nm in ((W // 2 - 220, e['sky_name']), (W // 2 + 220, e['season_name'])):
                    for k, l in enumerate(wrap(d, nm, sans(28, 600), 300)): d.text((cx, 520 + k * 34), l, font=sans(28, 600), fill=MUTED + (int(255 * a),), anchor='mm')
                d.text((W // 2, 405), 'over', font=sans(30, 400), fill=GOLD + (int(255 * a),), anchor='mm')
                b = fadein(lt, 0.8); block(d, 640, e['image'], serif(80, 400, True), WHITE, maxw=W - 140, alpha=b)
                c = fadein(lt, 2.0); rule(d, 900, 120, c); block(d, 950, e['meaning'], sans(48, 400), SOFT, maxw=W - 200, alpha=c)
            elif sec in ('t0', 't1', 't2'):
                i = int(sec[1]); th = C['themes'][i]; atmosphere(im, sea_art if i % 2 else sky_art, 1560, 0.8); d = ImageDraw.Draw(im, 'RGBA'); dust(im, t, 0.7)
                a = fadein(lt, 0.05); d.text((W // 2, 240), f'{i + 1} / 3', font=sans(30, 600), fill=MUTED + (int(255 * a),), anchor='mm')
                kicker(d, 600, th['area'].upper(), a)
                b = fadein(lt, 0.4); y = block(d, 680, th['headline'], serif(100, 500), WHITE, maxw=W - 120, alpha=b)
                c = fadein(lt, 1.1); rule(d, y + 50, 120, c); block(d, y + 100, th['line'], sans(52, 400), SOFT, maxw=W - 180, alpha=c)
            elif sec in ('opp', 'chal'):
                o = C['opportunity' if sec == 'opp' else 'challenge']; atmosphere(im, sky_art if sec == 'opp' else sea_art, 1560, 0.8); d = ImageDraw.Draw(im, 'RGBA'); dust(im, t, 0.7)
                a = fadein(lt, 0.05); kicker(d, 600, 'THE OPPORTUNITY' if sec == 'opp' else 'THE CATCH', a)
                b = fadein(lt, 0.4); y = block(d, 680, o['headline'], serif(100, 500), WHITE, maxw=W - 120, alpha=b)
                c = fadein(lt, 1.1); rule(d, y + 50, 120, c); y = block(d, y + 100, o['line'], sans(52, 400), SOFT, maxw=W - 180, alpha=c)
                if lt > 2.0:
                    g = fadein(lt, 2.0); f = fit(d, 'Try: ' + o['tip'], 42, W - 260, lambda s: sans(s, 600)); tw = d.textlength('Try: ' + o['tip'], font=f)
                    d.rounded_rectangle([W // 2 - tw / 2 - 44, y + 60, W // 2 + tw / 2 + 44, y + 160], 50, outline=GOLD + (int(255 * g),), width=2)
                    d.text((W // 2, y + 110), 'Try: ' + o['tip'], font=f, fill=GOLD_L + (int(255 * g),), anchor='mm')
            elif sec == 'elements':
                E = C['elements']; dust(im, t, 0.5)
                a = fadein(lt, 0.05); block(d, 230, E['intro1'], serif(56, 400), SOFT, alpha=a); block(d, 305, E['intro2'], serif(56, 500), WHITE, alpha=a)
                y = 440
                for j, el in enumerate(['Wood', 'Fire', 'Earth', 'Metal', 'Water']):
                    b = fadein(lt, 0.5 + j * 0.75, 0.6)
                    if b <= 0: continue
                    md = el_md[el].copy(); md.putalpha(md.getchannel('A').point(lambda v: int(v * b))); im.alpha_composite(md, (90, y))
                    d.text((240, y + 4), E['cards'][el]['people'], font=sans(34, 700), fill=EL_TINT[el] + (int(255 * b),))
                    f = fit(d, E['cards'][el]['line'], 40, W - 340, lambda s: sans(s, 400), 34); yy = block(d, y + 50, E['cards'][el]['line'], f, WHITE, maxw=W - 340, align='l', x=240, lead=1.12, alpha=b)
                    yy = int(max(yy, y + 124)); d.line([(240, yy + 14), (W - 90, yy + 14)], fill=GOLD_D + (int(120 * b),), width=1)
                    y = yy + 34
                c = fadein(lt, 4.6); d.text((W // 2, y + 60), "Don't know yours? It's free at skyandseason.com", font=sans(36, 600), fill=GOLD + (int(255 * c),), anchor='mm')
        if abs(t - 2.9) < 0.5 / FPS: im.convert('RGB').save(f'{folder}/cover.jpg', quality=92)
        im.convert('RGB').save(f'{tmp}/{fr:05d}.jpg', quality=90)
    music = f'{tmp}/m.m4a'
    subprocess.run([sys.executable, f'{HERE}/music.py', music, str(bars), str((int(ym[5:]) - 1) % 4)], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', music, '-map', '0:v', '-map', '1:a',
                    '-af', 'loudnorm=I=-16:TP=-1.5', '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-r', str(FPS),
                    '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', f'{folder}/reel.mp4'], check=True)
    shutil.rmtree(tmp); shutil.rmtree(hook_dir)
    stories(D, C, folder)
    pd = D['post_date']; md = os.path.join(ROOT, 'media', pd); os.makedirs(md, exist_ok=True)
    for n in ['reel.mp4', 'cover.jpg', 'story1.jpg', 'story2.jpg', 'story3.jpg']: shutil.copy(f'{folder}/{n}', f'{md}/monthly-{n}')
    print('month ahead', ym, round(total, 1), 's ->', md)

# ---------- stories ----------
def stories(D, C, folder):
    bm = D['bazi_month']; month = D['gregorian_month']; S = C['stories']
    lens = C.get('lens', 'inner'); ST, BR = ('stems', 'branches') if lens == 'classic' else ('inner-stems', 'inner-branches')
    def base(k):
        im = night(); dust(im, 3 + k * 2.1, 0.6); d = ImageDraw.Draw(im, 'RGBA'); kicker(d, 230, f'THE MONTH AHEAD · {month.upper()}')
        for j in range(3):
            x = W // 2 - 50 + j * 50; d.rounded_rectangle([x - 18, 268, x + 18, 274], 3, fill=GOLD if j == k else (255, 255, 255, 70))
        return im, d
    e = C['energy']
    # 1 teaser: the month's painting
    im, d = base(0); t = S['teaser']
    y = painting_panel(im, art(ST, SLUG[bm['stem']]), 330, 760, 0.5, 1); d = ImageDraw.Draw(im, 'RGBA')
    kick = t['kicker'] if 'month ahead' not in t['kicker'].lower() else f"{month.split()[0]} in one picture"
    d.text((W // 2, y + 60), kick.upper(), font=sans(30, 700), fill=GOLD, anchor='mm')
    yy = y + 110
    for l in t['headline']: yy = block(d, yy, l, serif(84, 500), WHITE, maxw=W - 120, lead=1.15)
    rule(d, yy + 30, 120); yy = block(d, yy + 70, t['line'], sans(44, 400), SOFT, maxw=W - 200)
    d.rounded_rectangle([W // 2 - 330, 1680, W // 2 + 330, 1780], 50, outline=GOLD, width=2); d.text((W // 2, 1730), t['pointer'], font=sans(36, 600), fill=GOLD_L, anchor='mm')
    im.convert('RGB').save(f'{folder}/story1.jpg', quality=92)
    # 2 question: reply with a number (a native poll can be added by hand)
    im, d = base(1); q = S['question']
    im.alpha_composite(medallion(art(BR, BR_SLUG[bm['branch']]), 220), (W // 2 - 116, 330))
    y = block(d, 640, q['question'], serif(84, 500), WHITE, maxw=W - 140) + 50
    for i, o in enumerate(q['options']):
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).rounded_rectangle([110, y, W - 110, y + 132], 66, outline=GOLD + (170,), width=2, fill=(255, 255, 255, 16)); im.alpha_composite(ov); d = ImageDraw.Draw(im, 'RGBA')
        d.ellipse([150, y + 26, 230, y + 106], fill=GOLD); d.text((190, y + 66), str(i + 1), font=sans(44, 700), fill=INK0, anchor='mm')
        d.text((270, y + 66), o, font=sans(48, 600), fill=WHITE, anchor='lm'); y += 160
    block(d, y + 40, q['reply_line'], sans(40, 600), GOLD_L, maxw=W - 220)
    im.convert('RGB').save(f'{folder}/story2.jpg', quality=92)
    # 3 conversion: the five element groups
    im, d = base(2); c = S['conversion']; E = C['elements']
    y = block(d, 340, c['headline'], serif(80, 500), WHITE, maxw=W - 140)
    y = block(d, y + 20, c['line'], sans(40, 400), SOFT, maxw=W - 200) + 40
    for el in ['Wood', 'Fire', 'Earth', 'Metal', 'Water']:
        md = medallion(art(ST, EL_SLUG[el]), 104, EL_TINT[el]); im.alpha_composite(md, (100, int(y)))
        d.text((240, y + 2), E['cards'][el]['people'], font=sans(32, 700), fill=EL_TINT[el])
        f = fit(d, E['cards'][el]['line'], 38, W - 340, lambda s: sans(s, 400), 32); yy = block(d, y + 46, E['cards'][el]['line'], f, WHITE, maxw=W - 340, align='l', x=240, lead=1.12)
        yy = int(max(yy, y + 112)); d.line([(240, yy + 12), (W - 100, yy + 12)], fill=GOLD_D + (120,), width=1); y = yy + 30
    y += 40; d.rounded_rectangle([110, y, W - 110, y + 120], 60, fill=GOLD); d.text((W // 2, y + 60), c['invitation'], font=serif(52, 500), fill=INK0, anchor='mm')
    d.text((W // 2, y + 190), c['link_line'], font=sans(38, 600), fill=GOLD_L, anchor='mm')
    im.convert('RGB').save(f'{folder}/story3.jpg', quality=92)

if __name__ == '__main__':
    ym = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == 'stories':
        f = os.path.join(ROOT, 'monthly', ym); stories(json.load(open(f'{f}/data.json')), tidy(json.load(open(f'{f}/content.json'))), f)
    else:
        render(ym)
