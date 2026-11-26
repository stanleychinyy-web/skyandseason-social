"""Builds tools/y2027/queue.json: the 2027 Fire Goat series for the 7pm Mon/Wed/Fri/Sat slots, 27 Nov 2026 - 31 Mar 2027.
Facts are computed here (ten forces of Ding against each element; the Goat's relations to the 12 animals) so copy never
guesses. The Saturday batch writes tools/y2027/<slug>.json for each queued topic of its week, in order."""
import json, datetime
D = datetime.date
slots = [d for d in (D(2026, 11, 27) + datetime.timedelta(n) for n in range(130)) if d.weekday() in (0, 2, 4, 5) and d <= D(2027, 3, 31)]
# Ding (Yin Fire) against each Day Master: the force it brings in 2027 (Ten Mirrors names)
FORCE = {'Yang Wood': 'Speak-up', 'Yin Wood': 'Joy', 'Yang Fire': 'Rival', 'Yin Fire': 'Friend', 'Yang Earth': 'Support', 'Yin Earth': 'Insight',
         'Yang Metal': 'Recognition', 'Yin Metal': 'Pressure', 'Yang Water': 'Steady money (+ the Ding-Ren pairing)', 'Yin Water': 'Opportunity'}
# The Goat (Wei) against each animal
REL = {'Goat': 'own year (sits with the Tai Sui)', 'Ox': 'clash (Chou-Wei)', 'Rat': 'harm (Zi-Wei)', 'Dog': 'punishment + break (Xu-Wei)',
       'Horse': 'best partner (Wu-Wei pair)', 'Pig': 'team (Hai-Mao-Wei)', 'Rabbit': 'team (Hai-Mao-Wei)',
       'Tiger': 'steady', 'Dragon': 'steady', 'Snake': 'steady', 'Monkey': 'steady', 'Rooster': 'steady'}
EL_OF = {'Rat': 'Water', 'Ox': 'Earth', 'Tiger': 'Wood', 'Rabbit': 'Wood', 'Dragon': 'Earth', 'Snake': 'Fire', 'Horse': 'Fire', 'Goat': 'Earth',
         'Monkey': 'Metal', 'Rooster': 'Metal', 'Dog': 'Earth', 'Pig': 'Water'}
T = []
def add(series, slug, hook, angle, **kw): T.append(dict(series=series, slug=slug, hook=hook, angle=angle, **kw))
# A. What is 2027 (explainers)
add('explainer', 'what-is-2027', '2027 is a Fire Goat year. Here\'s what that means.', 'Yin Fire (candle) over the Goat (warm summer earth).', spec='what-is-2027.json')
add('explainer', '2027-starts-4-feb', 'Your 2027 doesn\'t start on 1 Jan.', 'Start of spring Thu 4 Feb 2027 09:46 SGT; CNY Sat 6 Feb; Jan/early-Feb births take the year before.', spec='2027-starts-4-feb.json')
add('explainer', 'sun-to-candle', '2026 burned like the sun. 2027 glows like a lamp.', 'Bing Wu -> Ding Wei; Horse-Goat pair: 2027 finishes 2026.', spec='sun-to-candle.json')
add('explainer', 'heavenly-river', 'A fire year with hidden water.', 'The year\'s sound element (nayin) of Bing Wu/Ding Wei is Heavenly River Water: rain from the sky on a fire year. Cooling, timing, emotions.', fig='Yin Water')
add('explainer', 'four-meet-tai-sui', 'Goat, Ox, Rat, Dog: 2027 is your "meet the boss" year.', 'Tai Sui = the year\'s ruler. Goat sits with it, Ox clashes, Rat harm, Dog punishment/break. Not bad luck: a year to move with care. Balanced: what each is good for.', animals=['Goat', 'Ox', 'Rat', 'Dog'])
add('explainer', 'three-words', '2027 in three words.', 'Warm. Focused. Finish. (Candle, Goat, Horse-Goat pair.) Ask viewers for their word.', fig='Yin Fire')
add('myth', 'clash-year-myth', 'Is a clash year a bad year?', 'No: a clash is movement. Good for moves, change, travel; hard on forcing things. Balanced.', animals=['Ox'])
# B. Your animal in 2027 (12 + 2 recaps), most dramatic first
for a in ['Ox', 'Goat', 'Rat', 'Dog', 'Horse', 'Rabbit', 'Pig', 'Tiger', 'Dragon', 'Snake', 'Monkey', 'Rooster']:
    add('animal', f'animal-{a.lower()}', f'Born in a {a} year? Here\'s your 2027.', f'Goat vs {a}: {REL[a]}. Hook, the upside, the catch, one thing to do. Years: born 1948+12k (Jan/early Feb = year before).', animals=[a], el=EL_OF[a])
add('animal', 'animals-go-slow', 'The 4 animals who should take 2027 slowly.', 'Goat, Ox, Rat, Dog — kind framing, each with its upside.', animals=['Goat', 'Ox', 'Rat', 'Dog'])
add('animal', 'animals-easy', 'The 3 animals with the easiest start to 2027.', 'Horse (pair), Rabbit and Pig (team).', animals=['Horse', 'Rabbit', 'Pig'])
# C. Your element in 2027 (Day Master; 10 + recap), around CNY
for e in ['Yin Metal', 'Yang Metal', 'Yin Water', 'Yang Water', 'Yang Wood', 'Yang Fire', 'Yin Wood', 'Yin Fire', 'Yang Earth', 'Yin Earth']:
    add('element', f'element-{e.lower().replace(" ", "-")}', f'Born on a {e} day? 2027 is your {FORCE[e].split(" (")[0].lower()} year.', f'Ding brings {e} the {FORCE[e]} force. Strength + catch + one tip. Explain "the element of the day you were born".', fig=e)
add('element', 'elements-one-word', 'The 10 elements in 2027, one word each.', 'All ten forces in plain words; ends: find yours.', fig='Yin Fire')
# Specials around the turn of the year
add('special', 'before-4-feb', 'Do these 3 things before 4 Feb.', 'Clear one corner, close one loop, write one goal (general, not superstition).', fig='Yang Wood', near='2027-02-03')
add('special', 'goat-new-year', 'Happy Fire Goat year!', 'CNY greeting reel; the 12 animals; find your 2027 mark.', animals=['Goat'], near='2027-02-06')
# D. Day animal (spouse palace) and 2027
add('dayanimal', 'day-animal-intro', 'Your love life in 2027 isn\'t about your year animal.', 'The day animal (the branch of the day you were born) is the partner palace. Find it free on the chart.', fig='Yin Wood')
add('dayanimal', 'day-ox', 'Day animal Ox? 2027 shakes up home and partner.', 'Goat clashes Ox in the partner palace: moves, changes; talk early.', animals=['Ox'])
add('dayanimal', 'day-horse', 'Day animal Horse? 2027 pairs with your partner palace.', 'Wu-Wei pair: good for commitment, meeting people.', animals=['Horse'])
add('dayanimal', 'day-team', 'Day animal Rabbit or Pig? Easy company in 2027.', 'Hai-Mao-Wei team.', animals=['Rabbit', 'Pig'])
add('dayanimal', 'day-friction', 'Day animal Rat or Dog? Small rubs at home in 2027.', 'Zi-Wei harm, Xu-Wei punishment/break: patience, not drama.', animals=['Rat', 'Dog'])
add('dayanimal', 'day-goat', 'Day animal Goat? 2027 holds up a mirror.', 'Own-branch year: self-reflection in relationships.', animals=['Goat'])
# E. Ding Wei and the economy (traditional view, never advice)
add('economy', 'last-ding-wei-1967', 'The last Ding Wei year was 1967.', 'Singapore issued its first own currency notes (12 Jun 1967); ASEAN founded (8 Aug 1967). Building foundations. No predictions.', fig='Yang Earth')
add('economy', 'fire-industries', 'A Fire year: which work does tradition favour?', 'Fire = light, screens, energy, media, beauty, tech. Traditional association only; not financial advice.', fig='Yang Fire')
add('economy', 'earth-industries', 'The Goat is Earth: land, food, home.', 'Earth = property, construction, food, logistics. Traditional view; not advice.', fig='Yang Earth')
add('economy', 'goat-economy', 'The Goat economy: care, craft and comfort.', 'Goat = arts, wellness, caregiving, home. Traditional view.', animals=['Goat'])
add('economy', 'candle-money', 'Money in a candle year: steady beats splashy.', 'Yin Fire = focus; habits over gambles. General habits only, not advice.', fig='Yin Fire')
# F. Ask Sky & Season (sells the Calendar question pills: work, money, love, study, health)
for q, h in [('love', 'Is 2027 a good year to get married?'), ('work', 'Is 2027 a good year to change jobs?'), ('money', 'Is 2027 a good year to start a business?'),
             ('study', 'Is 2027 a good year to study?'), ('health', 'How do I look after myself in a Fire year?'), ('home', 'Is 2027 a good year to move house?')]:
    add('ask', f'ask-{q}', h, f'The general traditional view, then: it depends on your chart. Calendar -> Feb 2027 -> {q} pill shows your mark.', fig='Yin Fire', question=q)
# H. Home in 2027 (from the site's home compass: centre 9; heavy ground N; tired ground W; Tai Sui SW; shadow NE; three cold winds W)
add('home', 'home-heavy-north', '2027: let the north of your home rest.', 'Annual heavy ground (5) in the North: no drilling or reno there; keep calm, tidy.', fig='Yang Earth')
add('home', 'home-west-rest', 'The west side of your home needs quiet in 2027.', 'Tired ground (2) and the three cold winds in the West.', fig='Yin Earth')
add('home', 'home-tai-sui', 'Don\'t face the boss: the Tai Sui sits southwest in 2027.', 'Tai Sui SW, its shadow NE: don\'t start renovation there; sitting with your back to it is fine.', fig='Yang Earth')
# M. 2027 by season (month pillars from the year: Ren Yin Feb ... Gui Chou Jan 2028)
add('months', 'months-feb-apr', '2027, Feb to Apr: the growing months.', 'Ren Yin, Gui Mao, Jia Chen: Wood months feed the year\'s fire. Start things.', fig='Yang Wood')
add('months', 'months-may-jul', '2027, May to Jul: the hottest stretch.', 'Yi Si, Bing Wu, Ding Wei: fire peaks; pace yourself.', fig='Yang Fire')
add('months', 'months-aug-oct', '2027, Aug to Oct: harvest time.', 'Wu Shen, Ji You, Geng Xu: Metal; results and cleanup.', fig='Yang Metal')
add('months', 'months-nov-jan', '2027, Nov to Jan: the cool down.', 'Xin Hai, Ren Zi, Gui Chou: Water; rest; the Ox month clashes the year.', fig='Yang Water')
# P. Element families in 2027 (March): Yang + Yin of one element, work / money / love in one reel
for e, f in [('Wood', 'Yang Wood'), ('Fire', 'Yin Fire'), ('Earth', 'Yang Earth'), ('Metal', 'Yang Metal'), ('Water', 'Yin Water')]:
    add('family', f'family-{e.lower()}', f'{e} people in 2027: work, money, love.', f'Yang {e} and Yin {e} side by side, using their two forces; then the Calendar pills for their own mark.', fig=f, el=e)
add('special', 'q1-check-in', '2027 so far: how is your Fire Goat year going?', 'End-of-March check-in; invite comments; the Calendar shows the months ahead.', fig='Yin Fire')
# order: explainers first, then animals, myth, economy 1, elements around CNY, specials on their dates, then day animals, asks, home, months, economy
order = ['what-is-2027', '2027-starts-4-feb', 'sun-to-candle', 'heavenly-river', 'four-meet-tai-sui', 'three-words',
         'animal-ox', 'animal-goat', 'animal-rat', 'animal-dog', 'last-ding-wei-1967', 'animal-horse', 'animal-rabbit', 'animal-pig', 'clash-year-myth',
         'animal-tiger', 'animal-dragon', 'animal-snake', 'animal-monkey', 'animal-rooster', 'animals-go-slow', 'animals-easy', 'fire-industries',
         'element-yin-metal', 'element-yang-metal', 'element-yin-water', 'element-yang-water', 'element-yang-wood', 'ask-love', 'element-yang-fire',
         'element-yin-wood', 'before-4-feb', 'goat-new-year', 'element-yin-fire', 'element-yang-earth', 'element-yin-earth', 'elements-one-word', 'ask-work',
         'months-feb-apr', 'day-animal-intro', 'day-ox', 'day-horse', 'earth-industries', 'day-team', 'day-friction', 'day-goat', 'ask-money', 'home-heavy-north',
         'home-west-rest', 'home-tai-sui', 'goat-economy', 'ask-study', 'months-may-jul', 'ask-home', 'candle-money', 'ask-health', 'months-aug-oct', 'months-nov-jan', 'family-wood', 'family-fire', 'family-earth', 'family-metal', 'family-water', 'q1-check-in']
by = {t['slug']: t for t in T}; assert set(order) == set(by), set(by) ^ set(order)
q = [by[s] for s in order]
# pin specials to their dates
out = []; it = iter([t for t in q if 'near' not in t]); pins = {t['near']: t for t in q if 'near' in t}
for d in slots:
    ds = d.isoformat()
    t = pins.get(ds) or next(it, None)
    out.append(dict(date=ds, dow=d.strftime('%a'), **(t or {'series': 'flex', 'slug': '', 'hook': 'Open: repeat the best performer or answer comments', 'angle': ''}), used=ds <= '2026-11-30'))
json.dump(out, open('queue.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(slots), 'slots', len(T), 'topics', sum(1 for x in out if x['series'] == 'flex'), 'flex')
for x in out: print(x['date'], x['dow'], x['series'], x['slug'])
