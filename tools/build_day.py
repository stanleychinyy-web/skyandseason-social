"""Render one day's reels in format v4 (Stanley 30 Oct 2026: fresh art per card, music only).
python3 tools/build_day.py <date>
Needs tools/days/<date>.json, media/<date>/lines.json (render.py daily) and schedule/<date>.json.
Art (optional, from the "Build reels" workflow): media/<date>/art/*.jpg (morning) and media/<date>/art-evening/*.jpg.
Morning: reel4 sky (Mon-Sat) or season (Sun) -> media/<date>/reel.mp4 + cover.jpg.
Evening: a series slug -> reel4 series, "ranking-<slug>" -> reel4 ranking -> series-reel.mp4 + series-cover.jpg.
Character reels (earth-discovery, trilogy: evening-reel.mp4) are left alone.
9pm story: reel4 clip (evening source on series/ranking days) -> story-clip.mp4.
"""
import json, os, subprocess, sys, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
R4 = os.path.join(ROOT, 'tools', 'reels', 'reel4.py')


def run(*a):
    print('>', ' '.join(a), flush=True); subprocess.run([sys.executable, R4, *a], check=True, cwd=ROOT)


def main(date):
    dt = datetime.date.fromisoformat(date)
    sch = json.load(open(f'{ROOT}/schedule/{date}.json', encoding='utf-8'))
    if not os.path.exists(f'{ROOT}/media/{date}/lines.json'):
        subprocess.run([sys.executable, f'{ROOT}/tools/render.py', 'daily', f'{ROOT}/tools/days/{date}.json'], check=True, cwd=ROOT)
        for k in range(1, 5):
            p = f'{ROOT}/media/{date}/a{k}.jpg'
            if os.path.exists(p): os.remove(p)
    if sch.get('morning'):
        run('season' if dt.weekday() == 6 else 'sky', date)
    ev = sch.get('evening') or {}; ser = ev.get('series', ''); src = 'reel'
    if ev and ev.get('video', '').endswith('series-reel.mp4'):
        if ser.startswith('ranking-'):
            run('ranking', f'tools/rankings/{ser[8:]}.json', date); src = 'ranking'
        elif os.path.exists(f'{ROOT}/tools/series/{ser}.json'):
            run('series', f'tools/series/{ser}.json', date); src = 'series'
    if sch.get('morning'):
        run('clip', date, src)


if __name__ == '__main__':
    for d in sys.argv[1:]: main(d)
