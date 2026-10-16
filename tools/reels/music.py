"""Usage: python3 music.py out.m4a [transpose semitones] [melody a|b]
Bright 112 bpm tune from real sampled instruments (tonejs-instruments, MIT). 8 bars, C-G-Am-F."""
import numpy as np, subprocess, os, sys, functools
SR = 44100; BPM = 112; BEAT = 60 / BPM; BARS = 8
NM = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_modules')
NOTES = ['C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs', 'A', 'As', 'B']

@functools.lru_cache(None)
def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def midi_of(name):
    n, o = name[:-1], int(name[-1]); return NOTES.index(n) + 12 * (o + 1)

@functools.lru_cache(None)
def bank(inst):
    d = f'{NM}/tonejs-instrument-{inst}-mp3'
    return {midi_of(f[:-4]): f'{d}/{f}' for f in os.listdir(d) if f.endswith('.mp3')}

def note(inst, m, dur):
    b = bank(inst); src = min(b, key=lambda k: abs(k - m)); x = load(b[src])
    r = 2 ** ((m - src) / 12)
    if r != 1: x = np.interp(np.arange(0, len(x) - 1, r), np.arange(len(x)), x).astype(np.float32)
    n = int(dur * SR); x = x[:n] if len(x) > n else np.pad(x, (0, n - len(x)))
    f = min(int(0.08 * SR), n); x[-f:] *= np.linspace(1, 0, f)
    return x

T = int(sys.argv[2]) if len(sys.argv) > 2 else 0
VAR = sys.argv[3] if len(sys.argv) > 3 else 'a'
def M(s):  # 'E5' -> midi, transposed
    return midi_of(s.replace('#', 's')) + T

out = np.zeros(int((BARS * 4 * BEAT + 2.5) * SR), np.float32)
def put(x, t, g):
    i = int(t * SR); out[i:i + len(x)] += g * x[:len(out) - i]

CH = {'C': ['C3', 'G3', 'C4', 'E4', 'G4'], 'G': ['G2', 'D3', 'G3', 'B3', 'D4'], 'Am': ['A2', 'E3', 'A3', 'C4', 'E4'], 'F': ['F2', 'C3', 'F3', 'A3', 'C4']}
PROG = ['C', 'G', 'Am', 'F', 'C', 'G', 'F', 'C']
STRUM = [(0, 1, 1.0), (1, 1, .7), (1.5, -1, .55), (2.5, -1, .6), (3, 1, .75), (3.5, -1, .5)]
for bar, ch in enumerate(PROG):
    t0 = bar * 4 * BEAT
    last = bar == BARS - 1
    pattern = [(0, 1, 1.0)] if last else STRUM
    for beat, dirn, g in pattern:
        ns = CH[ch] if dirn > 0 else CH[ch][2:][::-1]
        for k, n in enumerate(ns):
            put(note('guitar-acoustic', M(n), 3.0 if last else BEAT * 1.6), t0 + beat * BEAT + k * 0.012, 0.22 * g)
    put(note('piano', M(CH[ch][0]), 4 * BEAT), t0, 0.35)
# xylophone melody: (beat offset in bar, note)
MEL = [
    [(0, 'E6'), (1, 'G6'), (2, 'E6'), (2.5, 'D6'), (3, 'C6')],
    [(0, 'D6'), (1, 'B5'), (2, 'G5'), (3, 'D6')],
    [(0, 'C6'), (1, 'E6'), (2, 'A6'), (2.5, 'G6'), (3, 'E6')],
    [(0, 'F6'), (1, 'E6'), (2, 'C6'), (3, 'A5')],
    [(0, 'E6'), (1, 'G6'), (2, 'E6'), (2.5, 'D6'), (3, 'C6')],
    [(0, 'D6'), (1, 'G6'), (2, 'B5'), (3, 'D6')],
    [(0, 'C6'), (1, 'F6'), (2, 'A6'), (3, 'G6')],
    [(0, 'C7'), (0.5, 'G6'), (1, 'E6'), (1.5, 'C6')],
]
MEL_B = [
    [(0, 'G5'), (0.5, 'C6'), (1, 'E6'), (2, 'G6'), (3, 'E6')],
    [(0, 'D6'), (1.5, 'B5'), (2, 'D6'), (3, 'G6')],
    [(0, 'A5'), (0.5, 'C6'), (1, 'E6'), (2, 'C6'), (3, 'A5')],
    [(0, 'F6'), (1, 'A6'), (2, 'G6'), (3, 'F6')],
    [(0, 'E6'), (0.5, 'G6'), (1, 'C7'), (2, 'G6'), (3, 'E6')],
    [(0, 'D6'), (1, 'B5'), (2, 'D6'), (2.5, 'E6'), (3, 'G6')],
    [(0, 'F6'), (1, 'C6'), (2, 'A5'), (3, 'C6')],
    [(0, 'E6'), (0.5, 'G6'), (1, 'C7')],
]
if VAR == 'b': MEL = MEL_B
for bar, mel in enumerate(MEL):
    for beat, n in mel:
        put(note('xylophone', M(n), 1.2), bar * 4 * BEAT + beat * BEAT, 0.30)
out /= np.max(np.abs(out)) / 0.89
dst = sys.argv[1] if len(sys.argv) > 1 else 'tune.m4a'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', 'afade=t=out:st=%.2f:d=2' % (BARS * 4 * BEAT + 0.3), '-c:a', 'aac', '-b:a', '160k', dst], input=out.tobytes(), check=True)
print('tune', dst, round(len(out) / SR, 1), 's; bar =', round(4 * BEAT, 3))
