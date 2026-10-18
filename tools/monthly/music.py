"""Warm, bright bed for the Month Ahead reel: real sampled harp, piano and flute (tonejs-instruments, MIT),
84 bpm, D major, I-V-vi-IV. Usage: python3 tools/monthly/music.py out.m4a <bars> [variant 0-3]
The variant shifts the melody so consecutive months do not sound identical."""
import numpy as np, subprocess, os, sys, functools
SR = 44100; BPM = 84; BEAT = 60 / BPM; BAR = 4 * BEAT
NM = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reels', 'node_modules')
NOTES = ['C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs', 'A', 'As', 'B']

@functools.lru_cache(None)
def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def midi_of(n): return NOTES.index(n[:-1].replace('#', 's')) + 12 * (int(n[-1]) + 1)
@functools.lru_cache(None)
def bank(inst):
    d = f'{NM}/tonejs-instrument-{inst}-mp3'
    return {midi_of(f[:-4]): f'{d}/{f}' for f in os.listdir(d) if f.endswith('.mp3')}
def note(inst, m, dur, release=0.25):
    b = bank(inst); src = min(b, key=lambda k: abs(k - m)); x = load(b[src]); r = 2 ** ((m - src) / 12)
    if r != 1: x = np.interp(np.arange(0, len(x) - 1, r), np.arange(len(x)), x).astype(np.float32)
    n = int(dur * SR); x = x[:n] if len(x) > n else np.pad(x, (0, n - len(x)))
    f = min(int(release * SR), n); x[-f:] *= np.linspace(1, 0, f); return x

def main(dst, bars, variant=0):
    out = np.zeros(int((bars * BAR + 4) * SR), np.float32)
    def put(x, t, g):
        i = int(t * SR); out[i:i + len(x)] += g * x[:len(out) - i]
    CH = {'D': ['D3', 'A3', 'D4', 'F#4', 'A4'], 'A': ['A2', 'E3', 'A3', 'C#4', 'E4'], 'Bm': ['B2', 'F#3', 'B3', 'D4', 'F#4'], 'G': ['G2', 'D3', 'G3', 'B3', 'D4']}
    prog = ['D', 'A', 'Bm', 'G']
    MEL = [['F#5', 'E5', 'D5', 'A5'], ['E5', 'C#5', 'A4', 'E5'], ['D5', 'F#5', 'B5', 'A5'], ['G5', 'F#5', 'D5', 'B4'],
           ['A5', 'F#5', 'E5', 'D5'], ['C#5', 'E5', 'A5', 'G5'], ['F#5', 'D5', 'B4', 'D5'], ['B4', 'D5', 'G5', 'F#5']]
    for bar in range(bars):
        ch = CH[prog[bar % 4]]; t0 = bar * BAR; last = bar == bars - 1
        pat = [0, 1, 2, 3, 4, 3, 2, 1]                     # harp arpeggio in eighths
        for k, idx in enumerate(pat if not last else [0, 1, 2, 3, 4]):
            put(note('harp', midi_of(ch[idx]) + 12 * (idx < 2), BEAT * 2.5), t0 + k * BEAT / 2, 0.20 if k else 0.26)
        put(note('piano', midi_of(ch[0]) - 12, BAR * 1.2, 0.6), t0, 0.30)
        put(note('piano', midi_of(ch[2]), BAR * 1.0, 0.6), t0, 0.12)
        if bar >= 2 and not last and (bar // 4) % 3 != 2:  # flute enters after the hook, rests one phrase in three
            mel = MEL[(bar + variant * 2) % 8]
            for j, n in enumerate(mel):
                put(note('flute', midi_of(n), BEAT * 1.6, 0.4), t0 + j * BEAT, 0.16)
        if last:
            put(note('harp', midi_of('D6'), 3.0, 1.2), t0 + 2 * BEAT, 0.22)
    out /= np.max(np.abs(out)) / 0.85
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af',
                    'aecho=0.8:0.6:60:0.18,afade=t=in:d=0.4,afade=t=out:st=%.2f:d=2.5' % (bars * BAR - 0.5),
                    '-c:a', 'aac', '-b:a', '160k', dst], input=out.tobytes(), check=True)
    print('music', dst, round(bars * BAR, 1), 's')

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 0)
