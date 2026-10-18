"""Validated facts for one "Month Ahead" package.
  python3 tools/monthly/month.py 2026-11  > monthly/2026-11/data.json
The Gregorian month M is previewed on the last day of the month before it. The BaZi (solar) month that
begins inside M starts at its solar term ("jie"), so the two calendars are reported separately.
Sources: month and year pillars from lunar-lite (the calendar engine skyandseason.com uses for every pillar);
exact solar-term times from astronomy-engine (sun's apparent ecliptic longitude), shown in Singapore time.
The engine only resolves two-hour blocks, so the minute comes from the astronomy and is cross-checked."""
import sys, os, json, datetime, subprocess, calendar
import astronomy
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools')); sys.path.insert(0, os.path.join(ROOT, 'tools', 'reels'))
from daytype import daytype, name, STEMS, BRANCH_ANIMAL, BRANCH_EL
from week import GOD, SEASON, FORCE
from reel import relation, GLOSS, LANDSCAPE, STEM_INFO, HOURS
SGT = datetime.timezone(datetime.timedelta(hours=8))
HAN_STEMS = '甲乙丙丁戊己庚辛壬癸'; HAN_BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
# solar term (jie) that opens the BaZi month beginning in each Gregorian month: (pinyin, English, sun longitude)
JIE = {1: ('Xiao Han', 'Minor Cold', 285), 2: ('Li Chun', 'Start of Spring', 315), 3: ('Jing Zhe', 'Awakening of Insects', 345),
       4: ('Qing Ming', 'Clear and Bright', 15), 5: ('Li Xia', 'Start of Summer', 45), 6: ('Mang Zhong', 'Grain in Ear', 75),
       7: ('Xiao Shu', 'Minor Heat', 105), 8: ('Li Qiu', 'Start of Autumn', 135), 9: ('Bai Lu', 'White Dew', 165),
       10: ('Han Lu', 'Cold Dew', 195), 11: ('Li Dong', 'Start of Winter', 225), 12: ('Da Xue', 'Major Snow', 255)}
ZHONG = {1: ('Da Han', 'Major Cold', 300), 2: ('Yu Shui', 'Rain Water', 330), 3: ('Chun Fen', 'Spring Equinox', 0), 4: ('Gu Yu', 'Grain Rain', 30),
         5: ('Xiao Man', 'Grain Buds', 60), 6: ('Xia Zhi', 'Summer Solstice', 90), 7: ('Da Shu', 'Major Heat', 120), 8: ('Chu Shu', 'End of Heat', 150),
         9: ('Qiu Fen', 'Autumn Equinox', 180), 10: ('Shuang Jiang', 'Frost Descent', 210), 11: ('Xiao Xue', 'Minor Snow', 240), 12: ('Dong Zhi', 'Winter Solstice', 270)}
# hidden stems (share %), as on the site's Earthly Branch cards (earth-branches.js)
HIDDEN = {0: [(9, 100)], 1: [(5, 60), (9, 30), (7, 10)], 2: [(0, 60), (2, 30), (4, 10)], 3: [(1, 100)], 4: [(4, 60), (1, 30), (9, 10)],
          5: [(2, 60), (6, 30), (4, 10)], 6: [(3, 70), (5, 30)], 7: [(5, 60), (3, 30), (1, 10)], 8: [(6, 60), (8, 30), (4, 10)],
          9: [(7, 100)], 10: [(4, 60), (7, 30), (3, 10)], 11: [(8, 70), (0, 30)]}
PROD = {'Wood': 'Fire', 'Fire': 'Earth', 'Earth': 'Metal', 'Metal': 'Water', 'Water': 'Wood'}
CTRL = {'Wood': 'Earth', 'Earth': 'Water', 'Water': 'Fire', 'Fire': 'Metal', 'Metal': 'Wood'}
def el_rel(a, b):
    if a == b: return f'{a} and {b} are the same element'
    if PROD[a] == b: return f'{a} feeds {b}'
    if PROD[b] == a: return f'{b} feeds {a}'
    if CTRL[a] == b: return f'{a} keeps {b} in check'
    return f'{b} keeps {a} in check'

def term_time(lon, y, m):
    t = astronomy.SearchSunLongitude(lon, astronomy.Time.Make(y, m, 1, 0, 0, 0), 40)
    return t.Utc().replace(tzinfo=datetime.timezone.utc).astimezone(SGT)

def engine(dates):
    js = ("const {getHeavenlyStemAndEarthlyBranchBySolarDate:g}=require('lunar-lite');const out={};"
          f"for(const d of {json.dumps(dates)}){{out[d]=[];for(let h=0;h<12;h++){{const x=g(d,h);out[d].push([x.yearly.join(''),x.monthly.join('')])}}}}"
          "console.log(JSON.stringify(out))")
    r = subprocess.run(['node', '-e', js], cwd=os.path.join(ROOT, 'tools', 'reels'), capture_output=True, text=True, check=True)
    return json.loads(r.stdout)

def build(ym):
    y, m = map(int, ym.split('-'))
    jie = JIE[m]; start = term_time(jie[2], y, m)
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    nxt = JIE[nm]; end = term_time(nxt[2], ny, nm)
    zh = ZHONG[m]; mid = term_time(zh[2], y, m)
    probe = [(start.date() + datetime.timedelta(d)).isoformat() for d in (-1, 0, 1)]
    eng = engine(probe)
    before, after = eng[probe[0]][6][1], eng[probe[2]][6][1]
    year = eng[probe[2]][6][0]
    s, b = HAN_STEMS.index(after[0]), HAN_BRANCHES.index(after[1])
    blocks = [i for i, (yy, mm) in enumerate(eng[probe[1]]) if mm == after]
    eng_block = blocks[0] if blocks else None
    astro_block = ((start.hour + 1) // 2) % 12
    checks = {
        'month_pillar_changes_around_term': before != after,
        'engine_first_two_hour_block_with_new_month': eng_block,
        'astronomical_two_hour_block': astro_block,
        'note': 'lunar-lite resolves two-hour blocks only; if the blocks differ, trust the astronomical minute and say so.'}
    ys, yb = HAN_STEMS.index(year[0]), HAN_BRANCHES.index(year[1])
    hid = [dict(stem=name(i), god=GOD[i], share=p) for i, p in HIDDEN[b]]
    dms = []
    for dm in range(10):
        t = daytype(dm, s); bt = daytype(dm, HIDDEN[b][0][0])
        dms.append(dict(day_master=name(dm), god=GOD[dm], month_force=FORCE[t], month_force_gloss=GLOSS[FORCE[t]], month_type=t,
                        branch_force=FORCE[bt], branch_force_gloss=GLOSS[FORCE[bt]]))
    animals = [dict(animal=BRANCH_ANIMAL[a], relation=relation(a, b)[0].replace('DAY', 'MONTH'), why=relation(a, b)[1].replace(' day', ' month').replace(' today', ' this month').replace('Today is', 'This is')) for a in range(12)]
    stem_el, br_el = STEMS[s][1], BRANCH_EL[b]
    return dict(
        gregorian_month=datetime.date(y, m, 1).strftime('%B %Y'), post_date=(datetime.date(y, m, 1) - datetime.timedelta(1)).isoformat(),
        bazi_month=dict(pillar=after, stem=name(s), stem_god=GOD[s], stem_nature=STEM_INFO[s][0], stem_good_for=STEM_INFO[s][1], stem_watch=STEM_INFO[s][2],
                        branch=BRANCH_ANIMAL[b], branch_element=br_el, season=SEASON[b], landscape=LANDSCAPE[b], hidden_stems=hid,
                        polarity=STEMS[s][0], stem_vs_branch=el_rel(stem_el, br_el),
                        best_friend=BRANCH_ANIMAL[[1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2][b]], team=[BRANCH_ANIMAL[(b + 4) % 12], BRANCH_ANIMAL[(b + 8) % 12]],
                        clash=BRANCH_ANIMAL[(b + 6) % 12], previous_pillar=before),
        starts=dict(term=f'{jie[0]} ({jie[1]})', sgt=start.strftime('%a %-d %b %Y, %-I:%M %p SGT'), iso=start.isoformat()),
        mid_term=dict(term=f'{zh[0]} ({zh[1]})', sgt=mid.strftime('%a %-d %b %Y, %-I:%M %p SGT')),
        ends=dict(term=f'{nxt[0]} ({nxt[1]})', sgt=end.strftime('%a %-d %b %Y, %-I:%M %p SGT'), iso=end.isoformat()),
        calendars_note=f"The Gregorian month runs 1–{calendar.monthrange(y, m)[1]} {datetime.date(y, m, 1):%B}. The BaZi month {after} runs from {start:%-d %b %-I:%M %p} to {end:%-d %b %-I:%M %p} SGT; the first days of {datetime.date(y, m, 1):%B} still belong to {before}.",
        year=dict(pillar=year, stem=name(ys), branch=BRANCH_ANIMAL[yb], year_stem_vs_month_stem=el_rel(STEMS[ys][1], stem_el),
                  year_branch_vs_month_branch=el_rel(BRANCH_EL[yb], br_el)),
        day_masters=dms, animals=animals, checks=checks)

if __name__ == '__main__':
    print(json.dumps(build(sys.argv[1]), indent=1, ensure_ascii=False))
