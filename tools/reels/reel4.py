"""Daily Sky reel, format v4 (mock-up 30 Oct 2026): hook first, paintings, big type, motion, optional voice.

python3 tools/reels/reel4.py sky|season <date> | series|ranking <spec.json> <date> | clip <date> [reel|series|ranking]   [--art DIR] [--out PATH]
Defaults: media/<date>/reel.mp4 + cover.jpg, series-reel.mp4 + series-cover.jpg, story-clip.mp4. Art: media/<date>/art (morning), art-evening (evening).
Music only (Stanley 30 Oct: "No one talk"); the old --voice code path is kept but not used.
Needs media/<date>/lines.json (render.py daily) and tools/days/<date>.json.
Voice: Piper (free, open source) with a model in tools/assets/voice/*.onnx (not required).
"""
import json, sys, os, subprocess, tempfile, shutil, datetime, math, wave, glob
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__)); NM = HERE + '/node_modules'
ROOT = os.path.abspath(os.path.join(HERE, '..', '..')); ASSETS = os.path.join(ROOT, 'tools', 'assets')
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'tools'))
from daytype import day, name, STEMS, BRANCH_ANIMAL
from week import GOD

W, H, FPS = 1080, 1920, 30
BEAT = 60 / 112; BAR = 4 * BEAT; CARD = 2 * BAR
GOLD = (255, 214, 120); WHITE = (255, 255, 255); SOFT = (235, 230, 245); INK = (30, 25, 50); CREAMY = (255, 230, 200)
PAINT = ['jia', 'yi', 'bing', 'ding', 'wu', 'ji', 'geng', 'xin', 'ren', 'gui']
PLAIN = {'Friend': 'a friend day', 'Rival': 'a rival day', 'Joy': 'a joy day', 'Speak-up': 'a speaking-up day', 'Insight': 'an insight day',
         'Support': 'a support day', 'Opportunity': 'an opportunity day', 'Steady-money': 'a steady-money day', 'Pressure': 'a pressure day',
         'Recognition': 'a recognition day'}
SHORT = {'Friend': 'friends', 'Rival': 'rivals', 'Joy': 'joy', 'Speak-up': 'speaking up', 'Insight': 'insight', 'Support': 'support',
         'Opportunity': 'opportunity', 'Steady-money': 'steady money', 'Pressure': 'pressure', 'Recognition': 'recognition'}


def F(s, w=700): return ImageFont.truetype(f'{NM}/@fontsource/fredoka/files/fredoka-latin-{w}-normal.woff', s)
def NR(s, w=400, it=True): return ImageFont.truetype(f'{ASSETS}/fonts/newsreader-latin-{w}-{"italic" if it else "normal"}.woff', s)
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def ease_back(t):
    t = max(0.0, min(1.0, t)); c = 1.70158; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


_PAINT = {}
ART_DIR = None   # media/<date>/art with hook.jpg, 01-*.jpg … (fresh generated art); falls back to the stem paintings
def art_path(key, slug):
    if ART_DIR:
        hits = sorted(glob.glob(f'{ART_DIR}/{key}*.jpg')) if key != 'hook' else glob.glob(f'{ART_DIR}/hook.jpg')
        if hits: return hits[0]
    return f'{ASSETS}/art/stems/{slug}.jpg'
def painting(slug, key=None):
    """Full-bleed image, darkened, with a bottom gradient. Oversized so it can drift."""
    path = art_path(key, slug) if key else f'{ASSETS}/art/stems/{slug}.jpg'
    if path in _PAINT: return _PAINT[path]
    im = Image.open(path).convert('RGB')
    r = max(W / im.width, H / im.height) * 1.12
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(0.52)
    _PAINT[path] = im; return im


def frame_bg(slug, p, key=None):
    """p in 0..1 across the card: slow zoom-out drift."""
    src = painting(slug, key); z = 1.0 + 0.06 * (1 - p)
    cw, ch = int(W * z), int(H * z)
    x0 = (src.width - cw) // 2; y0 = int((src.height - ch) * (0.35 + 0.1 * p))
    im = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR).convert('RGBA')
    return Image.alpha_composite(im, _overlay())


_OV = []
def _overlay():
    if not _OV:
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for y in range(700, H, 4): d.rectangle([0, y, W, y + 4], fill=(10, 8, 20, int(205 * (y - 700) / 1220)))
        _OV.append(ov)
    return _OV[0]


def wrap(d, txt, f, maxw):
    out, line = [], ''
    for w in txt.split():
        t = (line + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: line = t
        else:
            if line: out.append(line)
            line = w
    return out + [line]


def pop_text(im, d, x, y, txt, f, fill, t, maxw=W - 140, lead=1.04, per=0.07, start=0.0):
    """Words land one by one (scale pop), `per` seconds apart from `start`."""
    k = 0
    for line in wrap(d, txt, f, maxw):
        cx = x
        for wd in line.split():
            tw = d.textlength(wd + ' ', font=f); lt = t - start - k * per
            if lt > 0:
                s = ease_back(lt / 0.22)
                if abs(s - 1) < 0.02: d.text((cx, y), wd, font=f, fill=fill)
                else:
                    tmp = Image.new('RGBA', (int(tw) + 40, int(f.size * 1.3)), (0, 0, 0, 0)); td = ImageDraw.Draw(tmp)
                    td.text((0, 0), wd, font=f, fill=fill)
                    sw, sh = max(1, int(tmp.width * s)), max(1, int(tmp.height * s))
                    sc = tmp.resize((sw, sh)); im.alpha_composite(sc, (int(cx + (tmp.width - sw) / 2), int(y + (tmp.height - sh) / 2)))
            cx += tw; k += 1
        y += int(f.size * lead)
    return y


def pill(d, x, y, txt, f, bg, fg):
    tw = d.textlength(txt, font=f); d.rounded_rectangle([x, y, x + tw + 88, y + 92], 46, fill=bg)
    d.text((x + 44 + tw / 2, y + 46), txt, font=f, fill=fg, anchor='mm')


def first_sentence(line, limit=60):
    s = line.split('. ')[0].rstrip('.')
    if len(s) > limit:
        cut = s[:limit].rsplit(' ', 1)[0]; s = cut + '…'
    return s + ('' if s.endswith('…') else '.')


VOICE_URL = 'https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-gb-southern_english_female-low.tar.gz'
def voice_model():
    """Free Piper voice (open source). Fetched once from GitHub into tools/assets/voice (git-ignored)."""
    d = f'{ASSETS}/voice'; os.makedirs(d, exist_ok=True)
    found = glob.glob(f'{d}/*.onnx')
    if found: return found[0]
    tgz = f'{d}/voice.tar.gz'
    subprocess.run(['curl', '-sSL', '--max-time', '300', '-o', tgz, VOICE_URL], check=True)
    subprocess.run(['tar', 'xzf', tgz, '-C', d], check=True); os.remove(tgz)
    return glob.glob(f'{d}/*.onnx')[0]


def voice_wav(model, text, path):
    from piper import PiperVoice
    v = voice_wav.cache.get(model) or PiperVoice.load(model); voice_wav.cache[model] = v
    with wave.open(path, 'wb') as w: v.synthesize_wav(text, w)
    with wave.open(path) as w: return w.getnframes() / w.getframerate()
voice_wav.cache = {}


def render_sky(date, voice=False, out_path=None):
    dt = datetime.date.fromisoformat(date); s, b = day(dt)
    spec = json.load(open(f'{ROOT}/tools/days/{date}.json', encoding='utf-8'))
    lines = json.load(open(f'{ROOT}/media/{date}/lines.json', encoding='utf-8'))
    idx = {name(i): i for i in range(10)}
    DRAMA = ['Pressure', 'Speak-up', 'Rival', 'Opportunity', 'Recognition', 'Insight', 'Joy', 'Steady-money', 'Support', 'Friend']
    fl = min(lines, key=lambda l: DRAMA.index(l['type'])); feat = fl['element']
    hook_line = first_sentence(fl['line'])
    HOOK = 1.5 * BAR; CLOSE = 1.5 * BAR; n = len(lines); total = HOOK + n * CARD + CLOSE
    out = os.path.dirname(out_path) if out_path else f'{ROOT}/media/{date}'; os.makedirs(out, exist_ok=True)
    out_path = out_path or f'{out}/reel.mp4'; tmp = tempfile.mkdtemp()
    frames = f'{out}/.frames4'; os.makedirs(frames, exist_ok=True)
    # voice lines (synthesised first so timing is known)
    cues = []
    model = voice_model() if voice else None
    if model:
        cues.append((0.15, voice_wav(model, f"{feat} people. {hook_line}", f'{tmp}/v_hook.wav')))
        for k, l in enumerate(lines):
            cues.append((HOOK + k * CARD + 0.2, voice_wav(model, f"{l['element']}. {PLAIN[l['type']].capitalize()}. {l['line']}", f'{tmp}/v{k}.wav')))
        cues.append((HOOK + n * CARD + 0.2, voice_wav(model, "Your element is the day you were born. Find it free at sky and season dot com.", f'{tmp}/v_close.wav')))
    date_txt = dt.strftime('%a %-d %b').upper()
    for fr in range(int(total * FPS) + 1):
        t = fr / FPS
        if t < HOOK:
            p = t / HOOK; im = frame_bg(PAINT[s], p, 'hook'); d = ImageDraw.Draw(im)
            pill(d, 70, 290, date_txt, F(34, 700), WHITE, INK)
            y = pop_text(im, d, 70, 400, f'{feat} people:', F(132, 700), GOLD, t, per=0.1, start=0.05)
            y = pop_text(im, d, 70, y + 10, hook_line, F(112, 700), WHITE, t, per=0.08, start=0.35)
            if t > 1.3: d.text((70, y + 40), f'{name(s)} day · {GOD[s]}', font=NR(54), fill=CREAMY)
            if t > 1.8:
                d.rounded_rectangle([60, 1540, 700, 1620], 16, fill=(20, 14, 10)); d.text((80, 1562), 'Your element in 3 sec…', font=F(46, 600), fill=GOLD)
        elif t < HOOK + n * CARD:
            k = int((t - HOOK) // CARD); lt = t - HOOK - k * CARD; l = lines[k]; si = idx[l['element']]
            im = frame_bg(PAINT[si], lt / CARD, f'{k + 1:02d}-'); d = ImageDraw.Draw(im)
            d.text((70, 250), f'{k + 1} / {n}', font=F(44, 700), fill=GOLD)
            pop_text(im, d, 70, 320, l['element'].upper(), F(150, 700), WHITE, lt, per=0.12)
            if lt > 0.25: d.text((70, 480), GOD[si], font=NR(60), fill=CREAMY)
            if lt > 0.4: pill(d, 70, 590, f'Today: {SHORT[l["type"]]}', F(44, 700), GOLD, INK)
            parts = l['line'].split('. ', 1); head = parts[0] + ('.' if len(parts) > 1 else '')
            y = pop_text(im, d, 70, 820, head, F(92, 700), WHITE, lt, per=0.09, start=0.55, lead=1.06)
            if len(parts) > 1: pop_text(im, d, 70, y + 30, parts[1], F(70, 500), SOFT, lt, per=0.07, start=0.55 + 0.09 * len(head.split()) + 0.15, lead=1.1)
            d.text((70, 1620), 'Yours is the day you were born · skyandseason.com', font=F(38, 500), fill=(200, 195, 215))
        else:
            lt = t - HOOK - n * CARD; im = frame_bg(PAINT[s], lt / CLOSE, 'hook'); d = ImageDraw.Draw(im)
            y = pop_text(im, d, 70, 520, 'Your element is the day you were born.', F(104, 700), WHITE, lt, per=0.08, lead=1.05)
            if lt > 0.9: y = pop_text(im, d, 70, y + 40, 'Find it free in 60 seconds.', F(72, 500), SOFT, lt, per=0.07, start=0.9)
            if lt > 1.4:
                pill(d, 70, y + 60, 'skyandseason.com', F(52, 700), GOLD, INK)
                d.text((70, y + 200), 'Then comment your element below.', font=F(46, 600), fill=CREAMY)
        d.rectangle([0, H - 16, int(W * t / total), H], fill=GOLD)
        if abs(t - 1.2) < 0.5 / FPS: im.convert('RGB').save(os.path.join(out, 'cover.jpg' if out_path.endswith('/reel.mp4') else 'reel4-cover.jpg'), quality=92)
        im.convert('RGB').save(f'{frames}/{fr:05d}.jpg', quality=90)
    bars = int(math.ceil(total / BAR)); music = f'{tmp}/tune.m4a'
    subprocess.run([sys.executable, f'{HERE}/music.py', music, '2', 'a', str(bars)], check=True)
    if cues:
        inputs = ['-i', music]; fc = f'[1:a]volume=0.33[m];'; names = ['[m]']
        for i, (at, dur) in enumerate(cues):
            inputs += ['-i', f'{tmp}/v_hook.wav' if i == 0 else (f'{tmp}/v_close.wav' if i == len(cues) - 1 else f'{tmp}/v{i - 1}.wav')]
            fc += f'[{i + 2}:a]aresample=48000,volume=1.6,adelay={int(at * 1000)}|{int(at * 1000)}[v{i}];'; names.append(f'[v{i}]')
        fc += ''.join(names) + f'amix=inputs={len(names)}:normalize=0:dropout_transition=0[a]'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{frames}/%05d.jpg', *inputs, '-filter_complex', fc,
                        '-map', '0:v', '-map', '[a]', '-t', f'{total:.3f}', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-r', str(FPS),
                        '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', out_path], check=True)
    else:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{frames}/%05d.jpg', '-i', music, '-map', '0:v', '-map', '1:a',
                        '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000',
                        '-movflags', '+faststart', out_path], check=True)
    shutil.rmtree(tmp); shutil.rmtree(frames); print('sky v4', out_path, round(total, 1), 's', 'voice' if cues else 'no voice')


# ---------- v4 engine shared by season / series / ranking / clip (4 Nov 2026) ----------
EL_SLUG = {'Wood': 'jia', 'Fire': 'bing', 'Earth': 'wu', 'Metal': 'geng', 'Water': 'ren'}
FOOT = 'Yours is the day you were born · skyandseason.com'


def encode(frames_dir, total, out_path, bars_hint=None):
    tmp = tempfile.mkdtemp(); music = f'{tmp}/tune.m4a'
    bars = bars_hint or int(math.ceil(total / BAR))
    subprocess.run([sys.executable, f'{HERE}/music.py', music, '2', 'a', str(bars)], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{frames_dir}/%05d.jpg', '-i', music, '-map', '0:v', '-map', '1:a',
                    '-t', f'{total:.3f}', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000',
                    '-movflags', '+faststart', out_path], check=True)
    shutil.rmtree(tmp); shutil.rmtree(frames_dir)


def run_frames(total, draw, out_dir, cover_path, cover_t=1.2, tag='.frames4'):
    frames = f'{out_dir}/{tag}'; os.makedirs(frames, exist_ok=True)
    for fr in range(int(total * FPS) + 1):
        t = fr / FPS; im = draw(t); d = ImageDraw.Draw(im)
        d.rectangle([0, H - 16, int(W * t / total), H], fill=GOLD)
        if cover_path and abs(t - cover_t) < 0.5 / FPS: im.convert('RGB').save(cover_path, quality=92)
        im.convert('RGB').save(f'{frames}/{fr:05d}.jpg', quality=90)
    return frames


def reading(im, d, y, line, lt, start=0.55, big=92, small=70):
    parts = line.split('. ', 1); head = parts[0] + ('.' if len(parts) > 1 else '')
    y = pop_text(im, d, 70, y, head, F(big, 700), WHITE, lt, per=0.09, start=start, lead=1.06)
    if len(parts) > 1: y = pop_text(im, d, 70, y + 30, parts[1], F(small, 500), SOFT, lt, per=0.07, start=start + 0.09 * len(head.split()) + 0.15, lead=1.1)
    return y


def close_card(im, d, lt, comment):
    y = pop_text(im, d, 70, 520, 'Your element is the day you were born.', F(104, 700), WHITE, lt, per=0.08, lead=1.05)
    if lt > 0.9: y = pop_text(im, d, 70, y + 40, 'Find it free in 60 seconds.', F(72, 500), SOFT, lt, per=0.07, start=0.9)
    if lt > 1.4:
        pill(d, 70, y + 60, 'skyandseason.com', F(52, 700), GOLD, INK)
        d.text((70, y + 200), comment, font=F(46, 600), fill=CREAMY)


def years(a):
    return ' · '.join(str(y) for y in range(1948 + a, 2021, 12)[-4:])


def render_season(date, out_path=None):
    from reel import relation
    dt = datetime.date.fromisoformat(date); s, b = day(dt)
    spec = json.load(open(f'{ROOT}/tools/days/{date}.json', encoding='utf-8')); tips = spec['animal_tips']
    out = f'{ROOT}/media/{date}'; os.makedirs(out, exist_ok=True); out_path = out_path or f'{out}/reel.mp4'
    A = BRANCH_ANIMAL[b]; clash = (b + 6) % 12
    from week import ANIMAL_EL
    HOOK = 1.5 * BAR; CLOSE = 1.5 * BAR; n = 12; total = HOOK + n * CARD + CLOSE
    date_txt = dt.strftime('%a %-d %b').upper()
    def draw(t):
        if t < HOOK:
            im = frame_bg(PAINT[s], t / HOOK, 'hook'); d = ImageDraw.Draw(im)
            pill(d, 70, 290, f'{date_txt} · {A.upper()} DAY', F(34, 700), WHITE, INK)
            y = pop_text(im, d, 70, 400, f'Born in {"an" if BRANCH_ANIMAL[clash][0] in "AEIOU" else "a"} {BRANCH_ANIMAL[clash]} year?', F(124, 700), GOLD, t, per=0.1, start=0.05)
            y = pop_text(im, d, 70, y + 10, tips[BRANCH_ANIMAL[clash]], F(104, 700), WHITE, t, per=0.08, start=0.45)
            if t > 1.8:
                d.rounded_rectangle([60, 1540, 760, 1620], 16, fill=(20, 14, 10)); d.text((80, 1562), 'All 12 animals, one by one…', font=F(46, 600), fill=GOLD)
            return im
        if t < HOOK + n * CARD:
            k = int((t - HOOK) // CARD); lt = t - HOOK - k * CARD; a = k
            im = frame_bg(EL_SLUG[ANIMAL_EL[a]], lt / CARD, f'{k + 1:02d}'); d = ImageDraw.Draw(im)
            d.text((70, 250), f'{k + 1} / {n}', font=F(44, 700), fill=GOLD)
            pop_text(im, d, 70, 320, BRANCH_ANIMAL[a].upper(), F(150, 700), WHITE, lt, per=0.12)
            if lt > 0.25: d.text((70, 480), f'Born {years(a)}', font=NR(56), fill=CREAMY)
            if lt > 0.4:
                lab = relation(a, b)[0].split(' · ')[0].replace('-', ' ').lower().capitalize()
                pill(d, 70, 590, lab, F(44, 700), GOLD, INK)
            reading(im, d, 820, tips[BRANCH_ANIMAL[a]], lt)
            d.text((70, 1620), 'Born in Jan or early Feb? Use the animal before yours.', font=F(36, 500), fill=(200, 195, 215))
            return im
        lt = t - HOOK - n * CARD; im = frame_bg(PAINT[s], lt / CLOSE, 'hook'); d = ImageDraw.Draw(im)
        close_card(im, d, lt, 'Then comment your animal below.'); return im
    frames = run_frames(total, draw, out, f'{out}/cover.jpg')
    encode(frames, total, out_path); print('season v4', out_path, round(total, 1), 's')


def render_series(spec_path, date, out_path=None):
    sp = json.load(open(spec_path, encoding='utf-8'))
    out = f'{ROOT}/media/{date}'; os.makedirs(out, exist_ok=True); out_path = out_path or f'{out}/series-reel.mp4'
    SC = 1.5 * BAR; HOOK = 1.5 * BAR; CLOSE = 1.5 * BAR; n = 10; total = HOOK + n * SC + CLOSE
    cover = EL_SLUG[sp.get('cover_element', 'Fire')]
    def draw(t):
        if t < HOOK:
            im = frame_bg(cover, t / HOOK, 'hook'); d = ImageDraw.Draw(im); y = 400
            y = pop_text(im, d, 70, y, sp['title'][0], F(96, 700), GOLD, t, per=0.08, start=0.05)
            y = pop_text(im, d, 70, y, ' '.join(sp['title'][1:]), F(132, 700), WHITE, t, per=0.1, start=0.3, lead=1.02)
            if t > 0.9: pop_text(im, d, 70, y + 40, sp['tag_line'], F(60, 500), SOFT, t, per=0.06, start=0.9)
            if t > 1.8:
                d.rounded_rectangle([60, 1540, 640, 1620], 16, fill=(20, 14, 10)); d.text((80, 1562), 'Pause on yours…', font=F(46, 600), fill=GOLD)
            return im
        if t < HOOK + n * SC:
            k = int((t - HOOK) // SC); lt = t - HOOK - k * SC
            im = frame_bg(PAINT[k], lt / SC, f'{k + 1:02d}'); d = ImageDraw.Draw(im)
            d.text((70, 250), f'{k + 1} / {n}', font=F(44, 700), fill=GOLD)
            pop_text(im, d, 70, 320, name(k).upper(), F(150, 700), WHITE, lt, per=0.1)
            if lt > 0.2: d.text((70, 480), GOD[k], font=NR(60), fill=CREAMY)
            pop_text(im, d, 70, 720, sp['items'][name(k)], F(96, 700), WHITE, lt, per=0.07, start=0.35, lead=1.08)
            d.text((70, 1620), FOOT, font=F(38, 500), fill=(200, 195, 215))
            return im
        lt = t - HOOK - n * SC; im = frame_bg(cover, lt / CLOSE, 'hook'); d = ImageDraw.Draw(im)
        y = pop_text(im, d, 70, 480, 'Which one are you?', F(124, 700), GOLD, lt, per=0.08)
        if lt > 0.6: y = pop_text(im, d, 70, y + 30, 'Your element is the day you were born. Find it free in 60 seconds.', F(64, 500), SOFT, lt, per=0.05, start=0.6)
        if lt > 1.4:
            pill(d, 70, y + 60, 'skyandseason.com', F(52, 700), GOLD, INK)
            d.text((70, y + 200), sp.get('comment_line', 'Comment your element below.'), font=F(46, 600), fill=CREAMY)
        return im
    frames = run_frames(total, draw, out, f'{out}/series-cover.jpg', cover_t=1.6, tag='.frames4e')
    encode(frames, total, out_path); print('series v4', out_path, round(total, 1), 's')


def render_ranking(spec_path, date, out_path=None):
    sp = json.load(open(spec_path, encoding='utf-8')); idx = {name(i): i for i in range(10)}
    out = f'{ROOT}/media/{date}'; os.makedirs(out, exist_ok=True); out_path = out_path or f'{out}/series-reel.mp4'
    ranks = sp['rank'][:5]; n = len(ranks); HOOK = 1.5 * BAR; CLOSE = 1.5 * BAR; total = HOOK + n * CARD + CLOSE
    cover = EL_SLUG[sp.get('cover_element', 'Fire')]
    def draw(t):
        if t < HOOK:
            im = frame_bg(cover, t / HOOK, 'hook'); d = ImageDraw.Draw(im)
            y = pop_text(im, d, 70, 400, 'Which element is', F(96, 700), GOLD, t, per=0.08, start=0.05)
            y = pop_text(im, d, 70, y, ' '.join(sp['title']), F(132, 700), WHITE, t, per=0.1, start=0.3, lead=1.02)
            if t > 0.9: pop_text(im, d, 70, y + 40, sp['tag_line'], F(60, 500), SOFT, t, per=0.06, start=0.9)
            if t > 1.8:
                d.rounded_rectangle([60, 1540, 700, 1620], 16, fill=(20, 14, 10)); d.text((80, 1562), 'Counting down to #1', font=F(46, 600), fill=GOLD)
            return im
        if t < HOOK + n * CARD:
            k = int((t - HOOK) // CARD); lt = t - HOOK - k * CARD; ri = n - 1 - k; r = ranks[ri]; si = idx[r['element']]
            im = frame_bg(PAINT[si], lt / CARD, f'{ri + 1:02d}'); d = ImageDraw.Draw(im)
            top = ri == 0
            pop_text(im, d, 70, 220, f'#{ri + 1}', F(170 if top else 130, 700), GOLD, lt, per=0.1)
            pop_text(im, d, 70, 420, r['element'].upper(), F(140, 700), WHITE, lt, per=0.1, start=0.1)
            if lt > 0.3: d.text((70, 575), GOD[si], font=NR(60), fill=CREAMY)
            y = pop_text(im, d, 70, 760, r['line'], F(88, 700), WHITE, lt, per=0.08, start=0.45, lead=1.08)
            if lt > 1.6 and r.get('plus'):
                pill(d, 70, y + 50, 'The upside', F(40, 700), GOLD, INK)
                pop_text(im, d, 70, y + 170, r['plus'], F(66, 500), SOFT, lt, per=0.06, start=1.7, lead=1.1)
            d.text((70, 1620), FOOT, font=F(38, 500), fill=(200, 195, 215))
            return im
        lt = t - HOOK - n * CARD; im = frame_bg(cover, lt / CLOSE, 'hook'); d = ImageDraw.Draw(im)
        y = pop_text(im, d, 70, 460, 'Agree?', F(150, 700), GOLD, lt, per=0.08)
        y = pop_text(im, d, 70, y + 10, sp.get('comment_line', 'Tag your #1 below.'), F(88, 700), WHITE, lt, per=0.08, start=0.4)
        if lt > 1.0: y = pop_text(im, d, 70, y + 40, 'Your element is the day you were born. Find it free in 60 seconds.', F(60, 500), SOFT, lt, per=0.05, start=1.0)
        if lt > 1.6: pill(d, 70, y + 60, 'skyandseason.com', F(52, 700), GOLD, INK)
        return im
    frames = run_frames(total, draw, out, f'{out}/series-cover.jpg', cover_t=1.6, tag='.frames4e')
    encode(frames, total, out_path); print('ranking v4', out_path, round(total, 1), 's')


def render_clip(date, source='reel'):
    """9pm video story: the hook + first cards of today's reel (or tonight's evening reel), then a 3.5 s end card. No emoji."""
    global ART_DIR
    dt = datetime.date.fromisoformat(date); s, b = day(dt); out = f'{ROOT}/media/{date}'
    evening = source in ('series', 'ranking'); src = f'{out}/series-reel.mp4' if evening else f'{out}/reel.mp4'
    HOOK = 1.5 * BAR
    cut = HOOK + (CARD if source == 'ranking' else 3 * 1.5 * BAR if source == 'series' else 2 * CARD)
    if source == 'ranking': head, body = 'Who is #1?', "The full countdown is in tonight's reel on our page."
    elif source == 'series': head, body = 'Which one are you?', "All 10 elements are in tonight's reel on our page."
    elif dt.weekday() == 6: head, body = 'Found your animal?', "All 12 animals are in today's reel on our page."
    else: head, body = 'Did you find yours?', "All 10 elements are in today's reel on our page."
    im = frame_bg(PAINT[s], 0.5, 'hook'); d = ImageDraw.Draw(im)
    pill(d, 70, 380, 'TONIGHT', F(36, 700), GOLD, INK)
    y = pop_text(im, d, 70, 520, head, F(120, 700), WHITE, 99)
    y = pop_text(im, d, 70, y + 30, body, F(64, 500), SOFT, 99)
    pill(d, 70, y + 70, '@theskyandseason', F(52, 700), GOLD, INK)
    d.text((70, y + 220), 'Find your element free at skyandseason.com', font=F(44, 600), fill=CREAMY)
    end = f'{out}/_clip_end.jpg'; im.convert('RGB').save(end, quality=92)
    tail = 3.5; tot = cut + tail
    fc = (f'[0:v]trim=0:{cut:.3f},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p[a];'
          f'[1:v]fps={FPS},format=yuv420p[e];[a][e]concat=n=2:v=1:a=0[v];'
          f'[0:a]atrim=0:{tot:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={tot - 1.2:.3f}:d=1.2[au]')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-loop', '1', '-t', str(tail), '-i', end,
                    '-filter_complex', fc, '-map', '[v]', '-map', '[au]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21',
                    '-r', str(FPS), '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', f'{out}/story-clip.mp4'], check=True)
    os.remove(end); print('clip v4', f'{out}/story-clip.mp4', round(tot, 1), 's', source)


if __name__ == '__main__':
    kind = sys.argv[1]
    pos = [a for a in sys.argv[2:] if not a.startswith('--')]
    if '--art' in sys.argv: ART_DIR = sys.argv[sys.argv.index('--art') + 1]
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    if out in pos: pos.remove(out)
    if ART_DIR in pos: pos.remove(ART_DIR)
    if kind in ('series', 'ranking'):
        spec, date = pos[0], pos[1]
        if not ART_DIR and os.path.isdir(f'{ROOT}/media/{date}/art-evening'): ART_DIR = f'{ROOT}/media/{date}/art-evening'
        (render_series if kind == 'series' else render_ranking)(spec, date, out)
    elif kind == 'clip':
        date = pos[0]
        if not ART_DIR and os.path.isdir(f'{ROOT}/media/{date}/art'): ART_DIR = f'{ROOT}/media/{date}/art'
        render_clip(date, pos[1] if len(pos) > 1 else 'reel')
    else:
        date = pos[0]
        if not ART_DIR and os.path.isdir(f'{ROOT}/media/{date}/art'): ART_DIR = f'{ROOT}/media/{date}/art'
        if kind == 'season': render_season(date, out)
        else: render_sky(date, False, out)
