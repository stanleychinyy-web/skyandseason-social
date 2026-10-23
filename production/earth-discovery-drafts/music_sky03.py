# SKY03 "The First Bloom" — original cue: soft piano, harp, celesta, warm pad, ~70 bpm, bright (F major);
# ambience: morning birds + breeze -> soft sprout pops -> shimmer at the Yi transformation -> sparkles as the garden grows -> evening crickets.
# usage: python3 music_sky03.py <out.wav> <story> <t2> <t3> <t4> <tdusk>
import sys, numpy as np, fluidsynth, wave
from scipy import signal
SR = 48000
OUTW = sys.argv[1]; story, t2, t3, t4, tsun = map(float, sys.argv[2:7]); DUR = story + 4.0
fs = fluidsynth.Synth(samplerate=SR, gain=0.6); sf = fs.sfload('/usr/share/sounds/sf2/TimGM6mb.sf2')
PROG = {0: 49, 1: 0, 2: 46, 5: 8, 7: 89, 8: 73, 6: 11}
for ch, pg in PROG.items(): fs.program_select(ch, sf, 0, pg); fs.cc(ch, 91, 110)
ev = []
def note(ch, n, t0, d, v=70): ev.append((t0, 1, ch, n, v)); ev.append((t0 + d, 0, ch, n, 0))
def chord(ch, ns, t0, d, v=60, sp=0.0):
    for k, n in enumerate(ns): note(ch, n, t0 + k * sp, d - k * sp, v)
b = 60 / 70
# A: rain arrives (F - Dm, gentle piano raindrops) 0..t2
chord(7, [41, 48, 53, 57], 0.0, t2 + 0.5, 42, 0.2)
for k, (t, n) in enumerate([(0.6, 81), (1.3, 84), (2.0, 81), (2.9, 77), (3.6, 79), (4.4, 81), (5.2, 84)]):
    if t < t2: note(1, n, t, 1.0, 50 + (k % 2) * 6)
chord(1, [50, 57, 62], max(0.1, t2 - 2.2), 2.2, 38, 0.1)
for k, n in enumerate([89, 93, 96]): note(5, n, 1.0 + k * b * 1.5, 1.2, 44)
# B: transformation (Bb -> C -> F swell, harp glissando) t2..t3
chord(0, [46, 53, 58, 62, 65], t2, (t3 - t2) * 0.5 + 0.3, 46, 0.1)
chord(0, [48, 55, 60, 64, 67], t2 + (t3 - t2) * 0.5, (t3 - t2) * 0.5 + 0.3, 52, 0.1)
for k, n in enumerate([60, 64, 67, 72, 76, 79, 84, 88, 91]): note(2, n, t2 + 0.8 + k * 0.11, 1.6, 56)
for k, n in enumerate([84, 88, 91, 96]): note(5, n, t3 - 1.2 + k * 0.18, 1.6, 52)
# C: playing in rain -> sun (F - Gm - C - F, flute melody) t3..t4
chord(0, [41, 53, 57, 60, 65], t3, (t4 - t3) * 0.5 + 0.3, 50, 0.08)
chord(0, [43, 55, 58, 62, 67], t3 + (t4 - t3) * 0.5, (t4 - t3) * 0.5 + 0.3, 50, 0.08)
for t, n in [(0.3, 77), (0.9, 79), (1.5, 81), (2.2, 84), (3.1, 81), (3.8, 79), (4.5, 81), (5.3, 77)]:
    if t3 + t < t4: note(8, n, t3 + t, 0.7, 62)
for k, n in enumerate([65, 69, 72, 77, 81, 84]): note(2, n, tsun + k * 0.12, 1.4, 58)
# D: closing (F major, gentle resolve) t4..end + end card
end = story
chord(0, [41, 53, 57, 60, 65, 69], t4, end - t4 + 4.0, 48, 0.1); chord(7, [53, 57, 60, 65], t4, end - t4 + 4.0, 38)
for t, n in [(0.5, 81), (1.5, 79), (2.5, 77), (3.6, 76), (4.6, 77)]:
    if t4 + t < end + 1: note(1, n, t4 + t, 1.6, 50)
note(5, 89, end + 0.7, 2.6, 50); note(5, 96, end + 0.9, 2.4, 42)
ev.sort(key=lambda e: e[0])
N = int(DUR * SR); out = np.zeros((N, 2), np.float32); pos = 0; k = 0; step = SR // 100
while pos < N:
    tc = pos / SR
    while k < len(ev) and ev[k][0] <= tc:
        _, on, ch, n, v = ev[k]; (fs.noteon(ch, n, v) if on else fs.noteoff(ch, n)); k += 1
    m = min(step, N - pos); out[pos:pos + m] = fs.get_samples(m).reshape(-1, 2).astype(np.float32) / 32768.0; pos += m
tt = np.arange(N) / SR; rng = np.random.default_rng(11)
ir_t = np.arange(int(2.2 * SR)) / SR; ir = rng.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 2.2); ir /= np.abs(ir).sum() ** 0.5 * 40
for c in range(2): out[:, c] += signal.fftconvolve(out[:, c], np.roll(ir, 70 * c))[:N] * 0.7
out = np.tanh(out * 1.5) * 0.8
def band(lo, hi, n): return signal.lfilter(*signal.butter(2, [lo / 24000, hi / 24000], 'band'), rng.normal(0, 1, n))
def env(a, b, fade=0.8): return np.clip(np.minimum((tt - a) / fade + 1, (b - tt) / fade + 1), 0, 1)
for t0 in rng.uniform(0.3, tsun, 10):                                           # morning birds
    n = int(0.11 * SR); i = int(t0 * SR)
    if i + n >= N: continue
    f = np.linspace(rng.uniform(3200, 4200), rng.uniform(4500, 5800), n); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.012; c = rng.integers(0, 2); out[i:i + n, c] += s; out[i:i + n, 1 - c] += s * 0.5
for t0 in [t2 * 0.55, t2 * 0.62, t2 * 0.7]:                                      # tiny sprout 'pops'
    n = int(0.08 * SR); i = int(t0 * SR); f0 = rng.uniform(700, 1000)
    pl = np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f0 * 1.8, n)) / SR) * np.exp(-np.arange(n) / SR * 40) * 0.03
    out[i:i + n, 0] += pl; out[i:i + n, 1] += pl * 0.8
for t0 in rng.uniform(t3 + 0.5, t3 + (t4 - t3) * 0.7, 26):                         # sparkles as the garden grows
    n = int(0.25 * SR); i = int(t0 * SR); f0 = rng.uniform(2500, 4200)
    pl = np.sin(2 * np.pi * f0 * np.arange(n) / SR) * np.exp(-np.arange(n) / SR * 14) * rng.uniform(0.006, 0.014)
    c = rng.integers(0, 2); out[i:i + n, c] += pl; out[i:i + n, 1 - c] += pl * 0.5
def whoosh(t0, d, g, lo, hi):
    n = int(d * SR); x = band(lo, hi, n); e = np.sin(np.linspace(0, np.pi, n)) ** 2; i = int(t0 * SR); m = min(n, N - i)
    out[i:i + m, 0] += x[:m] * e[:m] * g; out[i:i + m, 1] += np.roll(x, 200)[:m] * e[:m] * g
whoosh(t2 + 0.6, 3.0, 0.035, 2500, 9000)                                          # shimmer on the change
breeze = band(300, 3000, N) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * tt)); bz = env(0, end + 3, 1.5) * 0.014; out[:, 0] += breeze * bz; out[:, 1] += np.roll(breeze, 500) * bz
for t0 in np.arange(tsun, end + 3.0, 0.45):                                       # evening crickets
    t0 += rng.uniform(0, 0.15); n = int(0.09 * SR); i = int(t0 * SR)
    if i + n >= N: continue
    ch = np.sin(2 * np.pi * 4400 * np.arange(n) / SR) * (np.sin(2 * np.pi * 45 * np.arange(n) / SR) > 0) * np.sin(np.linspace(0, np.pi, n)) * 0.006
    c = rng.integers(0, 2); out[i:i + n, c] += ch; out[i:i + n, 1 - c] += ch * 0.6
out *= (np.minimum(1, tt / 0.5) * np.minimum(1, (DUR - tt) / 1.8))[:, None]
out *= 0.85 / max(1e-6, np.abs(out).max())
with wave.open(OUTW, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print('music ok', DUR)
