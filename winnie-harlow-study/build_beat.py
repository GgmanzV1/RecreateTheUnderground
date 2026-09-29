#!/usr/bin/env python3
"""Glasshouse - an original 140 BPM underground beat, built as a study companion
to Nettspend's "Winnie Harlow".

Every chord, melody and drum pattern in here is original. The sound and mix are built
to targets measured from the reference (see ANALYSIS.md): 140 BPM half-time in
G# minor; a sustaining 808 with set harmonic levels that jumps rather than glides,
mono below 90 Hz; a short dark kick that punches over it; a dry beat-3 clap; short
hats that roll on one pitch; wide, soft-attacked melodic layers in a short room; no
ducking; mastered to -9.2 LUFS with a -1 dBTP ceiling.

Outputs (next to this file):
  midi/loops/*.mid                 one 8-bar loop per part, drag into FL's piano roll
  midi/glasshouse_arrangement.mid  every part laid out over the whole song
  audio/glasshouse_preview.mp3     synthesized preview of the target sound

Usage:
  pip install numpy scipy soundfile mido pyloudnorm
  python3 build_beat.py            # MIDI + preview
  python3 build_beat.py --stems    # also write one audio file per part
  python3 build_beat.py --wav      # also write a 16-bit WAV of the preview
"""
import argparse
from dataclasses import dataclass, replace
from pathlib import Path

import mido
import numpy as np
import soundfile as sf
from scipy import ndimage, signal

HERE = Path(__file__).resolve().parent
BPM = 140
SR = 44100
PPQ = 96                  # FL Studio's default resolution
STEP = 60 / BPM / 4       # seconds per 16th note
LOOP_BARS = 8
RNG = np.random.default_rng(7)


@dataclass
class Note:
    step: float           # start, in 16th notes
    length: float         # in 16th notes
    pitch: int            # MIDI note number, C4 = 60 (FL shows this as C5)
    vel: int
    glide: bool = False   # 808 only: slide into this note from the previous one


# ---------------------------------------------------------------------------
# Composition (all original). Positions are 16th-note steps inside an 8-bar loop.
# ---------------------------------------------------------------------------

# One chord per two bars: i - VI - iv - v in G# minor. (808 root, pad voicing)
CHORDS = [
    (32, [56, 59, 63, 70]),        # G#m(add9)  G#3 B3 D#4 A#4
    (28, [52, 56, 59, 63, 66]),    # Emaj9      E3 G#3 B3 D#4 F#4
    (37, [49, 52, 56, 59, 63]),    # C#m9       C#3 E3 G#3 B3 D#4
    (39, [51, 54, 58, 61]),        # D#m7       D#3 F#3 A#3 C#4
]

# Lead: a 3-3-2 / 3-3-2 syncopated bell motif, re-voiced over each chord. It sits in
# D#4-E5, inside the C3-B5 range where the reference's melodic layer measures.
LEAD_RHYTHM = [(0, 3), (3, 3), (6, 2), (8, 3), (11, 3), (14, 2)]
LEAD_ACCENT = [112, 88, 96, 106, 90, 96]
LEAD_NOTES = [
    ([75, 71, 68, 70, 71, 73], [75, 71, 68, 70, 68, 66]),
    ([75, 71, 68, 66, 68, 71], [75, 71, 68, 66, 64, 63]),
    ([76, 73, 68, 71, 73, 75], [76, 73, 68, 71, 68, 64]),
    ([73, 70, 66, 68, 70, 73], [75, 70, 66, 63, 66, 70]),
]

# 808 per two bars: (step, length, semitones from root). Notes leave short gaps (the
# 808 sounds ~75% of the time) and jump between pitches; only the drop at the very
# end of the loop glides. Kicks land on 808 starts but never on beat 3.
BASS_A = [(0, 5, 0), (7, 3, 0), (11, 4, 0), (16, 3, 0), (19, 5, 0), (26, 2, 0), (28, 3, 12)]
BASS_B = [(0, 5, 0), (7, 3, 0), (11, 4, 0), (16, 6, 0), (26, 4, 0), (30, 2, -7)]
KICK_A = [0, 7, 11, 16, 19]
KICK_B = [0, 7, 11, 16, 26]

DRUM_NOTE = 60            # FL's sampler plays a one-shot at original pitch on C5


def loop_patterns():
    p = {name: [] for name in PARTS}

    for c, (root, voicing) in enumerate(CHORDS):
        base = c * 32
        last = c == len(CHORDS) - 1
        bass, kicks = (BASS_B, KICK_B) if last else (BASS_A, KICK_A)
        for i, (s, ln, off) in enumerate(bass):
            if last and i == len(bass) - 2:
                ln += 1   # overlap the glide note so it slides instead of retriggering
            p["808"].append(Note(base + s, ln, root + off, 118 if s % 16 == 0 else 104,
                                 glide=last and i == len(bass) - 1))
        for s in kicks:
            p["kick"].append(Note(base + s, 1, DRUM_NOTE, 120 if s % 16 == 0 else 104))

        for pitch in voicing:
            p["pad"].append(Note(base, 32, pitch, 80))

        for half, pitches in enumerate(LEAD_NOTES[c]):
            for (s, ln), pitch, vel in zip(LEAD_RHYTHM, pitches, LEAD_ACCENT):
                p["lead"].append(Note(base + half * 16 + s, ln, pitch, vel))

        tones = [n + 12 for n in sorted(voicing)]
        order = tones + tones[-2:0:-1]
        for k in range(32):
            p["arp"].append(Note(base + k, 0.9, order[k % len(order)], 72 if k % 2 == 0 else 54))

    for bar in range(LOOP_BARS):
        b = bar * 16
        p["snare"].append(Note(b + 8, 1, DRUM_NOTE, 116))
        p["clap"].append(Note(b + 8, 1, DRUM_NOTE, 104))

        # 8th-note base with rolls in 5 of 8 bars (the reference rolls in ~64% of bars).
        # Rolls stay on one pitch and swell or fade over a ~20 dB velocity range.
        hats = {s: v for s, v in zip(range(0, 16, 2), [110, 58, 96, 58, 110, 58, 96, 66])}
        rolls = []
        if bar in (1, 5):     # 16th-note triplets across beat 4, swelling in
            hats = {s: v for s, v in hats.items() if s < 12}
            rolls = [(12 + i * 4 / 6, 4 / 6, 60, 24 + 15 * i) for i in range(6)]
        elif bar == 2:        # 32nds on beat 2, fading out
            hats = {s: v for s, v in hats.items() if not 4 <= s < 8}
            rolls = [(4 + i * 0.5, 0.5, 60, 104 - 12 * i) for i in range(8)]
        elif bar == 3:        # 32nds swelling into the next bar
            hats = {s: v for s, v in hats.items() if s < 12}
            rolls = [(12 + i * 0.5, 0.5, 60, 14 + 12 * i) for i in range(8)]
        elif bar == 7:        # 16ths into 32nd triplets to turn the loop around
            hats = {s: v for s, v in hats.items() if s < 8}
            rolls = [(8 + i, 1, 60, 96 if i % 2 == 0 else 50) for i in range(4)]
            rolls += [(12 + i / 3, 1 / 3, 60, 10 + 8 * i) for i in range(12)]
        if bar in (2, 6):     # open hat on the "and" of 2, right before the snare
            hats.pop(6, None)
            p["openhat"].append(Note(b + 6, 2, DRUM_NOTE, 88))
        for s, v in hats.items():
            p["hat"].append(Note(b + s, 1, DRUM_NOTE, v))
        for s, ln, pitch, v in rolls:
            p["hat"].append(Note(b + s, ln * 0.9, pitch, v))

        if bar % 2 == 1:
            for s, pitch in ((3, 60), (13, 62)):
                p["perc"].append(Note(b + s, 1, pitch, 76))

    p["snare"] += [Note(7 * 16 + 14, 1, DRUM_NOTE, 72), Note(7 * 16 + 15, 1, DRUM_NOTE, 90)]
    return p


PARTS = ["kick", "808", "snare", "clap", "hat", "openhat", "perc", "pad", "lead", "arp", "fx"]
DRUMS = {"kick", "808", "snare", "clap", "hat", "openhat", "perc"}

# The reference's beat plays almost from bar 1 and never drops a layer; the vocal makes
# the changes. As an instrumental, Glasshouse keeps that shape but leaves the lead out
# of the verse (room for vocals), stops the 808 for one bar and ends on the melody alone.
SECTIONS = [
    ("Intro", 0, 4, {"pad", "lead"}),
    ("Hook", 4, 20, DRUMS | {"pad", "lead"}),
    ("Verse", 20, 36, DRUMS | {"pad", "arp"}),
    ("Hook", 36, 52, DRUMS | {"pad", "lead", "arp"}),
    ("Outro", 52, 56, {"pad", "lead", "arp"}),
]
SONG_BARS = 56
MUTES = {35: {"kick", "808"}}   # the "808 stop" before the second hook
# One-off hits outside the loops: (part, bar, pitch, length in steps, velocity).
EXTRAS = [("fx", 4, DRUM_NOTE, 4, 100), ("fx", 36, DRUM_NOTE, 4, 100)]


def arrange(loops):
    song = {name: [] for name in PARTS}
    for _, b0, b1, parts in SECTIONS:
        for bar in range(b0, b1):
            lb = (bar - b0) % LOOP_BARS
            for part in parts - MUTES.get(bar, set()):
                for n in loops[part]:
                    if lb * 16 <= n.step < (lb + 1) * 16:
                        song[part].append(replace(n, step=n.step + (bar - lb) * 16))
    for part, bar, pitch, length, vel in EXTRAS:
        song[part].append(Note(bar * 16, length, pitch, vel))
    for part in song:
        song[part].sort(key=lambda n: n.step)
    return song


# ---------------------------------------------------------------------------
# MIDI export
# ---------------------------------------------------------------------------

def midi_track(name, notes):
    events = []
    for n in notes:
        on = round(n.step * PPQ / 4)
        off = max(on + 1, round((n.step + n.length) * PPQ / 4))
        events.append((on, 1, mido.Message("note_on", note=n.pitch, velocity=n.vel)))
        events.append((off, 0, mido.Message("note_off", note=n.pitch, velocity=0)))
    events.sort(key=lambda e: (e[0], e[1]))
    track = mido.MidiTrack([mido.MetaMessage("track_name", name=name)])
    now = 0
    for tick, _, msg in events:
        track.append(msg.copy(time=tick - now))
        now = tick
    track.append(mido.MetaMessage("end_of_track", time=0))
    return track


def write_midi(path, tracks):
    mid = mido.MidiFile(type=1, ticks_per_beat=PPQ)
    mid.tracks.append(mido.MidiTrack([
        mido.MetaMessage("track_name", name="Glasshouse"),
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)),
        mido.MetaMessage("time_signature", numerator=4, denominator=4),
        mido.MetaMessage("end_of_track", time=0),
    ]))
    for name, notes in tracks.items():
        if notes:
            mid.tracks.append(midi_track(name, notes))
    path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(path)


# ---------------------------------------------------------------------------
# Synthesis (only for the preview; in FL you use real samples and synths)
# ---------------------------------------------------------------------------

def hz(pitch):
    return 440.0 * 2 ** ((pitch - 69) / 12)


def filt(x, kind, freq, order=2):
    sos = signal.butter(order, freq, btype=kind, fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def noise(n):
    return RNG.standard_normal(n)


def env_t(n):
    return np.arange(n) / SR


def saw(freq, n):
    dt = freq / SR
    ph = (RNG.random() + dt * np.arange(n)) % 1.0
    y = 2 * ph - 1
    lo = ph < dt
    t = ph[lo] / dt
    y[lo] -= t + t - t * t - 1
    hi = ph > 1 - dt
    t = (ph[hi] - 1) / dt
    y[hi] -= t * t + t + t + 1
    return y


def kick(vel):
    """Short and dark: ~150 ms, sweeping ~250 Hz down to a 55-60 Hz body in ~80 ms."""
    n = int(0.16 * SR)
    t = env_t(n)
    f = 54 + 200 * np.exp(-t / 0.025)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.045)
    x = np.tanh(1.6 * body) * np.minimum(1, (n - np.arange(n)) / (0.01 * SR))
    return filt(x, "lowpass", 900) * vel / 127


def snare(vel):
    """A short, dry body layer under the clap."""
    n = int(0.2 * SR)
    t = env_t(n)
    tone = 0.6 * np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.04)
    tone += 0.3 * np.sin(2 * np.pi * 320 * t) * np.exp(-t / 0.025)
    nz = filt(noise(n), "bandpass", [1000, 7000])
    nz *= np.exp(-t / 0.035) / np.abs(nz).max()
    return np.tanh(1.5 * (tone + 0.9 * nz)) * vel / 127


def clap(vel):
    """Three bursts 12 ms apart, dry: -20 dB by ~50 ms, -40 dB by ~75 ms, little below 600 Hz."""
    n = int(0.15 * SR)
    t = env_t(n)
    nz = filt(noise(n), "bandpass", [700, 3500])
    nz /= np.abs(nz).max()
    env = sum(np.where(t >= d, np.exp(-(t - d) / 0.0045), 0) for d in (0, 0.012, 0.024))
    env += 1.2 * np.where(t >= 0.024, np.exp(-(t - 0.024) / 0.022), 0)
    return nz * env * vel / 127


def metal_noise(seconds, decay):
    n = int(seconds * SR)
    t = env_t(n)
    sq = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (205.3, 304.4, 369.6, 522.7, 540.0, 800.0))
    x = filt(0.5 * sq / 6 + 0.5 * noise(n), "highpass", 4800, order=4)
    x = filt(x, "lowpass", 9000)       # energy peaks around 6 kHz, not in the fizz
    return x * np.exp(-t / decay) / np.abs(x).max()


HAT = metal_noise(0.15, 0.019)         # -20 dB in ~37 ms
OPEN_HAT = metal_noise(0.6, 0.16)


def pitched(sample, semis):
    ratio = 2 ** (semis / 12)
    idx = np.arange(0, len(sample) - 1, ratio)
    return np.interp(idx, np.arange(len(sample)), sample)


def rim(vel):
    n = int(0.12 * SR)
    t = env_t(n)
    x = 0.7 * np.sin(2 * np.pi * 1650 * t) * np.exp(-t / 0.012)
    x += 0.5 * filt(noise(n), "bandpass", [2000, 6000]) * np.exp(-t / 0.005)
    return x * vel / 127


def bell(freq, vel, seconds=2.0):
    """FM bell with a soft ~40 ms attack (the reference's melodic attacks measure ~46 ms)."""
    n = int(seconds * SR)
    t = env_t(n)
    index = 2.0 * np.exp(-t / 0.12) + 0.35
    ph = RNG.random() * 2 * np.pi
    x = np.sin(2 * np.pi * freq * t + ph + index * np.sin(2 * np.pi * 2 * freq * t))
    x += 0.12 * np.sin(2 * np.pi * 3.5 * freq * t) * np.exp(-t / 0.05)
    return x * np.exp(-t / 0.6) * np.minimum(1, t / 0.04) * vel / 127


def wide_bell(freq, vel):
    """Two bells detuned -7/+7 cents with independent phases: nearly uncorrelated L and R."""
    return np.stack([bell(freq * 2 ** (-7 / 1200), vel), bell(freq * 2 ** (7 / 1200), vel)], axis=1)


def glass(freq, vel):
    n = int(0.5 * SR)
    t = env_t(n)
    x = np.sin(2 * np.pi * freq * t)
    x += 0.35 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t / 0.03)
    x += 0.2 * np.sin(2 * np.pi * 5.02 * freq * t) * np.exp(-t / 0.015)
    return x * np.exp(-t / 0.12) * np.minimum(1, t / 0.008) * vel / 127


def zap(vel):
    """A laser-style FX hit: a sine sweeping 3 kHz down to 150 Hz."""
    n = int(0.35 * SR)
    t = env_t(n)
    f = 150 + 2850 * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
    return np.tanh(2 * x) * vel / 127


def pad_note(pitch, seconds, vel):
    release = 1.0
    n = int((seconds + release) * SR)
    t = env_t(n)
    f = hz(pitch)
    voices = [saw(f * 2 ** (c / 1200), n) for c in (-14, -7, 0, 7, 14)]
    left = voices[0] + 0.8 * voices[2] + voices[4] * 0.6
    right = voices[1] + 0.8 * voices[2] + voices[3] * 0.6
    env = np.minimum(1, t / 0.06)
    env = np.where(t > seconds, env * np.exp(-(t - seconds) / 0.3), env)
    return np.stack([left, right], axis=1) * env[:, None] * vel / 127 / 3


# Harmonic levels of the reference's 808 relative to its fundamental, in dB. Waveshaping
# a sine with Chebyshev polynomials sets each one exactly (a plain tanh can't reach a
# 3rd harmonic this loud without over-driving the 5th).
HARMONICS_808 = [(1, 0), (2, -15), (3, -6), (4, -16), (5, -28)]


def shape_808(phase):
    y = sum(10 ** (db / 20) * np.cos(k * phase) for k, db in HARMONICS_808)
    return y / sum(10 ** (db / 20) for _, db in HARMONICS_808)


def widen_808(x, width=0.49):
    """Mono below ~90 Hz; the harmonics above get a 90-degree-shifted side signal, which
    puts their L/R correlation near the reference's 0.6 and folds back to mono cleanly."""
    high = signal.sosfiltfilt(signal.butter(4, 110, "highpass", fs=SR, output="sos"), x)
    side = width * np.imag(signal.hilbert(high))
    return np.stack([x + side, x - side], axis=1)


def render_808(notes, n_total):
    freq = np.zeros(n_total)
    amp = np.zeros(n_total)
    prev_end, prev_f = -1, None
    for n in notes:
        i0 = int(round(n.step * STEP * SR))
        i1 = int(round((n.step + n.length) * STEP * SR))
        end = min(n_total, i1 + int(0.06 * SR))
        idx = np.arange(i0, end)
        f = hz(n.pitch)
        start_val = amp[i0 - 1] if i0 > 0 else 0.0
        a = np.full(len(idx), n.vel / 127)     # flat sustain, like the reference
        if n.glide and prev_end > i0:
            fr = np.full(len(idx), f)
            g = min(int(0.075 * SR), len(idx))
            fr[:g] = prev_f * (f / prev_f) ** (np.arange(g) / g)
            a[:] = start_val
        else:
            fr = f * (1 + 0.3 * np.exp(-(idx - i0) / SR / 0.012))
            att = min(int(0.003 * SR), len(a))
            a[:att] = start_val + (a[:att] - start_val) * np.linspace(0, 1, att)
        tail = idx >= i1
        a[tail] *= np.exp(-(idx[tail] - i1) / SR / 0.02)
        freq[i0:end] = fr
        amp[i0:end] = a
        prev_end, prev_f = i1, f
    return widen_808(amp * shape_808(2 * np.pi * np.cumsum(freq) / SR))


def one_808(pitch, seconds=3.0):
    """A single sustained 808 note, for loading into a sampler."""
    n = int(seconds * SR)
    x = render_808([Note(0, seconds / STEP - 0.6 / STEP, pitch, 127)], n)
    return x / np.abs(x).max()


def make_ir(seconds=1.0, tau=0.08, predelay=0.02, lowpass=6500):
    """Stereo room, RT60 ~0.55 s: the reference's melodic layer decays in ~0.4-0.7 s."""
    n = int(seconds * SR)
    t = env_t(n)
    ir = noise(n * 2).reshape(n, 2) * np.exp(-t / tau)[:, None]
    pd = int(predelay * SR)
    ir[:pd] = 0
    ir[pd:pd + int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))[:, None]
    ir = filt(ir, "lowpass", lowpass)
    return ir / np.sqrt((ir ** 2).sum(axis=0))


IR = make_ir()


def reverb(x, wet):
    mono = x.mean(axis=1)
    wet_sig = np.stack([signal.fftconvolve(mono, IR[:, ch])[: len(x)] for ch in (0, 1)], axis=1)
    return x + wet * wet_sig


def place(bus, x, seconds, pan=0.0):
    i = int(round(seconds * SR))
    if x.ndim == 1:
        a = (pan + 1) * np.pi / 4
        x = np.stack([x * np.cos(a), x * np.sin(a)], axis=1) * np.sqrt(2)
    n = min(len(x), len(bus) - i)
    if n > 0:
        bus[i:i + n] += x[:n]


def rms_db(x):
    active = np.abs(x).max(axis=1) > 1e-4 if x.ndim == 2 else np.abs(x) > 1e-4
    return 20 * np.log10(np.sqrt(np.mean(x[active] ** 2)) + 1e-12)


# Target RMS per bus (dBFS, measured where the part is playing) = the mix balance.
MIX = {"808": -14, "kick": -6,  "snare": -21, "hats": -30, "perc": -33,
       "pad": -27, "lead": -24, "arp": -32, "fx": -28}
TARGET_LUFS = -9.2        # the reference's integrated loudness
CEILING_DBTP = -1.0


def lufs(x):
    import pyloudnorm
    return pyloudnorm.Meter(SR).integrated_loudness(x)


def true_peak_db(x):
    return 20 * np.log10(np.abs(signal.resample_poly(x, 4, 1, axis=0)).max())


def limit(x, ceiling, window=0.02):
    """Look-ahead brickwall: the gain never exceeds what any sample within a window needs."""
    need = np.minimum(1, ceiling / np.maximum(np.abs(x).max(axis=1), 1e-9))
    w = int(window * SR)
    gain = ndimage.minimum_filter1d(need, 2 * w + 1)
    gain = ndimage.uniform_filter1d(gain, w)
    return x * gain[:, None]


def master(mix):
    """Soft clip, then limit, raising the drive until the master reaches TARGET_LUFS."""
    mix = mix / np.abs(mix).max()
    drive = 1.0
    for _ in range(12):
        y = np.tanh(drive * mix) / np.tanh(drive) * 10 ** (-0.3 / 20)
        ceiling = 10 ** (CEILING_DBTP / 20)
        y = limit(y, ceiling)
        tp = true_peak_db(y)
        if tp > CEILING_DBTP:
            y = limit(y, ceiling * 10 ** ((CEILING_DBTP - tp) / 20))
        loud = lufs(y)
        if abs(loud - TARGET_LUFS) < 0.1:
            break
        drive *= 10 ** ((TARGET_LUFS - loud) / 20)
    tp = true_peak_db(y)
    return y * 10 ** (min(0, CEILING_DBTP - tp) / 20)


def render(song, stems_dir=None):
    tail = 2.0
    bar_s = 16 * STEP
    n_total = int((SONG_BARS * bar_s + tail) * SR)
    t_of = lambda n: n.step * STEP  # noqa: E731
    bus = {k: np.zeros((n_total, 2)) for k in MIX if k != "808"}

    # Drums are mono and dry, like the reference's.
    for n in song["kick"]:
        place(bus["kick"], kick(n.vel), t_of(n))
    for n in song["snare"]:
        place(bus["snare"], snare(n.vel), t_of(n))
    for n in song["clap"]:
        place(bus["snare"], 0.8 * clap(n.vel), t_of(n))
    for n in song["hat"]:
        place(bus["hats"], pitched(HAT, n.pitch - DRUM_NOTE) * n.vel / 127, t_of(n))
    for n in song["openhat"]:
        place(bus["hats"], OPEN_HAT * n.vel / 127, t_of(n))
    for i, n in enumerate(song["perc"]):
        place(bus["perc"], pitched(rim(n.vel), n.pitch - DRUM_NOTE), t_of(n), pan=-0.4 if i % 2 else 0.4)

    # Melodic layers are wide (near-uncorrelated L/R), soft-attacked and in a short room.
    for n in song["pad"]:
        place(bus["pad"], pad_note(n.pitch, n.length * STEP, n.vel), t_of(n))
    for n in song["lead"]:
        place(bus["lead"], wide_bell(hz(n.pitch), n.vel), t_of(n))
    for i, n in enumerate(song["arp"]):
        place(bus["arp"], glass(hz(n.pitch), n.vel), t_of(n), pan=-0.6 if i % 2 else 0.6)
    for n in song["fx"]:
        place(bus["fx"], zap(n.vel), t_of(n), pan=-0.3)

    bus["pad"] = reverb(filt(bus["pad"], "lowpass", 4000), 0.35)
    bus["lead"] = reverb(filt(bus["lead"], "highpass", 200), 0.4)
    bus["arp"] = reverb(filt(bus["arp"], "highpass", 500), 0.4)
    bus["fx"] = reverb(bus["fx"], 0.3)
    bus["808"] = render_808(song["808"], n_total)

    for k, target in MIX.items():
        bus[k] *= 10 ** ((target - rms_db(bus[k])) / 20)

    mix = filt(sum(bus.values()), "highpass", 28)
    fade = np.clip(1 - (np.arange(n_total) / SR - SONG_BARS * bar_s) / tail, 0, 1)
    mix = master(mix * fade[:, None])

    if stems_dir:
        stems_dir.mkdir(parents=True, exist_ok=True)
        for k, x in bus.items():
            x = x * fade[:, None]
            sf.write(stems_dir / f"{k}.mp3", x / max(1.0, np.abs(x).max()), SR, format="MP3")
    return mix


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stems", action="store_true", help="also write one audio file per part")
    ap.add_argument("--wav", action="store_true", help="also write a WAV of the preview")
    args = ap.parse_args()

    loops = loop_patterns()
    for i, name in enumerate(p for p in PARTS if loops[p]):
        write_midi(HERE / "midi" / "loops" / f"{i + 1:02d}_{name}.mid", {name: loops[name]})
    song = arrange(loops)
    write_midi(HERE / "midi" / "glasshouse_arrangement.mid", song)
    print("wrote MIDI to", HERE / "midi")

    mix = render(song, HERE / "audio" / "stems" if args.stems else None)
    audio = HERE / "audio"
    audio.mkdir(exist_ok=True)
    sf.write(audio / "glasshouse_preview.mp3", mix, SR, format="MP3")
    if args.wav:
        sf.write(audio / "glasshouse_preview.wav", mix, SR, subtype="PCM_16")
    print(f"wrote preview ({len(mix) / SR:.1f}s) to", audio)


if __name__ == "__main__":
    main()
