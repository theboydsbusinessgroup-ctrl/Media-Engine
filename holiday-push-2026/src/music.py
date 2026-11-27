"""Original, royalty-free lounge loop (no samples): soft electric-piano chords,
sine bass and a brushed hi-hat at 84 BPM. Writes out/music.wav (30 s)."""
import numpy as np, wave, os

SR, BPM, SECS = 44100, 84, 30
beat = 60 / BPM
n = int(SR * SECS)
t = np.arange(n) / SR
mix = np.zeros(n)


def note(freq, start, dur, amp, harmonics=(1, 0.35, 0.12, 0.05)):
    s, e = int(start * SR), min(n, int((start + dur) * SR))
    if s >= n:
        return
    tt = np.arange(e - s) / SR
    env = (1 - np.exp(-tt * 60)) * np.exp(-tt * 1.6)
    sig = sum(a * np.sin(2 * np.pi * freq * (i + 1) * tt) for i, a in enumerate(harmonics))
    trem = 1 + 0.06 * np.sin(2 * np.pi * 4.5 * tt)
    mix[s:e] += amp * env * sig * trem


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)

# ii-V-I-vi in C, jazz voicings (midi)
prog = [
    ([50, 57, 60, 64, 65], 38),   # Dm9
    ([43, 53, 57, 59, 64], 31),   # G13
    ([48, 55, 59, 62, 64], 36),   # Cmaj9
    ([45, 55, 60, 61, 64], 33),   # A7(b9-ish)
]
bar = 4 * beat
time, i = 0.0, 0
rng = np.random.default_rng(7)
while time < SECS:
    chord, root = prog[i % 4]
    for k, m in enumerate(chord[1:]):
        note(hz(m), time + 0.012 * k, bar * 0.95, 0.06)
        note(hz(m), time + 2.5 * beat + 0.01 * k, beat * 1.4, 0.035)
    note(hz(root), time, beat * 1.8, 0.16, (1, 0.15))
    note(hz(root + 7), time + 2 * beat, beat * 1.6, 0.12, (1, 0.15))
    time += bar
    i += 1

# brushed hat on the off-beats + soft kick on 1 and 3
hat_len = int(0.09 * SR)
for b in np.arange(0, SECS / beat):
    s = int((b + 0.5) * beat * SR)
    if s + hat_len < n:
        noise = rng.standard_normal(hat_len)
        noise = np.diff(np.concatenate([[0], noise]))
        mix[s:s + hat_len] += 0.018 * noise * np.exp(-np.arange(hat_len) / SR * 40)
    if int(b) % 2 == 0:
        k = int(b * beat * SR)
        L = int(0.25 * SR)
        if k + L < n:
            kt = np.arange(L) / SR
            mix[k:k + L] += 0.22 * np.sin(2 * np.pi * (55 + 60 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14)

mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.5
stereo = np.stack([mix, np.roll(mix, 220) * 0.96], axis=1)
pcm = (stereo * 32767).astype(np.int16)
out = os.path.join(os.path.dirname(__file__), "out", "music.wav")
os.makedirs(os.path.dirname(out), exist_ok=True)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(out)
