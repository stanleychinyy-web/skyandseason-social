"""Facts for the two weekly reels, for the week starting on <monday>.
  python3 tools/reels/week.py 2026-10-19 > tools/reels/weeks/2026-10-19.json
Sky reel  (Saturday 19:00 before the week): the 10 Day Masters - lucky day and go-easy day, named by the site's ten forces.
Season reel (Sunday 19:00 before the week): the 12 animals - lucky day (harmony) and go-easy day (clash).
Only the 'tip' fields are left empty; the writer fills them (short, cheeky, general)."""
import sys, os, json, datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from daytype import day, daytype, name, STEMS, BRANCH_ANIMAL

ANIMAL_ICON = ['mouse-face', 'cow-face', 'tiger-face', 'rabbit-face', 'dragon-face', 'snake', 'horse-face', 'goat', 'monkey-face', 'rooster', 'dog-face', 'pig-face']
ANIMAL_EL = ['Water', 'Earth', 'Wood', 'Wood', 'Earth', 'Fire', 'Fire', 'Earth', 'Metal', 'Metal', 'Earth', 'Water']
# The site's 12 seasons (branch-stage-map.js): poetic name and months
SEASON = ['The Waiting Seed', 'The Snowmelt', 'The First Shoot', 'The Tender Seedling', 'The Staked Sapling', 'The Reaching Branch',
          'The Full Canopy', 'The Heavy Fruit', 'The Turning Leaf', 'The Bare Tree', 'The Fallen Soil', 'The Bare Ground']
# The site's ten stem gods (heavenly-stems.js) and ten forces (ten-god-map.js)
GOD = ['The Great Tree', 'The Climbing Vine', 'The Sun', 'The Candle Flame', 'The Mountain', 'The Fertile Field', 'The Raw Blade', 'The Jewel', 'The Ocean', 'The Rain and Mist']
SLUG = ['jia', 'yi', 'bing', 'ding', 'wu', 'ji', 'geng', 'xin', 'ren', 'gui']
FORCE = {'Friend': 'The Sovereign', 'Rival': 'The Shadow', 'Joy': 'The Muse', 'Speak-up': 'The Rebel', 'Steady-money': 'The Steward',
         'Opportunity': 'The Visionary', 'Recognition': 'The Guardian', 'Pressure': 'The Crucible', 'Support': 'The Sage', 'Insight': 'The Mystic'}
LUCKY_ORDER = ['Support', 'Joy', 'Steady-money', 'Recognition', 'Opportunity', 'Insight', 'Friend', 'Speak-up']
EASY_ORDER = ['Pressure', 'Rival']
HARMONY = {0: 1, 1: 0, 2: 11, 11: 2, 3: 10, 10: 3, 4: 9, 9: 4, 5: 8, 8: 5, 6: 7, 7: 6}
def trine(b): return {(b + 4) % 12, (b + 8) % 12}
def clash(b): return (b + 6) % 12
def label(d): return d.strftime('%a %-d')

def build(monday):
    days = [monday + datetime.timedelta(i) for i in range(7)]
    info = [(d, *day(d)) for d in days]
    sky = []
    for dm in range(10):
        types = [(d, daytype(dm, s)) for d, s, b in info]
        lucky = next(((d, t) for o in LUCKY_ORDER for d, t in types if t == o), None)
        easy = next(((d, t) for o in EASY_ORDER for d, t in types if t == o), None)
        sky.append(dict(dm=name(dm), element=STEMS[dm][1], god=GOD[dm], art=SLUG[dm],
                        lucky=label(lucky[0]).upper(), lucky_type=lucky[1], lucky_force=FORCE[lucky[1]], lucky_tip='',
                        easy=label(easy[0]) if easy else '', easy_type=easy[1] if easy else '', easy_force=FORCE[easy[1]] if easy else '', easy_tip=''))
    season = []
    for a in range(12):
        lucky = next((d for d, s, b in info if b == HARMONY[a]), None) or next((d for d, s, b in info if b in trine(a)), None) or next((d for d, s, b in info if b == a), None)
        easy = next((d for d, s, b in info if b == clash(a)), None)
        yrs = [y for y in range(1960 + a, 2012, 12)]
        season.append(dict(key=BRANCH_ANIMAL[a].lower(), name=BRANCH_ANIMAL[a], icon=ANIMAL_ICON[a], element=ANIMAL_EL[a], season=SEASON[a],
                           years=' · '.join(map(str, yrs)), lucky=label(lucky).upper() if lucky else '', lucky_tip='',
                           easy=label(easy) if easy else '', easy_tip=''))
    rng = f"{days[0].strftime('%a %-d')} – {days[-1].strftime('%a %-d %b')}"
    return dict(monday=monday.isoformat(), range=rng, sky=sky, season=season,
                days=[dict(date=d.isoformat(), stem=name(s), animal=BRANCH_ANIMAL[b]) for d, s, b in info])

if __name__ == '__main__':
    m = datetime.date.fromisoformat(sys.argv[1]); assert m.weekday() == 0, 'give a Monday'
    print(json.dumps(build(m), indent=1, ensure_ascii=False))
