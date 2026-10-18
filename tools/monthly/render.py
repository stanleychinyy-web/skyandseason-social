"""Render "The Month Ahead with Sky & Season": reel (1080x1920, ~60 s, 84 bpm, one section per bar group) + 3 stories.
  python3 tools/monthly/render.py 2026-11
Reads monthly/<ym>/data.json (month.py) and content.json (the writer), writes monthly/<ym>/reel.mp4, cover.jpg,
story1-3.jpg and copies them to media/<post_date>/monthly-*.  Run from the repo root after `cd tools/reels && npm install`.
Look: twilight-to-dawn. Opens on the approved Sky & Season orbit shot, then soft lavender pages with indigo type and
gold accents, Noto emoji for the elements and animals (same style as the daily posts), clean indigo closing page."""
import json, sys, os, io, math, random, subprocess, tempfile, shutil, datetime
import cairosvg
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
A = os.path.join(ROOT, 'tools', 'assets'); NM = os.path.join(ROOT, 'tools', 'reels', 'node_modules')
sys.path.insert(0, os.path.join(ROOT, 'tools')); sys.path.insert(0, os.path.join(ROOT, 'tools', 'reels'))
from daytype import STEMS
W, H, FPS = 1080, 1920, 30
BPM = 84; BAR = 240 / BPM
INK = (38, 28, 88); SOFT = (92, 82, 140); GOLD = (184, 140, 60); GOLD_L = (232, 200, 130); WHITE = (255, 253, 248)
TOP, BOT = (247, 243, 255), (214, 204, 246)
STEM_ICON = {'Yang Wood': 'deciduous-tree', 'Yin Wood': 'herb', 'Yang Fire': 'sun-with-face', 'Yin Fire': 'candle', 'Yang Earth': 'mountain',
             'Yin Earth': 'sheaf-of-rice', 'Yang Metal': 'axe', 'Yin Metal': 'gem-stone', 'Yang Water': 'water-wave', 'Yin Water': 'cloud-with-rain'}
ANIMAL_ICON = {'Rat': 'mouse-face', 'Ox': 'cow-face', 'Tiger': 'tiger-face', 'Rabbit': 'rabbit-face', 'Dragon': 'dragon-face', 'Snake': 'snake',
               'Horse': 'horse-face', 'Goat': 'goat', 'Monkey': 'monkey-face', 'Rooster': 'rooster', 'Dog': 'dog-face', 'Pig': 'pig-face'}
EL_ICON = {'Wood': 'deciduous-tree', 'Fire': 'fire', 'Earth': 'mountain', 'Metal': 'gem-stone', 'Water': 'water-wave'}
THEME_ICON = ['briefcase', 'two-hearts', 'seedling']

def serif(s, w=500, it=False): return ImageFont.truetype(f'{A}/fonts/newsreader-latin-{w}-{"italic" if it else "normal"}.woff', s)
def sans(s, w=400): return ImageFont.truetype(f'{A}/fonts/source-sans-3-latin-{w}-normal.woff', s)
_IC = None
def emoji(key, size):
    global _IC
    _IC = _IC or json.load(open(f'{NM}/@iconify-json/noto/icons.json'))
    ic = _IC['icons'][key]; w = ic.get('width', _IC.get('width', 128)); h = ic.get('height', _IC.get('height', 128))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{size}" height="{size}">{ic["body"]}</svg>'
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
def ease(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3
def wrap(d, txt, f, maxw):
    out, cur = [], ''
    for w in txt.split():
        x = (cur + ' ' + w).strip()
        if d.textlength(x, font=f) <= maxw: cur = x
        else: out.append(cur); cur = w
    return out + [cur]
def block(d, y, txt, f, fill, maxw=W - 200, lead=1.28, align='c', x=None, alpha=1.0):
    fill = fill + (int(255 * alpha),) if len(fill) == 3 else fill
    for i, l in enumerate(wrap(d, txt, f, maxw)):
        if align == 'c': d.text((W // 2, y + i * f.size * lead), l, font=f, fill=fill, anchor='ma')
        else: d.text((x, y + i * f.size * lead), l, font=f, fill=fill)
    return y + len(wrap(d, txt, f, maxw)) * f.size * lead
def fadein(t, start, dur=0.6): return ease((t - start) / dur)

_BG = None
def dawn():
    global _BG
    if _BG is None:
        g = Image.new('RGB', (W, H)); dd = ImageDraw.Draw(g)
        for yy in range(H):
            k = yy / H; dd.line([(0, yy), (W, yy)], fill=tuple(int(TOP[i] + (BOT[i] - TOP[i]) * k) for i in range(3)))
        glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse([-200, 1200, W + 200, 2400], fill=110)
        g = Image.composite(Image.new('RGB', (W, H), (255, 236, 205)), g, glow.filter(ImageFilter.GaussianBlur(160)))
        _BG = g.convert('RGBA')
    return _BG.copy()
random.seed(7); DUST = [(random.random() * W, random.random() * H, random.uniform(2, 5), random.uniform(0.2, 1.0), random.random() * 6.28) for _ in range(70)]
def dust(im, t):
    d = ImageDraw.Draw(im, 'RGBA')
    for x, y, r, sp, ph in DUST:
        yy = (y - t * 22 * sp) % H; xx = x + 14 * math.sin(t * 0.6 + ph); a = int(90 + 80 * math.sin(t * 1.3 + ph))
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=GOLD_L + (max(0, a),))
def ripples(im, t, cx, cy):
    d = ImageDraw.Draw(im, 'RGBA')
    for k in range(4):
        p = ((t * 0.35) + k / 4) % 1; rx, ry = 120 + 380 * p, 26 + 80 * p
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(110, 140, 220, int(150 * (1 - p))), width=4)
def kicker(d, y, txt, col=GOLD): d.text((W // 2, y), txt, font=sans(34, 700), fill=col, anchor='mm')
def card(d, box, a=235): d.rounded_rectangle(box, 44, fill=(255, 255, 255, a))

import re
def tidy(C):
    """Drop labels the template already draws (writers often repeat them)."""
    e = C['energy']; e['sky'] = re.sub(r'^\s*sky\s*[:·-]\s*', '', e['sky'], flags=re.I); e['season'] = re.sub(r'^\s*season\s*[:·-]\s*', '', e['season'], flags=re.I)
    for k in ('sky', 'season'): e[k] = e[k][:1].upper() + e[k][1:]
    C['personal']['day_master_lines'] = {k: re.sub(r'^.*?:\s*', '', v) if ':' in v else v for k, v in C['personal']['day_master_lines'].items()}
    q = C['stories']['question']; q['options'] = [re.sub(r'^\s*\d+\s*[·.)-]\s*', '', o) for o in q['options']]
    return C

def render(ym):
    folder = os.path.join(ROOT, 'monthly', ym)
    D = json.load(open(f'{folder}/data.json', encoding='utf-8')); C = tidy(json.load(open(f'{folder}/content.json', encoding='utf-8')))
    bm = D['bazi_month']; month_name = D['gregorian_month'].split()[0]
    sky_ic = emoji(STEM_ICON[bm['stem']], 300); sea_ic = emoji(ANIMAL_ICON[bm['branch']], 300)
    br_ic = emoji(ANIMAL_ICON[bm['branch']], 190); th_ic = [emoji(k, 200) for k in THEME_ICON]
    op_ic, ch_ic = emoji('sparkles', 200), emoji('snowflake', 200)
    dm_ic = {k: emoji(v, 76) for k, v in STEM_ICON.items()}
    mark = Image.open(f'{A}/brand/logo-mark-256.png').convert('RGBA').resize((150, 150))
    word = Image.open(f'{A}/brand/logo-wordmark-1200w.png').convert('RGBA'); word = word.resize((760, int(760 * word.height / word.width)))
    wa = word.getchannel('A'); word = Image.new('RGBA', word.size, GOLD_L + (255,)); word.putalpha(wa)
    hook_dir = tempfile.mkdtemp()
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'{A}/monthly/hook-orbit.mp4', '-vf', f'fps={FPS},scale={W}:{H}', f'{hook_dir}/%04d.jpg'], check=True)
    hook_frames = sorted(os.listdir(hook_dir))
    end_bg = Image.open(f'{A}/monthly/end-still.jpg').convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(10))
    end_bg = Image.blend(end_bg, Image.new('RGB', (W, H), (30, 22, 70)), 0.45).convert('RGBA')
    S = {'hook': (0, 2), 'energy': (2, 6), 't0': (6, 8), 't1': (8, 10), 't2': (10, 12), 'opp': (12, 14), 'chal': (14, 16), 'dm': (16, 19), 'close': (19, 21)}
    bars = 21; total = bars * BAR
    tmp = tempfile.mkdtemp(); start_txt = D['starts']['sgt'].replace(' SGT', '').replace(', ', ' · ')
    for fr in range(int(total * FPS)):
        t = fr / FPS; sec = next(k for k, (a, b) in S.items() if a * BAR <= t < b * BAR); lt = t - S[sec][0] * BAR
        if sec == 'hook':
            im = Image.open(f'{hook_dir}/{hook_frames[min(fr, len(hook_frames) - 1)]}').convert('RGBA')
            sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([0, 0, W, 900], fill=(10, 6, 30, 120))
            im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(80))); d = ImageDraw.Draw(im, 'RGBA')
            kicker(d, 250, f'THE MONTH AHEAD · {D["gregorian_month"].upper()}', GOLD_L)
            hs = 92
            while max(d.textlength(l, font=serif(hs, 600)) for l in C['hook']) > W - 150: hs -= 2
            for i, l in enumerate(C['hook']):
                a = fadein(lt, 0.25 + i * 0.9); d.text((W // 2, 360 + i * int(hs * 1.25) + 20 * (1 - a)), l, font=serif(hs, 600), fill=WHITE + (int(255 * a),), anchor='ma')
            if lt > BAR * 2 - 0.6:   # cross-fade into dawn
                k = ease((lt - (BAR * 2 - 0.6)) / 0.6); bg = dawn(); bg.putalpha(int(255 * k)); im.alpha_composite(bg)
        elif sec == 'close':
            im = end_bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); a = fadein(lt, 0.1, 0.8)
            ink = WHITE + (int(255 * a),)
            im.alpha_composite(mark, (W // 2 - 75, 470))
            for i, l in enumerate(C['close'][0].split('. ')):
                l = l if l.endswith('.') else l + '.'
                b = fadein(lt, 0.4 + i * 0.55); d.text((W // 2, 700 + i * 105), l, font=serif(84, 600, True), fill=WHITE + (int(255 * b),), anchor='ma')
            c = fadein(lt, 2.2); block(d, 1080, C['close'][1], sans(44, 400), (236, 230, 255), maxw=W - 240, alpha=c)
            if lt > 2.6:
                w2 = word.copy(); w2.putalpha(w2.getchannel('A').point(lambda v: int(v * fadein(lt, 2.6)))); im.alpha_composite(w2, (W // 2 - w2.width // 2, 1300))
                d.text((W // 2, 1440), 'skyandseason.com', font=sans(40, 600), fill=GOLD_L + (int(255 * fadein(lt, 2.8)),), anchor='mm')
        else:
            im = dawn(); dust(im, t); d = ImageDraw.Draw(im, 'RGBA')
            kicker(d, 230, f'THE MONTH AHEAD · {month_name.upper()}')
            if sec == 'energy':
                e = C['energy']
                d.text((W // 2, 300), f'From {start_txt}', font=sans(36, 600), fill=SOFT, anchor='mm')
                ripples(im, t, W // 2, 760)
                a = fadein(lt, 0.1); im.alpha_composite(sky_ic, (W // 2 - 150, 380 + int(30 * (1 - a))))
                if lt > 0.7: im.alpha_composite(br_ic, (W // 2 - 95, 670))
                y = 900; d.text((W // 2, y), 'SKY', font=sans(30, 700), fill=GOLD, anchor='mm')
                block(d, y + 30, e['sky'], serif(56, 600), INK, alpha=fadein(lt, 0.3))
                if lt > 1.6:
                    d.text((W // 2, 1080), 'SEASON', font=sans(30, 700), fill=GOLD, anchor='mm')
                    block(d, 1110, e['season'], serif(56, 600), INK, alpha=fadein(lt, 1.6))
                if lt > 3.6:
                    block(d, 1290, e['image'], serif(64, 400, True), INK, alpha=fadein(lt, 3.6))
                if lt > 5.6:
                    block(d, 1450, e['meaning'], sans(44, 400), SOFT, maxw=W - 220, alpha=fadein(lt, 5.6))
            elif sec in ('t0', 't1', 't2'):
                i = int(sec[1]); th = C['themes'][i]
                d.text((W // 2, 300), f'{i + 1} / 3', font=sans(34, 600), fill=SOFT, anchor='mm')
                a = fadein(lt, 0.05); im.alpha_composite(th_ic[i], (W // 2 - 100, 480 + int(30 * (1 - a))))
                d.text((W // 2, 760), th['area'].upper(), font=sans(42, 700), fill=GOLD + (int(255 * a),), anchor='mm')
                y = block(d, 820, th['headline'], serif(96, 600), INK, maxw=W - 140, alpha=fadein(lt, 0.3))
                card(d, [80, y + 60, W - 80, y + 60 + 70 + 70 * len(wrap(d, th['line'], sans(56), W - 280))], int(225 * fadein(lt, 0.9)))
                block(d, y + 95, th['line'], sans(56, 400), INK, maxw=W - 280, alpha=fadein(lt, 0.9))
            elif sec in ('opp', 'chal'):
                o = C['opportunity' if sec == 'opp' else 'challenge']
                a = fadein(lt, 0.05); im.alpha_composite(op_ic if sec == 'opp' else ch_ic, (W // 2 - 100, 470 + int(30 * (1 - a))))
                d.text((W // 2, 750), 'OPPORTUNITY' if sec == 'opp' else 'WATCH FOR', font=sans(42, 700), fill=GOLD + (int(255 * a),), anchor='mm')
                y = block(d, 810, o['headline'], serif(92, 600), INK, maxw=W - 140, alpha=fadein(lt, 0.3))
                y = block(d, y + 40, o['line'], sans(54, 400), INK, maxw=W - 200, alpha=fadein(lt, 1.0))
                if lt > 2.0:
                    f = sans(42, 600); tw = d.textlength('Try: ' + o['tip'], font=f)
                    if tw > W - 200: f = sans(36, 600); tw = d.textlength('Try: ' + o['tip'], font=f)
                    d.rounded_rectangle([W // 2 - tw / 2 - 40, y + 50, W // 2 + tw / 2 + 40, y + 150], 50, fill=INK + (int(255 * fadein(lt, 2.0)),))
                    d.text((W // 2, y + 100), 'Try: ' + o['tip'], font=f, fill=WHITE, anchor='mm')
            elif sec == 'dm':
                p = C['personal']
                block(d, 290, p['line'], serif(56, 600), INK, maxw=W - 160, alpha=fadein(lt, 0.05))
                y = 440
                for j, dmx in enumerate(D['day_masters']):
                    a = fadein(lt, 0.4 + j * 0.12, 0.4)
                    if a <= 0: continue
                    card(d, [70, y, W - 70, y + 104], int(225 * a))
                    ic = dm_ic[dmx['day_master']]; im.alpha_composite(ic, (95, y + 14))
                    d.text((195, y + 10), f"{dmx['day_master']} · {dmx['month_force']}", font=sans(34, 700), fill=INK + (int(255 * a),))
                    d.text((195, y + 54), p['day_master_lines'][dmx['day_master']], font=sans(33, 400), fill=SOFT + (int(255 * a),))
                    y += 112
        if abs(t - 2.6) < 0.5 / FPS: im.convert('RGB').save(f'{folder}/cover.jpg', quality=92)
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

def stories(D, C, folder):
    bm = D['bazi_month']; month = D['gregorian_month']; S = C['stories']
    def base(k):
        im = dawn(); dust(im, k * 1.7); d = ImageDraw.Draw(im, 'RGBA'); kicker(d, 240, f'THE MONTH AHEAD · {month.upper()}')
        for j in range(3):
            x = W // 2 - 50 + j * 50; d.rounded_rectangle([x - 18, 280, x + 18, 288], 4, fill=INK if j == k else (255, 255, 255))
        return im, d
    # 1 teaser
    im, d = base(0); t = S['teaser']
    d.text((W // 2, 360), t['kicker'].upper(), font=sans(36, 700), fill=SOFT, anchor='mm')
    ripples(im, 1.2, W // 2, 820); im.alpha_composite(emoji(STEM_ICON[bm['stem']], 300), (W // 2 - 150, 440)); im.alpha_composite(emoji(EL_ICON[bm['branch_element']], 190), (W // 2 - 95, 760))
    y = 1010
    for l in t['headline']: y = block(d, y, l, serif(76, 600), INK, maxw=W - 160)
    y = block(d, y + 30, t['line'], sans(46, 400), INK, maxw=W - 220)
    d.rounded_rectangle([140, 1560, W - 140, 1670], 55, fill=INK); d.text((W // 2, 1615), t['pointer'], font=sans(40, 600), fill=WHITE, anchor='mm')
    im.convert('RGB').save(f'{folder}/story1.jpg', quality=92)
    # 2 question (reply-to-answer; a native poll can be added by hand)
    im, d = base(1); q = S['question']
    im.alpha_composite(emoji('speech-balloon', 180), (W // 2 - 90, 360))
    y = block(d, 580, q['question'], serif(76, 600), INK, maxw=W - 160)
    y += 40
    for i, o in enumerate(q['options']):
        card(d, [120, y, W - 120, y + 140]); d.ellipse([160, y + 30, 240, y + 110], fill=INK); d.text((200, y + 70), str(i + 1), font=sans(46, 700), fill=WHITE, anchor='mm')
        d.text((280, y + 70), o, font=sans(50, 600), fill=INK, anchor='lm'); y += 165
    block(d, y + 40, q['reply_line'], sans(44, 600), GOLD, maxw=W - 220)
    im.convert('RGB').save(f'{folder}/story2.jpg', quality=92)
    # 3 conversion
    im, d = base(2); c = S['conversion']
    y = block(d, 360, c['headline'], serif(76, 600), INK, maxw=W - 160)
    y = int(block(d, y + 20, c['line'], sans(44, 400), SOFT, maxw=W - 200) + 30)
    for j, dmx in enumerate(D['day_masters']):
        col, row = j % 2, j // 2; x0 = 90 + col * 460; y0 = y + row * 128
        card(d, [x0, y0, x0 + 440, y0 + 112]); im.alpha_composite(emoji(STEM_ICON[dmx['day_master']], 70), (x0 + 18, y0 + 21))
        d.text((x0 + 104, y0 + 18), dmx['day_master'], font=sans(32, 700), fill=INK); d.text((x0 + 104, y0 + 60), dmx['month_force'], font=sans(32, 400), fill=SOFT)
    y += 5 * 128 + 30
    d.rounded_rectangle([120, y, W - 120, y + 120], 60, fill=INK); d.text((W // 2, y + 60), c['invitation'], font=serif(52, 600), fill=WHITE, anchor='mm')
    d.text((W // 2, y + 180), c['link_line'], font=sans(40, 600), fill=GOLD, anchor='mm')
    im.convert('RGB').save(f'{folder}/story3.jpg', quality=92)

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[2] == 'stories':
        f = os.path.join(ROOT, 'monthly', sys.argv[1]); stories(json.load(open(f'{f}/data.json')), tidy(json.load(open(f'{f}/content.json'))), f)
    else:
        render(sys.argv[1])
