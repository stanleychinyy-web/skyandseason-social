"""Daily Sky reel, format v4 (mock-up 30 Oct 2026): hook first, paintings, big type, motion, optional voice.

python3 tools/reels/reel4.py sky <date> [--voice] [--out media/<date>/reel4.mp4]
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
def painting(slug):
    """Full-bleed painting, darkened, with a bottom gradient. Oversized so it can drift."""
    if slug in _PAINT: return _PAINT[slug]
    im = Image.open(f'{ASSETS}/art/stems/{slug}.jpg').convert('RGB')
    r = max(W / im.width, H / im.height) * 1.12
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(0.52)
    _PAINT[slug] = im; return im


def frame_bg(slug, p):
    """p in 0..1 across the card: slow zoom-out drift."""
    src = painting(slug); z = 1.0 + 0.06 * (1 - p)
    cw, ch = int(W * z), int(H * z)
    x0 = (src.width - cw) // 2; y0 = int((src.height - ch) * (0.35 + 0.1 * p))
    im = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR).convert('RGBA')
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(700, H, 4): d.rectangle([0, y, W, y + 4], fill=(10, 8, 20, int(205 * (y - 700) / 1220)))
    return Image.alpha_composite(im, ov)


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
    feat = spec.get('featured', lines[0]['element']); fl = next(l for l in lines if l['element'] == feat)
    hook_line = first_sentence(fl['line'])
    HOOK = 1.5 * BAR; CLOSE = 1.5 * BAR; n = len(lines); total = HOOK + n * CARD + CLOSE
    out = os.path.dirname(out_path) if out_path else f'{ROOT}/media/{date}'; os.makedirs(out, exist_ok=True)
    out_path = out_path or f'{out}/reel4.mp4'; tmp = tempfile.mkdtemp()
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
            p = t / HOOK; im = frame_bg(PAINT[s], p); d = ImageDraw.Draw(im)
            pill(d, 70, 290, date_txt, F(34, 700), WHITE, INK)
            y = pop_text(im, d, 70, 400, f'{feat} people:', F(132, 700), GOLD, t, per=0.1, start=0.05)
            y = pop_text(im, d, 70, y + 10, hook_line, F(112, 700), WHITE, t, per=0.08, start=0.35)
            if t > 1.3: d.text((70, y + 40), f'{name(s)} day · {GOD[s]}', font=NR(54), fill=CREAMY)
            if t > 1.8:
                d.rounded_rectangle([60, 1540, 700, 1620], 16, fill=(20, 14, 10)); d.text((80, 1562), 'Your element in 3 sec…', font=F(46, 600), fill=GOLD)
        elif t < HOOK + n * CARD:
            k = int((t - HOOK) // CARD); lt = t - HOOK - k * CARD; l = lines[k]; si = idx[l['element']]
            im = frame_bg(PAINT[si], lt / CARD); d = ImageDraw.Draw(im)
            d.text((70, 250), f'{k + 1} / {n}', font=F(44, 700), fill=GOLD)
            pop_text(im, d, 70, 320, l['element'].upper(), F(150, 700), WHITE, lt, per=0.12)
            if lt > 0.25: d.text((70, 480), GOD[si], font=NR(60), fill=CREAMY)
            if lt > 0.4: pill(d, 70, 590, f'Today: {SHORT[l["type"]]}', F(44, 700), GOLD, INK)
            parts = l['line'].split('. ', 1); head = parts[0] + ('.' if len(parts) > 1 else '')
            y = pop_text(im, d, 70, 820, head, F(92, 700), WHITE, lt, per=0.09, start=0.55, lead=1.06)
            if len(parts) > 1: pop_text(im, d, 70, y + 30, parts[1], F(70, 500), SOFT, lt, per=0.07, start=0.55 + 0.09 * len(head.split()) + 0.15, lead=1.1)
            d.text((70, 1620), 'Yours is the day you were born · skyandseason.com', font=F(38, 500), fill=(200, 195, 215))
        else:
            lt = t - HOOK - n * CARD; im = frame_bg(PAINT[s], lt / CLOSE); d = ImageDraw.Draw(im)
            y = pop_text(im, d, 70, 520, 'Your element is the day you were born.', F(104, 700), WHITE, lt, per=0.08, lead=1.05)
            if lt > 0.9: y = pop_text(im, d, 70, y + 40, 'Find it free in 60 seconds.', F(72, 500), SOFT, lt, per=0.07, start=0.9)
            if lt > 1.4:
                pill(d, 70, y + 60, 'skyandseason.com', F(52, 700), GOLD, INK)
                d.text((70, y + 200), 'Then comment your element below.', font=F(46, 600), fill=CREAMY)
        d.rectangle([0, H - 16, int(W * t / total), H], fill=GOLD)
        if abs(t - 1.2) < 0.5 / FPS: im.convert('RGB').save(f'{out}/reel4-cover.jpg', quality=92)
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


if __name__ == '__main__':
    kind, date = sys.argv[1], sys.argv[2]
    voice = '--voice' in sys.argv
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    render_sky(date, voice, out)
