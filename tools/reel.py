"""Notification-pop reel (draft format, 16 Oct 2026).
  python3 tools/reel.py <date> [music.mp3]  -> media/<date>/reel.mp4  (needs media/<date>/lines.json from render.py daily)
Run from the repository root. ~9.5 s, 1080x1920, 30 fps."""
import json, os, sys, subprocess, datetime, tempfile, shutil
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import serif, sans, grad, notif, MARK, W
from daytype import day, name, BRANCH_EL
H, FPS = 1920, 30
GOLD = (214, 176, 106)
START, STEP, POP = 0.4, 0.62, 0.28      # first notification, gap between, pop-in time
TOP = 700                                # where the stack starts

def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def tile(nm, el, txt):
    t = Image.new('RGBA', (W, 400), (0, 0, 0, 0))
    h = notif(t, 0, nm, el, txt)
    return t.crop((0, 0, W, h))

def main(date, music=None):
    dt = datetime.date.fromisoformat(date); s, b = day(dt)
    L = json.load(open(f"media/{date}/lines.json", encoding='utf-8'))
    from render import STEMS
    tiles = [tile(l['element'], STEMS[i][1], l['line']) for i, l in enumerate(L)]
    base = grad(H).convert('RGBA'); d = ImageDraw.Draw(base)
    d.text((W // 2, 250), "Your element just", font=serif(78, 400, True), fill=(255, 255, 255), anchor='mm')
    d.text((W // 2, 345), "texted you.", font=serif(78, 400, True), fill=(255, 255, 255), anchor='mm')
    d.text((W // 2, 430), "Pause when you see yours", font=sans(36, 600), fill=GOLD, anchor='mm')
    d.text((W // 2, 530), dt.strftime('%A %-d %B'), font=sans(38, 600), fill=(220, 214, 235), anchor='mm')
    d.text((W // 2, 615), "6:00", font=sans(120, 400), fill=(255, 255, 255), anchor='mm')
    end_t = START + STEP * 10 + 0.9
    total = end_t + 2.2
    tmp = tempfile.mkdtemp()
    for f in range(int(total * FPS)):
        t = f / FPS; im = base.copy()
        shown = [i for i in range(10) if t >= START + i * STEP]
        if shown:
            k = shown[-1]; p = ease((t - (START + k * STEP)) / POP)
            y = TOP - (1 - p) * (tiles[k].height + 24)
            for i in reversed(shown):
                tl = tiles[i]
                if i == k:
                    a = tl.copy(); a.putalpha(a.getchannel('A').point(lambda v: int(v * p)))
                    sy = int(TOP - (1 - p) * 60)
                    im.alpha_composite(a, (0, sy)); y = TOP + p * (tl.height + 24)
                else:
                    if y < H: im.alpha_composite(tl, (0, int(y)))
                    y += tl.height + 24
        if t >= end_t:
            q = ease((t - end_t) / 0.35)
            ov = Image.new('RGBA', (W, H), (14, 12, 22, int(242 * q))); im.alpha_composite(ov)
            if q > 0.05:
                c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); e = ImageDraw.Draw(c)
                e.text((W // 2, 760), "Which one", font=serif(110, 600), fill=(255, 255, 255), anchor='mm')
                e.text((W // 2, 880), "was yours?", font=serif(110, 600), fill=(255, 255, 255), anchor='mm')
                e.text((W // 2, 1010), "Your element is the day you were born,", font=sans(40, 400), fill=(210, 204, 225), anchor='mm')
                e.text((W // 2, 1062), "not your zodiac animal.", font=sans(40, 400), fill=(210, 204, 225), anchor='mm')
                e.rounded_rectangle([190, 1150, 890, 1260], 55, fill=GOLD)
                e.text((W // 2, 1205), "skyandseason.com · free", font=sans(42, 700), fill=(20, 14, 30), anchor='mm')
                e.text((W // 2, 1340), "Comment yours below", font=sans(36, 600), fill=GOLD, anchor='mm')
                m = MARK.resize((80, 80)); c.paste(m, (W // 2 - 40, 560), m)
                c.putalpha(c.getchannel('A').point(lambda v: int(v * q))); im.alpha_composite(c)
        im.convert('RGB').save(f"{tmp}/{f:04d}.jpg", quality=92)
    out = f"media/{date}/reel.mp4"
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%04d.jpg']
    if music: cmd += ['-i', music, '-af', f'volume=0.55,afade=t=in:d=0.6,afade=t=out:st={total-1.2:.2f}:d=1.2', '-shortest', '-c:a', 'aac', '-b:a', '128k']
    cmd += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', '-movflags', '+faststart', out]
    subprocess.run(cmd, check=True); shutil.rmtree(tmp)
    print('reel', out, f'{total:.1f}s')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
