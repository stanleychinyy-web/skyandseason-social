"""Home tips for the daily story: the resting side of the home (annual + monthly flying stars,
Tai Sui, Sui Po, Three Killings) and one plain-words Feng Shui placement tip per element.
Pure Python, no third-party deps.  python3 tools/test_home.py runs the checks.

Sectors sit on the Luo Shu grid, keyed by palace number:
  1 N, 2 SW, 3 E, 4 SE, 5 Centre, 6 NW, 7 W, 8 NE, 9 S.
Forward flight from the centre: centre -> NW -> W -> NE -> S -> N -> SW -> E -> SE, each step +1 (9 wraps to 1).

Boundaries: the Feng Shui year starts at Li Chun (about 4 Feb) and the twelve solar months start on roughly
4 Feb, 6 Mar, 5 Apr, 5 May, 6 Jun, 7 Jul, 7 Aug, 8 Sep, 8 Oct, 7 Nov, 7 Dec and 6 Jan. The real moments shift
by at most a day from year to year (2024-2030); a day's slack is fine for a general home tip, so the fixed
days below are used on purpose."""
import datetime

SECTOR = {1: 'North', 2: 'South-west', 3: 'East', 4: 'South-east', 5: 'Centre',
          6: 'North-west', 7: 'West', 8: 'North-east', 9: 'South'}
FLIGHT = [5, 6, 7, 8, 9, 1, 2, 3, 4]          # palace order of the forward flight, starting at the centre
OPPOSITE = {1: 9, 9: 1, 3: 7, 7: 3, 8: 2, 2: 8, 4: 6, 6: 4}
BRANCHES = ['Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake', 'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Pig']
# Tai Sui (Grand Duke) sits in the sector of the year's animal.
TAI_SUI = {'Rat': 1, 'Ox': 8, 'Tiger': 8, 'Rabbit': 3, 'Dragon': 4, 'Snake': 4,
           'Horse': 9, 'Goat': 2, 'Monkey': 2, 'Rooster': 7, 'Dog': 6, 'Pig': 6}
# Three Killings face the frame opposite the year's element frame.
SAN_SHA = {'Tiger': 1, 'Horse': 1, 'Dog': 1,          # Fire frame  -> North
           'Monkey': 9, 'Rat': 9, 'Dragon': 9,        # Water frame -> South
           'Pig': 7, 'Rabbit': 7, 'Goat': 7,          # Wood frame  -> West
           'Snake': 3, 'Rooster': 3, 'Ox': 3}         # Metal frame -> East
# Centre star of the first (Tiger) month, by the year's animal.
FIRST_MONTH_CENTRE = {'Rat': 8, 'Horse': 8, 'Rabbit': 8, 'Rooster': 8,
                      'Dragon': 5, 'Dog': 5, 'Ox': 5, 'Goat': 5,
                      'Tiger': 2, 'Monkey': 2, 'Snake': 2, 'Pig': 2}
# (month, day) a solar month starts on; index 0 = Tiger month at Li Chun, index 11 = Ox month in the next calendar year.
MONTH_START = [(2, 4), (3, 6), (4, 5), (5, 5), (6, 6), (7, 7), (8, 7), (9, 8), (10, 8), (11, 7), (12, 7), (1, 6)]


def fly(centre):
    """Star in every palace when `centre` sits in the middle and the rest fly forward."""
    return {p: (centre - 1 + i) % 9 + 1 for i, p in enumerate(FLIGHT)}


def year_branch(year): return BRANCHES[(year - 4) % 12]


def annual(year):
    """Feng Shui year `year` (starts about 4 Feb): stars by palace, animal, Tai Sui, Sui Po, Three Killings."""
    centre = 9 - ((year - 2000) % 9) or 9
    animal = year_branch(year)
    return {'year': year, 'animal': animal, 'centre': centre, 'stars': fly(centre),
            'taiSui': TAI_SUI[animal], 'suiPo': OPPOSITE[TAI_SUI[animal]], 'sanSha': SAN_SHA[animal]}


def monthly(year, month_index):
    """Stars by palace for solar month `month_index` (0 = Tiger month at Li Chun ... 11 = Ox month) of Feng Shui year `year`.
    The centre star steps DOWN one per month from the first month's centre."""
    first = FIRST_MONTH_CENTRE[year_branch(year)]
    centre = (first - 1 - month_index) % 9 + 1
    return {'year': year, 'month_index': month_index, 'animal': BRANCHES[(2 + month_index) % 12], 'centre': centre, 'stars': fly(centre)}


def fs_year(date):
    """The Feng Shui year a calendar date belongs to (4 Feb boundary)."""
    return date.year if (date.month, date.day) >= (2, 4) else date.year - 1


def fs_month(date):
    """(Feng Shui year, month index 0-11) for a calendar date."""
    y = fs_year(date)
    idx = 0
    for i, (m, d) in enumerate(MONTH_START):
        start = datetime.date(y + (1 if i == 11 else 0), m, d)
        if date >= start: idx = i
    return y, idx


def _starred(stars, n): return [p for p in FLIGHT if stars[p] == n]


def _join(names):
    names = [('the Centre' if n == 'Centre' else n) for n in names]
    return names[0] if len(names) == 1 else ' and '.join(names[:2])


def resting(date):
    """Where to keep things quiet this month: no drilling, renovation or big furniture moves there,
    and never pick these as 'the side to face for focus'. All sectors are plain words."""
    if isinstance(date, str): date = datetime.date.fromisoformat(date)
    y, mi = fs_month(date); A = annual(y); M = monthly(y, mi)
    a5, a2 = _starred(A['stars'], 5), _starred(A['stars'], 2)
    m5, m2 = _starred(M['stars'], 5), _starred(M['stars'], 2)
    double = [p for p in m5 + m2 if p in a5 + a2]
    order = []
    for p in double + a5 + a2 + m5 + m2 + [A['taiSui']]:
        if p not in order: order.append(p)
    order = [p for p in order if p != 5]  # the centre is not a side of the home
    names = [SECTOR[p] for p in order]
    # Name the year's sides (annual 5, annual 2, Tai Sui) and this month's (monthly 5 / 2) separately,
    # so the line changes with the month instead of repeating the annual pair all year.
    year_side = [p for p in a5 + a2 + [A['taiSui']] if p != 5]
    month_side = [p for p in m5 + m2 if p != 5 and p not in year_side]
    yn = _join([SECTOR[p] for p in dict.fromkeys(year_side)])
    mn = _join([SECTOR[p] for p in dict.fromkeys(month_side)])
    if double:
        head = _join([SECTOR[p] for p in dict.fromkeys(double)])
        line = f'{head}: resting twice over this month. Nothing moves there.'
    elif mn:
        line = f'Resting sides: {yn} all year; {mn} this month. No drilling there.'
        if len(line) > 80: line = f'Resting sides: {yn} all year; {mn} this month.'
        if len(line) > 80: line = f'Resting: {", ".join(SECTOR[p] for p in dict.fromkeys(year_side))} all year; {", ".join(SECTOR[p] for p in dict.fromkeys(month_side))} this month.'
    else:
        line = f'Resting sides this month: {yn}. Hold the drilling and big moves there.'
    head = _join(names)
    side = 'side' if len(names) == 1 else 'sides'
    if len(line) > 80: line = f'Resting sides: {yn} all year; {mn} this month.' if mn and not double else f'Resting {side}: {head}. Hold the drilling there.'
    short = f'Resting {side}: {head}. Hold the drilling there.'
    return {'date': date.isoformat(), 'year': y, 'month_index': mi, 'month_animal': M['animal'],
            'annual': {SECTOR[p]: s for p, s in A['stars'].items()}, 'monthly': {SECTOR[p]: s for p, s in M['stars'].items()},
            'avoid': names, 'double': [SECTOR[p] for p in double],
            'taiSui': SECTOR[A['taiSui']], 'suiPo': SECTOR[A['suiPo']], 'sanSha': SECTOR[A['sanSha']],
            'line': line, 'short': short}


# ---------- AT HOME tips: one small action + the reason or the catch, plain words, <= 90 chars ----------
HOME_TIPS = {
 'Wood': [
  "Open the curtains before the kopi. Morning light is the cheapest fresh start in the flat.",
  "One thriving plant by the window beats five tired ones. Water the one, rehome the rest.",
  "Dead leaves off the plant, old flowers out of the vase. Keep only what is still growing.",
  "Move the plant off the bedside table. Green grows by day; the bedroom is for sleep.",
  "Wipe the dust off the plant leaves. A plant that can breathe makes the room feel alive.",
  "Open a window for ten minutes a day. Moving air wakes the whole flat up.",
  "Bookshelf wobbling? Fix it to the wall. Growth needs a steady frame, same as a sapling.",
  "Give the balcony herbs room to spread. Cramped roots, cramped growth; same for people.",
  "Something tall and green by the main door says welcome. Keep it alive, or skip it.",
  "Do the morning stretch where the sun comes in. East light plus movement sets the day.",
  "Fresh flowers on the dining table this week. Change the water; stale water undoes it.",
  "A wooden bowl or board on the table where you eat. Natural things slow a meal down.",
  "Trim the balcony plants a little each weekend. A pruned plant grows; a wild one sprawls.",
  "Hang the family photos at eye level in a line that climbs. Growth you see every day.",
 ],
 'Fire': [
  "Check the bulb at the main door. A bright entrance means the home is awake before you.",
  "Light the stove at least once this week, even for Milo. A cold kitchen feels empty.",
  "Keep every burner on the stove working. In Feng Shui the stove is the heart of the home.",
  "Stove and sink too close? A chopping board between them helps. Fire and water argue.",
  "One warm lamp in the living room, not just the ceiling light. Soft light pulls people in.",
  "One red cushion on the sofa, just one. A touch of warmth; a whole wall of red is too much.",
  "Dim light in the bedroom, bright light in the kitchen. Each room gets light for its job.",
  "Candles on the dining table, not the bedside. Warm where you gather, calm where you sleep.",
  "Turn the sofa so people face each other, not just the TV. Talk needs a corner, not a row.",
  "Replace the flickering tube light. A light that strobes makes a room jumpy on the quiet.",
  "Hang one bright picture facing the main door. The first thing you see sets the mood.",
  "Clean the hob and cooker hood this weekend. A clean stove makes cooking feel like a treat.",
  "Desk lamp on the side away from your writing hand. No shadow on the page, less squinting.",
  "A warm colour or a sunny print on the south wall. That side likes bright; don't overdo it.",
 ],
 'Earth': [
  "Clear the middle of the flat. The centre joins every room; a pile there blocks them all.",
  "Bed head flat against a solid wall, not a window. Your back wants something to lean on.",
  "No beam straight over the bed. Shift the bed a little, or soften the line with a canopy.",
  "Clear whatever is under the bed. Neat storage there is fine; a jumble there is not.",
  "One ceramic bowl or stone piece on the dining table. Something solid grounds a busy room.",
  "The centre of the flat is the hub; keep it walkable. If the trolley lives there, move it.",
  "Dining table clear by bedtime. A table that only ever holds laundry stops being a table.",
  "Boxes from the last move still stacked? Empty two this week. Stored weight is weight.",
  "Clear the top of the wardrobe. Things looming over your head at night don't help you rest.",
  "Heaviest furniture on the wall farthest from the door. Weight at the back steadies a room.",
  "A rug under the sofa pulls the seating together. Floating furniture feels unsettled.",
  "Heavy things low, light things high. The room feels steadier and nothing lands on you.",
  "One shelf for the everyday clutter, cleared each Sunday. Not minimalism, a landing place.",
  "Fix the wobbly chair or table leg. In a steady home, nothing rocks that is meant to stand.",
 ],
 'Metal': [
  "Soften a sharp corner that points at your bed or sofa. A plant or a folded throw will do.",
  "Knives in the block or a drawer, not on the counter. Sharp things away, calmer kitchen.",
  "No mirror facing the bed. Turn it, cover it at night, or move it inside the wardrobe door.",
  "No mirror straight opposite the main door. It bounces back what comes in; use a side wall.",
  "A mirror on the dining wall is fine, even good. It doubles the food and the faces.",
  "Bin the chipped mug and the cracked bowl. Broken things in daily use nag a little, daily.",
  "Glass coffee table with corners at knee height? A rounded one or a cloth saves your shins.",
  "Clear one drawer completely. Order in one small place spreads; so does the other thing.",
  "Take down the stopped clock. A dead clock on the wall nags; make it tick or let it go.",
  "A small metal chime by the balcony door. A clear little sound wakes up a stale corner.",
  "Sort the paper pile into keep, act, bin. Three piles, one evening, a lighter desk.",
  "A white or grey throw on the chair in the west corner. That side likes cool, clean tones.",
  "Clear out the expired medicine and the old sauces. Expired things take up space you need.",
  "Sharp shelf edge by the doorway? Pad it or shift it. No one wants to dodge a shelf.",
 ],
 'Water': [
  "Clear the entrance: shoes in, bags off the floor. Good things come through a clear door.",
  "Fix the dripping tap this week. Water that leaks all day drains more than the PUB bill.",
  "Bathroom door closed and the lid down. Water stays in the wet room instead of wandering.",
  "Aquarium in the living room, not the bedroom. Moving water is lively; sleep is not.",
  "Oil the main door hinge. A door that sticks or squeaks makes every arrival feel like work.",
  "Window facing the corridor or a T-junction head on? A blind or a sheer softens the glare.",
  "Clear the corridor outside your door of boxes and bikes. The way in should flow, not snag.",
  "Doormat clean, light on, lock smooth. Three small things make the entrance feel open.",
  "Nothing stored behind the main door. A door that opens fully lets the day in fully.",
  "Bed not in a straight line with the bedroom door. Shift it a little; you rest deeper.",
  "Desk with your back to a wall and the door in view. You relax when nobody can sneak up.",
  "Run the tap in the unused bathroom once a week. Still water goes stale; let it move.",
  "A small bowl of water near the entrance, kept clean. Dirty water is worse than no water.",
  "Umbrella dried and put away, not dripping in the hall. A soggy doorway is a soggy start.",
 ],
}
# Per-element offset so that two elements never show the 'same' slot on the same day; the index is taken from
# the date's ordinal (not day-of-year) so the rotation never jumps at New Year. The same element comes back
# 1, 9, 10, 11, 19, 20, 21 and 29 days later; with 12-18 tips none of those gaps lands on the same tip.
TIP_OFFSET = {'Wood': 0, 'Fire': 3, 'Earth': 6, 'Metal': 9, 'Water': 12}


def home_tip(date, element):
    """One general AT HOME tip for the day's element, rotated by the date; no repeat within 30 days."""
    if isinstance(date, str): date = datetime.date.fromisoformat(date)
    bank = HOME_TIPS[element]
    return bank[(date.toordinal() + TIP_OFFSET[element]) % len(bank)]


if __name__ == '__main__':
    import sys
    d = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
    r = resting(d)
    print(r['line']); print('avoid:', ', '.join(r['avoid']), '| double:', r['double'], '| Tai Sui', r['taiSui'], '| Sui Po', r['suiPo'], '| 3 Killings', r['sanSha'])
    for el in HOME_TIPS: print(f'{el:5}', home_tip(d, el))
