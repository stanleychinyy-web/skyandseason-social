"""Render Sky & Season posts.
  python3 tools/render.py daily  tools/days/2026-10-17.json   -> media/<date>/a1-a4.jpg + story1.jpg
  python3 tools/render.py series tools/series/<name>.json <date> -> media/<date>/b1-b4.jpg
Run from the repository root."""
import json, os, sys, datetime
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from daytype import day, daytype, name, STEMS, BRANCH_EL, BRANCH_ANIMAL
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets') + '/'
def serif(s, w=500, it=False): return ImageFont.truetype(A + f'fonts/newsreader-latin-{w}-{"italic" if it else "normal"}.woff', s)
def sans(s, w=600): return ImageFont.truetype(A + f'fonts/source-sans-3-latin-{w}-normal.woff', s)
W, H = 1080, 1350
EL = {'Wood': (63, 125, 92), 'Fire': (196, 71, 47), 'Earth': (183, 137, 47), 'Metal': (120, 124, 136), 'Water': (46, 90, 135)}
MARK = Image.open(A + 'brand/logo-mark-256.png').convert('RGBA')
BG1, BG2 = (14, 12, 22), (38, 28, 58)
CREAM, INK = (250, 246, 238), (27, 19, 48)

def wrap(d, t, f, mw):
    o, c = [], ''
    for w in t.split():
        x = (c + ' ' + w).strip()
        if d.textlength(x, font=f) <= mw: c = x
        else: o.append(c); c = w
    o.append(c); return o

def grad(h=H):
    im = Image.new('RGB', (W, h)); d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / h; d.line([(0, y), (W, y)], fill=tuple(int(BG1[i] + (BG2[i] - BG1[i]) * k) for i in range(3)))
    return im

def notif(im, y, nm, el, txt):
    d = ImageDraw.Draw(im, 'RGBA'); x0, x1 = 60, W - 60
    f = sans(34, 400); lines = wrap(d, txt, f, x1 - x0 - 150); h = 110 + len(lines) * 46
    d.rounded_rectangle([x0, y, x1, y + h], 36, fill=(255, 255, 255, 40))
    m = MARK.resize((64, 64)); im.paste(m, (x0 + 30, y + 30), m)
    d.text((x0 + 115, y + 30), "SKY & SEASON", font=sans(24, 700), fill=(230, 226, 240))
    d.text((x1 - 30, y + 30), "now", font=sans(24, 400), fill=(190, 184, 205), anchor='ra')
    d.text((x0 + 115, y + 62), nm, font=sans(32, 700), fill=tuple(min(255, c + 70) for c in EL[el]))
    for i, l in enumerate(lines): d.text((x0 + 115, y + 104 + i * 46), l, font=f, fill=(255, 255, 255))
    return y + h + 24

def save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True); im.convert('RGB').save(path, 'JPEG', quality=90, optimize=True)

def cover(im, cy, date, energy, feat, story=False):
    d = ImageDraw.Draw(im)
    d.text((W // 2, cy), date.strftime('%a %-d %b'), font=sans(44, 600), fill=(220, 214, 235), anchor='mm')
    d.text((W // 2, cy + 140), "6:00", font=sans(200, 400), fill=(255, 255, 255), anchor='mm')
    d.text((W // 2, cy + 340), "Your element got a message.", font=serif(56, 400, True), fill=(255, 255, 255), anchor='mm')
    d.text((W // 2, cy + 410), energy, font=sans(32, 600), fill=(214, 176, 106), anchor='mm')
    y = notif(im, cy + 500, *feat)
    hint = "See today's post for yours" if story else "Swipe to find yours"
    d.text((W // 2, y + 40), hint, font=sans(36, 600), fill=(214, 176, 106), anchor='mm')

def daily(spec_path):
    sp = json.load(open(spec_path, encoding='utf-8'))
    dt = datetime.date.fromisoformat(sp['date']); s, b = day(dt)
    bank = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lines.json'), encoding='utf-8'))
    v = (dt - datetime.date(2026, 10, 17)).days % 4
    lines = []
    for i in range(10):
        t = daytype(i, s)
        txt = sp.get('lines', {}).get(name(i)) or bank[t][v]
        lines.append((name(i), STEMS[i][1], txt))
    energy = f"Today: {name(s)} over {BRANCH_EL[b]}"
    feat = next(l for l in lines if l[0] == sp.get('featured', lines[0][0]))
    out = f"media/{sp['date']}"
    im = grad(); cover(im, 260, dt, energy, feat); save(im, f"{out}/a1.jpg")
    for k, (a, z) in enumerate([(0, 5), (5, 10)]):
        im = grad(); y = 110
        for l in lines[a:z]: y = notif(im, y, *l)
        save(im, f"{out}/a{k + 2}.jpg")
    im = grad(); d = ImageDraw.Draw(im)
    for i, l in enumerate(["Not sure which", "element is yours?"]): d.text((W // 2, 430 + i * 110), l, font=serif(92, 600), fill=(255, 255, 255), anchor='mm')
    for i, l in enumerate(["It's the day you were born,", "not your zodiac animal."]): d.text((W // 2, 680 + i * 56), l, font=sans(40, 400), fill=(210, 204, 225), anchor='mm')
    d.rounded_rectangle([200, 860, 880, 970], 55, fill=(214, 176, 106)); d.text((W // 2, 915), "skyandseason.com · free", font=sans(42, 700), fill=(20, 14, 30), anchor='mm')
    d.text((W // 2, 1080), sp.get('send_line', f"Send this to the {feat[0]} in your life."), font=sans(36, 400), fill=(210, 204, 225), anchor='mm')
    save(im, f"{out}/a4.jpg")
    st = grad(1920); cover(st, 420, dt, energy, feat, story=True)
    m = MARK.resize((90, 90)); st.paste(m, (W // 2 - 45, 200), m)
    save(st, f"{out}/story1.jpg")
    json.dump([{'element': l[0], 'type': daytype(i, s), 'line': l[2]} for i, l in enumerate(lines)],
              open(f"{out}/lines.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('daily', sp['date'], energy)

def series(spec_path, date):
    sp = json.load(open(spec_path, encoding='utf-8')); out = f"media/{date}"
    col = EL[sp.get('cover_element', 'Fire')]
    im = Image.new('RGB', (W, H), col); d = ImageDraw.Draw(im)
    for i, l in enumerate(sp['title']): d.text((70, 320 + i * 130), l, font=serif(118, 700), fill=CREAM)
    d.text((70, 330 + len(sp['title']) * 130 + 60), sp['tag_line'], font=sans(44, 600), fill=(255, 235, 222))
    m = MARK.resize((90, 90)); im.paste(m, (70, 1180), m); d.text((180, 1205), "SKY & SEASON", font=sans(34, 700), fill=CREAM)
    save(im, f"{out}/b1.jpg")
    for k, (a, z) in enumerate([(0, 5), (5, 10)]):
        im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im); y = 80
        for i in range(a, z):
            nm = name(i); c = EL[STEMS[i][1]]
            d.rounded_rectangle([60, y, W - 60, y + 220], 30, fill=c)
            d.text((100, y + 30), nm.upper(), font=sans(30, 700), fill=(255, 255, 255))
            for j, l in enumerate(wrap(d, sp['items'][nm], serif(50, 600), W - 220)): d.text((100, y + 78 + j * 60), l, font=serif(50, 600), fill=(255, 255, 255))
            y += 244
        save(im, f"{out}/b{k + 2}.jpg")
    im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im)
    for i, l in enumerate(["Which one", "are you?"]): d.text((70, 360 + i * 130), l, font=serif(130, 700), fill=INK)
    for i, l in enumerate(["Your element comes from the day you", "were born. Find it free in 60 seconds."]): d.text((70, 680 + i * 58), l, font=sans(42, 400), fill=(90, 84, 112))
    d.rounded_rectangle([70, 860, 700, 970], 55, fill=INK); d.text((385, 915), "skyandseason.com", font=sans(44, 700), fill=CREAM, anchor='mm')
    d.text((70, 1060), sp.get('comment_line', "Then comment your element below."), font=sans(40, 600), fill=col)
    save(im, f"{out}/b4.jpg")
    print('series', date, sp['title'])

if __name__ == '__main__':
    if sys.argv[1] == 'daily': daily(sys.argv[2])
    else: series(sys.argv[2], sys.argv[3])
