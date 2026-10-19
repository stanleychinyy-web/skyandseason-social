# Earth Discovery: 12 reels — production plan (V1, 18 Oct 2026)

Source brief: Stanley, 18 Oct 2026 ("Earth Discovery and Elemental Awakening"). Storyline is fixed: no extra scenes, characters, reunions or episodes. Sky appears only in Sky reels, Season only in Season reels.

## 0. Daily task notes

- The daily production task runs the **guard** (task step 8: restore any overwritten evening entries, mark posted reels) on EVERY run, including days when no reel is due and after all 12 are made. Only skip opening Flow on those days.
- Post slots: Tue / Thu / Sun 19:00 SGT, alternating Sky and Season (dates in earth-discovery.json). The Saturday Daily Reflection batch task must keep any existing `evening` entry with series `earth-discovery`.

## 0a. Stanley's quality rule (19 Oct 2026, after SKY01 V01) — overrides budget and schedule
- **Every shot in the story is a real Veo animation.** No static photos or in-house push-ins on stills (the closing shot K4 is now a 4th Veo clip V4 from K4). Only the end card is made in-house.
- **On-model in every frame:** Sky's hands are deep indigo-violet (never white), ears hang/flow as ribbons (never stand up), she floats clear of ground and water. Put these lines in every video prompt.
- **Quality over speed:** if a clip fails QC, regenerate it (spare credits may be used). Never queue a reel with a failed or missing shot. If the day's budget runs out, carry on the next day and let the post date slip; tell Stanley.
- Per reel now: 4 stills (4) + 4 Veo clips (80) ≈ 84 credits, plus retries.

## 1. Budget and method (most cost-effective, Stanley's standing rule)

Per reel, about 24–27 s:

| Piece | Tool | Credits |
|---|---|---|
| 4 start-frame stills (K1–K4) | Flow, Nano Banana 2.1, image + character refs | 4 |
| 3 video clips × 8 s (V1–V3) from K1–K3 | Flow, Veo 3.1 Fast image-to-video, 720p | 60 |
| Closing shot V4 from K4 (Veo image-to-video, gentle motion) | Flow, Veo 3.1 Fast, 720p | 20 |
| End card V2, 4 s | `endcard2.py` | 0 |
| Music + ambience | FluidSynth GM soundfont + synthesized nature beds | 0 |
| **Planned total** | | **84 + retries** |

- **Daily cap: 80 credits** (one reel plus up to 16 credits of redraws/one retry clip). Failed Flow clips are not charged; retry them.
- If a clip still breaks a rule after one retry, fix it in the edit (trim around it) rather than spend more.
- 12 reels ≈ 770 credits. Stop and tell Stanley if the Flow balance is below 80 before starting a reel.
- Keyframe-first rule (Render Rule Book §2.17–2.19): QC every still before spending video credits.

## 2. Character references (attach on every still)

| Use | Flow attachment |
|---|---|
| Default Sky | Flow character "Sky" (via @ → Characters) + `16_Flow_Character_References/SKY_REF_TURNAROUND_V01.jpg` |
| Default Season | Flow character "Season" + `SEASON_REF_TURNAROUND_V01.jpg` |
| Elemental form | the form's sheet in `16_Flow_Character_References/` (e.g. `SKY_GUI_WATER_REF_SHEET_V01.jpg`) + front master in `09_Sky_Yin_Transformations/` or `10_Season_Yang_Transformations/` |
| Expressions / acting | `SKY_REF_EXPRESSIONS_V01.jpg`, `SKY_REF_GESTURES-ACTING_V01.jpg` (Season equivalents) |

Upload any sheet not yet in Flow as an ingredient image (free). Transformation clips (V2) use a **two-image** setup when Flow allows first+last frame: first frame = default form (K2), last frame = elemental form (K2b, +1 credit). Otherwise the prompt describes the change and the elemental ref is attached.

## 3. Prompt blocks (append to every prompt)

**SKY BLOCK:** "Sky, the approved character from the attached reference, exactly as designed: small indigo-and-violet spirit, white face, chest and belly, white crescent moon on the forehead, long flowing ribbon ears (never horns), mitten-like hands, no legs walking — she always floats. Gentle, thoughtful, curious. Soft high-quality 3D cinematic fantasy animation, rich atmospheric light. Vertical 9:16. No text, no captions, no watermark, no other characters."

**SEASON BLOCK:** "Season, the approved character from the attached reference, exactly as designed: white body with sky-blue tips, golden eight-ray sun on the forehead, two legs, three fingers and a thumb on each hand, three toes on each foot, always upright (never on all fours). Expressive, energetic, adventurous. Soft high-quality 3D cinematic fantasy animation, rich atmospheric light. Vertical 9:16. No text, no captions, no watermark, no other characters."

**FORM LINE (transformation shots):** "transforms smoothly into the attached approved <FORM> elemental form — same face, eyes, proportions and silhouette; only ears, tail, iris and chest crystal change material as on the reference; the moon/sun symbol stays unchanged."

## 4. Standard edit (every reel)

1. Story ≈ 20–23 s: V1 (trim 6–7 s) → V2 (7–8 s, the transformation must play in full) → V3 (6–7 s) → closing K4 move (3 s).
2. Cuts: 6-frame cross-dissolves; 0.4 s fade from black at the start; hook visible inside the first 2 s (start V1 on its most striking frame if needed).
3. End card V2 (4 s) from the last story frame.
4. Render 1080×1920 then 720×1280, CRF 22, H.264 + AAC, under 10 MB.
5. **No words on screen** during the story. No title cards, no episode numbers.
6. Return to default form at the next reel's start (each reel opens in default form; the brief's continuity rule).

## 5. Sound (no dialogue)

- Sky reels: soft piano, harp, celesta, warm pad; slow (68–76 bpm); ambience matched to scene (breeze, rain, crickets, birds at dawn, crystal chimes).
- Season reels: brighter strings, pizzicato, flute, light percussion; 96–112 bpm; ambience (wind rush, ocean, forest, mountain wind, cave resonance).
- A soft shimmer/whoosh on each transformation; music swells at the transformation and resolves on the closing shot. Never dark or heavy.

## 6. QC checklist (before Stanley sees it)

- Sky floats in every frame; no legs; ears are ribbons, not horns; mitten hands.
- Season: two legs, 3 fingers + thumb, 3 toes, upright; sun symbol gold, 8 rays.
- Face, eyes, colours, moon/sun unchanged through the transformation; form matches the master sheet (not invented).
- Only one character; no text, letters or watermark in any frame; no extra creatures.
- Element reads without words; background continuous within the reel.
- Length 20–30 s; file < 10 MB; end card present.

---

## 7. Reels

Order of production and posting alternates: SKY01, SEA01, SKY02, SEA02 … SEA06.

### SKY01 — A New World (no element)
- **K1 / V1 Arrival + first rest.** Start: high above white clouds at golden morning, Earth's curve below; Sky small in upper third, floating down with a delicate violet light trail. Video: "Sky drifts gently down through the clouds leaving a soft violet trail of cosmic light, looks around with wide curious eyes; the camera follows her down until a green hilltop over a lush valley appears; she settles softly just above the grass, closes her eyes and enjoys the breeze, small flowers swaying." End: Sky hovering over the hilltop, eyes closed, smiling.
- **K2 / V2 Exploring.** Start: wide tracking shot, Sky gliding past rolling hills toward a forest and a sparkling river. Video: "Sky rises and floats across the landscape — hills, forest edge, a sparkling lake; she pauses to admire the view, ears flowing in the breeze; smooth side-tracking camera." End: Sky above a lake, mountains with gathering grey clouds behind.
- **K3 / V3 Something changes.** Start: medium shot, sky cooler, clouds over the mountains. Video: "The breeze turns cool; Sky notices clouds gathering over distant mountains; she lifts a mitten hand and a single tiny raindrop lands on it; she studies it with curiosity; slow push-in to a close-up." End: close-up of Sky looking at the raindrop on her hand.
- **K4 closing:** macro close-up of the raindrop on Sky's mitten, her eyes reflected, soft grey light. In-house slow push.
- Ref: default Sky. Sound: wind high above clouds → birds and meadow breeze → cool wind, first drop "plink".

### SEA01 — A World to Explore (no element)
- **K1 / V1 Arrival + landing.** Start: Earth from space, Season small, streaking toward the atmosphere with a golden trail. Video: "Season flies down through the atmosphere upright with a brilliant golden trail, excited grin; he lands on two feet on a sunlit hilltop above an enormous landscape and stretches both arms wide." End: Season on the hilltop, arms wide.
- **K2 / V2 Exploring.** Start: Season mid-run down the grassy hill. Video: "Season runs playfully down the hill on two legs, leaps into the air and flies fast and upright over forests, hills and a river; energetic, faster than a glide; dynamic tracking camera." End: Season flying toward a bright coastline.
- **K3 / V3 The endless ocean.** Start: Season standing on a coastal cliff edge, huge blue ocean beyond. Video: "Season lands on a coastal cliff; below, an immense blue ocean stretches to the horizon; a large wave rises and breaks against the rocks; Season leans forward, fascinated, eyes shining." End: Season from behind/three-quarter, gazing at the ocean.
- **K4 closing:** wide shot, Season small on the cliff, sun on the sea, about to leap. In-house push toward the sea.
- Ref: default Season. Sound: rushing wind, golden whoosh → skylarks → surf and gulls.

### SKY02 — The Whisper of Rain (Gui Water)
- **K1 / V1 Rain arrives + discovering water.** Start: quiet green valley under soft rain, Sky (default) looking up. Video: "Soft rain begins; Sky looks up, surprised as droplets touch her face; she holds out her mitten hands; several raindrops gather and float above her palms, shimmering; she watches, fascinated." End: floating droplets above her hands.
- **K2 / V2 Gui transformation.** Start: close medium shot, one luminous droplet rising toward her moon symbol. Video: "One luminous droplet touches her crescent moon; silver-blue energy spirals around her; she " + FORM LINE (Gui Water: translucent cyan water ears and tail, gentle mist at the tips, no pink). Last frame (K2b): Sky in Gui Water form, mist around her.
- **K3 / V3 Playing with rain → sun returns.** Start: Sky (Gui Water) mid-valley in rain. Video: "Sky in Gui Water form floats joyfully through the rainfall; droplets dance around her as ribbons and spirals of water; a gentle wave of mist spreads across the valley; the rain stops, sunlight breaks through, she dissolves gently back to default form as droplets fall away and looks down at the wet ground." End: Sky (default) looking down at moist soil.
- **K4 closing:** close-up of a tiny seed on wet soil, Sky's face soft-focus above, sunlight. In-house push.
- Ref: default Sky (V1), Gui Water sheet + master (V2, V3). Sound: soft rain, plinks, harp; shimmer on the change; birds when the sun returns.

### SEA02 — The Mighty Ocean (Ren Water)
- **K1 / V1 The sea + the wave.** Start: Season flying low over a vast rolling ocean. Video: "Season flies upright over powerful waves, looking down with excitement; an enormous wave rises in front of him; he looks surprised, then smiles confidently and reaches toward it." End: Season reaching toward the wall of water.
- **K2 / V2 Ren transformation.** Start: Season touching the wave, deep-blue glow. Video: "The ocean glows deep blue; powerful swirling water surrounds Season; he " + FORM LINE (Ren Water: cresting-wave ears, swirling-wave tail). Last frame: Season in Ren Water form inside a spiral of water.
- **K3 / V3 Riding the ocean → the shore.** Start: Season (Ren Water) surfing a wave crest on two feet. Video: "Season surfs and flies across the waves, water forming sweeping arcs and spiralling currents around him; a wave carries him gently to the shoreline where his water form washes back to his default white body; he looks up." End: Season on the beach looking up.
- **K4 closing:** low angle, Season small at the forest edge looking up at an enormous ancient tree rising above the canopy into the clouds. In-house tilt-up.
- Ref: default Season (V1), Ren Water sheet + master. Sound: big surf, wind, bold strings; water swell on the change.

### SKY03 — The First Bloom (Yi Wood)
- **K1 / V1 The little seed + touch.** Start: Sky (default) low over wet soil, seed in front. Video: "Sky tilts her head at a tiny seed on wet soil; she lowers herself and gently touches it with her mitten; a tiny green shoot emerges; she looks delighted." End: shoot with two leaves, Sky smiling.
- **K2 / V2 Yi transformation.** Start: soft green energy around her hands. Video: "Soft green light grows around her hands; delicate vines and flower petals circle her; she " + FORM LINE (Yi Wood: leaf-ribbon ears with vine curls, leaf-sprout tail). Last frame: Sky in Yi Wood form among circling petals.
- **K3 / V3 The garden awakens → dusk.** Start: Sky (Yi Wood) over a bare patch of ground. Video: "With each gentle gesture, grass grows, vines climb and flowers bloom until the bare patch becomes a colourful garden; she admires it with a soft smile as the sun sets beyond the hills and her leaves fade back to her default form; a faint warm glow appears in the distance." End: dusk garden, tiny orange glow far away.
- **K4 closing:** Sky from behind in the darkening garden, small warm firelight in the distance. In-house push.
- Ref: default Sky, Yi Wood sheet + master. Sound: earth/soil creaks, birds, harp arpeggios; evening crickets at the end.

### SEA03 — The Tree That Reaches the Sky (Jia Wood)
- **K1 / V1 Ancient forest + strength.** Start: Season walking into a forest of tall trees, tilting his head up. Video: "Season walks into an ancient forest, notices one enormous tree rising into the clouds, gasps; he approaches and presses both hands against the trunk; a gentle pulse of green energy rises from the roots." End: Season's hands on the glowing bark.
- **K2 / V2 Jia transformation.** Video: "Powerful green energy spirals upward around Season; bark, living branches and leaves form as he " + FORM LINE (Jia Wood: broad leaf fans, full leafy plume), standing tall and upright. Last frame: Season in Jia Wood form, arms raised.
- **K3 / V3 Reaching higher → above the canopy.** Video: "Season raises his arms; nearby saplings shoot up into strong trees, branches spreading to the light; he admires the forest proudly, then flies upward above the canopy, his leaves settling back to his default form, and sees the brilliant sun above a layer of clouds." End: Season above the canopy, one hand reaching to the sun.
- **K4 closing:** silhouette of Season's reaching hand against the sun over clouds. In-house push.
- Ref: default Season, Jia Wood sheet + master. Sound: creaking wood, leaves rustling, rising strings.

### SKY04 — A Light in the Darkness (Ding Fire)
- **K1 / V1 Dark garden + the flame.** Start: night garden, deep blue shadows, Sky (default) floating cautiously, tiny orange light far off. Video: "Sky floats cautiously through the dark garden; she notices a distant flickering light, follows it and finds a small stone fireplace with a gentle flame; warm orange light falls on her face." End: Sky's face lit warm, close to the flame.
- **K2 / V2 Ding transformation.** Video: "Sky reaches toward the flame; a delicate ribbon of warm light moves from the fire to her; she " + FORM LINE (Ding Fire: slim rising candle-flame ears, soft refined glow — candle, not bonfire). Last frame: Sky in Ding Fire form glowing softly.
- **K3 / V3 Illuminating the garden → dawn.** Video: "Sky floats into the darkness; small glowing lights like candle flames appear around her, lighting flowers, trees and paths; the garden becomes calm and magical; she rises above it and the night fades toward dawn, her glow settling back to her default form." End: Sky above the glowing garden, first light on the horizon.
- **K4 closing:** wide dawn view of a fertile grassland beyond the garden. In-house slow pan.
- Ref: default Sky, Ding Fire sheet + master. Sound: crickets, soft crackle, celesta, warm pad; birds at dawn.

### SEA04 — The Radiant Sun (Bing Fire)
- **K1 / V1 Clouds + the ray.** Start: Season flying above a dim forest, grey clouds blocking the sun. Video: "Dark clouds drift over the forest and everything turns dim and cool; a single golden ray breaks through; Season notices, reaches toward it, and his sun symbol begins to glow." End: Season in the golden ray, symbol glowing.
- **K2 / V2 Bing transformation.** Video: "Golden solar energy swirls around Season; he " + FORM LINE (Bing Fire: radiant red-to-gold flame fans and blazing plume). Last frame: Season in Bing Fire form, radiant.
- **K3 / V3 Bringing sunlight.** Video: "Season rises above the clouds and spreads his arms; a gentle but powerful wave of golden light sweeps across the sky, the clouds part and sunlight floods the forest and valleys; distant mountains appear; he flies toward them as his flames settle back to his default white body." End: Season flying toward a mountain range.
- **K4 closing:** cinematic wide of the sunlit mountain range, Season a small figure flying toward it. In-house push.
- Ref: default Season, Bing Fire sheet + master. Sound: wind, rising brass-like strings, warm whoosh; birds when the light returns.

### SKY05 — The Gentle Earth (Ji Earth)
- **K1 / V1 Grassland + soil.** Start: morning field, soft grass, Sky (default) low. Video: "Sky arrives at a peaceful open field, grass swaying in the morning breeze; she floats close to the ground, lifts a little dark soil in her mitten hands and lets it crumble softly." End: soil falling from her hands.
- **K2 / V2 Ji transformation.** Video: "Warm earthy energy spreads outward; fine particles of soil swirl gracefully around Sky; she " + FORM LINE (Ji Earth: rounded clay-layer ears and tail in warm earth tones). Last frame: Sky in Ji Earth form.
- **K3 / V3 Nurturing the field → the sparkle.** Video: "Sky gently touches the ground; the soil becomes rich; fresh grass, small plants and flowers spread across the field, calm and abundant; her form softens back to default; she notices a tiny sparkle under the soil and brushes the dirt away." End: Sky's mitten beside a half-uncovered gem.
- **K4 closing:** macro of the partly uncovered gemstone glimmering in soil. In-house push.
- Ref: default Sky, Ji Earth sheet + `SKY_JI_EARTH_FRONT_V02.png`. Sound: meadow, soft earth textures, cello and harp.

### SEA05 — The Unshakable Mountain (Wu Earth)
- **K1 / V1 Mountains + the stone.** Start: Season walking a high mountain path, cliffs above clouds. Video: "Season travels through a magnificent mountain range, admiring the huge cliffs; a large boulder blocks the path; he pushes hard but it doesn't move; he pauses and looks at the mountain thoughtfully." End: Season with hands on the boulder, thinking.
- **K2 / V2 Wu transformation.** Video: "Season places both hands on the rock; deep earthy energy glows beneath the surface; he " + FORM LINE (Wu Earth: rock-plate fans and slab plume). Last frame: Season in Wu Earth form, steady.
- **K3 / V3 The mountain responds.** Video: "Season presses forward steadily; the great boulder slowly slides aside — controlled, not destructive; the path opens to a magnificent view; behind where the stone stood is a cave opening with a faint metallic shimmer; his stone settles back to his default form as he looks in." End: Season peering into the glowing cave.
- **K4 closing:** from inside the cave looking out at Season's curious face, silver glints on the walls. In-house push.
- Ref: default Season, Wu Earth sheet + master. Sound: mountain wind, deep stone rumble, low drums kept light.

### SKY06 — The Hidden Jewel (Xin Metal)
- **K1 / V1 Hidden beauty + brilliance.** Start: Sky (default) brushing soil from a gem. Video: "Sky carefully brushes away the dirt and reveals a beautiful crystal; she lifts it gently and turns it; sunlight passes through it, casting delicate reflections and rainbow sparkles on her face; she gazes in wonder." End: Sky holding the gem, rainbow glints.
- **K2 / V2 Xin transformation.** Video: "The gem glows silver-white; fine crystalline light surrounds Sky; she " + FORM LINE (Xin Metal: faceted jewel ribbons, silver-lavender sheen). Last frame: Sky in Xin Metal form holding the crystal.
- **K3 / V3 A world of reflection.** Video: "Sky raises the gem; tiny sparkles spread across the landscape; morning dew, crystals and smooth stones catch the sunlight beautifully; she floats above the sparkling field, smiles gently and holds the crystal close." End: Sky above the field.
- **K4 closing:** beautiful close-up of Sky in Xin Metal form surrounded by delicate sparkling light (series end — she stays in form here; no hint of Season).
- Ref: default Sky (V1), Xin Metal sheet + master. Sound: crystal chimes, celesta, gentle strings resolving.

### SEA06 — The Strength Within Iron (Geng Metal)
- **K1 / V1 Hidden metal + resonance.** Start: Season inside a dim cavern, rough dark iron ore in the rock. Video: "Season enters the cavern and finds a rough piece of iron ore; he examines it, places one hand on it; a metallic resonance ripples through the cave and silver-white sparks rise from the rock." End: sparks around his hand.
- **K2 / V2 Geng transformation.** Video: "Strong silver-grey metallic energy surrounds Season; he " + FORM LINE (Geng Metal: angular metal/crystal fans and shard plume, raw iron texture). Last frame: Season in Geng Metal form.
- **K3 / V3 The power of metal → sunlight.** Video: "Season carefully lifts the iron from the stone; it glows and takes the shape of a softly glowing polished blade — calm, not aggressive; he walks out of the cave onto a mountain ledge in golden sunset light and looks proudly at the world below." End: Season on the ledge.
- **K4 closing:** Season in Geng Metal form standing against the vast sunset mountains (series end — no hint of Sky).
- Ref: default Season (V1), Geng Metal sheet + master. Sound: cave drips, metallic ring, building strings resolving warmly.

## 8. Captions (written at production time, per house rules)

Hook line about the element in everyday words; one paragraph on what that element is like in people (Yin or Yang version); a question or tag prompt; "A Sky & Season short. Explore your free chart at skyandseason.com (link in bio)."; 10 hashtags incl. #skyandseason #innerconstellation, rotated. No episode numbers, no "next episode".
