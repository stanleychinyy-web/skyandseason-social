"""Checks for tools/home.py.  python3 tools/test_home.py"""
import os, re, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from home import annual, monthly, resting, home_tip, fs_month, HOME_TIPS, SECTOR, fly
from daytype import day, STEMS

S = {v: k for k, v in SECTOR.items()}   # name -> palace

# flight path
assert fly(1) == {5: 1, 6: 2, 7: 3, 8: 4, 9: 5, 1: 6, 2: 7, 3: 8, 4: 9}
assert fly(9)[6] == 1 and fly(9)[4] == 8

# annual centre stars
assert [annual(y)['centre'] for y in (2024, 2025, 2026, 2027)] == [3, 2, 1, 9]
A26 = annual(2026)
assert A26['animal'] == 'Horse'
assert {SECTOR[p]: s for p, s in A26['stars'].items() if p != 5} == {
    'North-west': 2, 'West': 3, 'North-east': 4, 'South': 5, 'North': 6, 'South-west': 7, 'East': 8, 'South-east': 9}
assert (SECTOR[A26['taiSui']], SECTOR[A26['suiPo']], SECTOR[A26['sanSha']]) == ('South', 'North', 'North')
A27 = annual(2027)
assert A27['animal'] == 'Goat'
assert (SECTOR[A27['taiSui']], SECTOR[A27['suiPo']], SECTOR[A27['sanSha']]) == ('South-west', 'North-east', 'West')
assert A27['stars'][S['North']] == 5 and A27['stars'][S['West']] == 2
# other frames
assert SECTOR[annual(2028)['sanSha']] == 'South'      # Monkey, Water frame
assert SECTOR[annual(2029)['sanSha']] == 'East'       # Rooster, Metal frame
assert SECTOR[annual(2031)['sanSha']] == 'West'       # Pig, Wood frame

# monthly stars 2026 (Horse year, first month centre 8, going down one per month)
assert monthly(2026, 0)['centre'] == 8
assert monthly(2027, 0)['centre'] == 5 and monthly(2028, 0)['centre'] == 2
M = monthly(2026, 7)   # Rooster month 8 Sep - 7 Oct
assert M['animal'] == 'Rooster' and M['centre'] == 1
assert M['stars'][S['South']] == 5 and M['stars'][S['North-west']] == 2
M = monthly(2026, 1)   # Rabbit month
assert M['centre'] == 7 and M['stars'][S['South']] == 2
M = monthly(2026, 4)   # Horse month
assert M['centre'] == 4 and M['stars'][S['North-west']] == 5
M = monthly(2026, 10)  # Rat month 7 Dec - 5 Jan
assert M['animal'] == 'Rat' and M['centre'] == 7 and M['stars'][S['South']] == 2
M = monthly(2026, 8)   # Dog month 8 Oct - 7 Nov
assert M['animal'] == 'Dog' and M['centre'] == 9
assert {SECTOR[p]: s for p, s in M['stars'].items() if p != 5} == {
    'North-west': 1, 'West': 2, 'North-east': 3, 'South': 4, 'North': 5, 'South-west': 6, 'East': 7, 'South-east': 8}

# calendar -> Feng Shui year / month
assert fs_month(datetime.date(2026, 2, 3)) == (2025, 11)
assert fs_month(datetime.date(2026, 2, 4)) == (2026, 0)
assert fs_month(datetime.date(2026, 10, 7)) == (2026, 7)
assert fs_month(datetime.date(2026, 10, 8)) == (2026, 8)
assert fs_month(datetime.date(2027, 1, 5)) == (2026, 10)
assert fs_month(datetime.date(2027, 1, 6)) == (2026, 11)

# resting sides
R = resting('2026-10-22')   # Dog month: annual 5 S, annual 2 NW, monthly 5 N, monthly 2 W, Tai Sui S
assert R['avoid'] == ['South', 'North-west', 'North', 'West'] and R['double'] == []
assert (R['taiSui'], R['suiPo'], R['sanSha']) == ('South', 'North', 'North')
assert R['line'].startswith('Resting sides: South and North-west all year; North and West this month') and len(R['line']) <= 80
R = resting('2026-09-20')   # Rooster month: monthly 5 on annual 5 (S), monthly 2 on annual 2 (NW)
assert R['double'] == ['South', 'North-west'] and R['avoid'][:2] == ['South', 'North-west']
R = resting('2026-12-20')   # Rat month: monthly 2 in S on the annual 5
assert R['double'] == ['South'] and R['avoid'][0] == 'South'
R = resting('2027-02-10')   # Goat year: annual 5 N, annual 2 W, Tai Sui SW
assert R['avoid'][:2] == ['North', 'West'] and R['taiSui'] == 'South-west'
for d in range(0, 800):
    r = resting(datetime.date(2026, 1, 1) + datetime.timedelta(d))
    assert len(r['line']) <= 80 and len(r['short']) <= 70, r   # the Centre can carry a 2 (e.g. 2025), that is fine
    assert r['taiSui'] in r['avoid']

# home tips: bank size, length, words we never use, and no repeat within 30 days for the day's Sky element
BANNED = ('BaZi', 'Day Master', 'pillar', 'card', 'luck', 'wealth', 'money', 'health', 'curse', 'bad energy')
for el, bank in HOME_TIPS.items():
    assert 12 <= len(bank) <= 18, (el, len(bank))          # sizes 12-18 keep the 1/9/10/11/19/20/21/29-day gaps apart
    assert len(set(bank)) == len(bank), el
    for t in bank:
        assert len(t) <= 90, (len(t), t)
        assert not any(re.search(r'\b'+re.escape(w)+r'\b', t, re.I) for w in BANNED), t
        assert all(ord(c) < 0x2000 for c in t), t          # no emoji, no Chinese characters
start = datetime.date(2026, 1, 1)
seen = {}   # (element, tip) -> last date shown
for d in range(0, 1100):
    dt = start + datetime.timedelta(d); s, _ = day(dt); el = STEMS[s][1]
    t = home_tip(dt, el)
    if (el, t) in seen: assert (dt - seen[(el, t)]).days >= 30, (el, t, seen[(el, t)], dt)
    seen[(el, t)] = dt
assert home_tip('2026-10-23', 'Metal') == home_tip(datetime.date(2026, 10, 23), 'Metal')
print('test_home: all checks passed')
