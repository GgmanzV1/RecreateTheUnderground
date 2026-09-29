#!/usr/bin/env python3
"""Glasshouse - an original 140 BPM underground beat, built as a study companion
to Nettspend's "Winnie Harlow".

It uses the production framework measured from the reference (140 BPM half-time,
G# minor with the weight on D#, a distorted 808 that never leaves, washed-out
synths, a loop-based arrangement that changes by muting parts), but every chord,
melody and drum pattern in here is original.

Outputs (next to this file):
  midi/loops/*.mid                 one 8-bar loop per part, drag into FL's piano roll
  midi/glasshouse_arrangement.mid  every part laid out over the whole song
  audio/glasshouse_preview.mp3     synthesized preview of the target sound

Usage:
  pip install numpy scipy soundfile mido
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
from scipy import signal

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

# Lead: a 3-3-2 / 3-3-2 syncopated bell motif, re-voiced over each chord.
LEAD_RHYTHM = [(0, 3), (3, 3), (6, 2), (8, 3), (11, 3), (14, 2)]
LEAD_ACCENT = [112, 88, 96, 106, 90, 96]
LEAD_NOTES = [
    ([87, 83, 80, 82, 83, 85], [87, 83, 80, 82, 80, 78]),
    ([87, 83, 80, 78, 80, 83], [87, 83, 80, 78, 76, 75]),
    ([88, 85, 80, 83, 85, 87], [88, 85, 80, 83, 80, 76]),
    ([85, 82, 78, 80, 82, 85], [87, 82, 78, 75, 78, 82]),
]

# 808 per two bars: (step, length, semitones from root). The last event glides.
BASS_A = [(0, 6, 0), (7, 3, 0), (11, 5, 0), (16, 3, 0), (19, 6, 0), (26, 2, 0), (28, 4, 12)]
BASS_B = [(0, 6, 0), (7, 3, 0), (11, 5, 0), (16, 6, 0), (24, 6, 0), (30, 2, -7)]
KICK_A = [0, 7, 11, 16, 19]
KICK_B = [0, 7, 11, 16, 24]

DRUM_NOTE = 60            # FL's sampler plays a one-shot at original pitch on C5


def loop_patterns():
    p = {name: [] for name in PARTS}

    for c, (root, voicing) in enumerate(CHORDS):
        base = c * 32
        last = c == len(CHORDS) - 1
        bass, kicks = (BASS_B, KICK_B) if last else (BASS_A, KICK_A)
        for i, (s, ln, off) in enumerate(bass):
            if i == len(bass) - 2:
                ln += 1   # overlap the glide note so FL's Porta mode slides into it
            p["808"].append(Note(base + s, ln, root + off, 118 if s % 16 == 0 else 104,
                                 glide=i == len(bass) - 1))
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

        hats = {s: v for s, v in zip(range(0, 16, 2), [100, 74, 94, 74, 100, 74, 94, 80])}
        rolls = []
        if bar in (1, 5):     # 16th-note triplet roll on beat 4 (bar 6 climbs in pitch)
            hats = {s: v for s, v in hats.items() if s < 12}
            rolls = [(12 + i * 4 / 6, 4 / 6, 60 + (i if bar == 5 else 0), 70 + 5 * i) for i in range(6)]
        elif bar == 3:        # 32nd-note roll on beat 2, swelling in
            hats = {s: v for s, v in hats.items() if not 4 <= s < 8}
            rolls = [(4 + i * 0.5, 0.5, 60, 55 + 6 * i) for i in range(8)]
        elif bar == 7:        # 16ths into a rising 32nd-triplet roll to turn the loop around
            hats = {s: v for s, v in hats.items() if s < 8}
            rolls = [(8 + i, 1, 60, 86 if i % 2 == 0 else 64) for i in range(4)]
            rolls += [(12 + i / 3, 1 / 3, 60 + i // 2, 60 + 4 * i) for i in range(12)]
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


PARTS = ["kick", "808", "snare", "clap", "hat", "openhat", "perc", "pad", "lead", "arp", "riser"]
DRUMS = {"kick", "808", "snare", "clap", "hat", "openhat", "perc"}

# Sections start on loop boundaries and last a multiple of 8 bars.
SECTIONS = [
    ("Intro", 0, 8, {"pad", "lead"}),
    ("Hook", 8, 24, DRUMS | {"pad", "lead"}),
    ("Verse", 24, 40, DRUMS | {"pad", "arp"}),
    ("Hook", 40, 56, DRUMS | {"pad", "lead", "arp"}),
    ("Outro", 56, 64, {"pad", "lead", "arp"}),
]
SONG_BARS = 64
# Bar-level drop-outs: the "808 stop" and the pre-hook gap.
MUTES = {31: {"kick", "808"}, 39: DRUMS - {"hat"}}


def arrange(loops):
    song = {name: [] for name in PARTS}
    for _, b0, b1, parts in SECTIONS:
        for bar in range(b0, b1):
            lb = (bar - b0) % LOOP_BARS
            for part in parts - MUTES.get(bar, set()):
                for n in loops[part]:
                    if lb * 16 <= n.step < (lb + 1) * 16:
                        song[part].append(replace(n, step=n.step + (bar - lb) * 16))
    song["riser"].append(Note(6 * 16, 32, DRUM_NOTE, 100))
    song["808"].append(Note(56 * 16, 16, CHORDS[0][0], 120))   # last boom on the outro
    song["kick"].append(Note(56 * 16, 1, DRUM_NOTE, 120))
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
    n = int(0.4 * SR)
    t = env_t(n)
    f = 48 + 170 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.14)
    click = filt(noise(n), "highpass", 3000) * np.exp(-t / 0.004) * 0.35
    return np.tanh(1.8 * (body + click)) * vel / 127


def snare(vel):
    n = int(0.35 * SR)
    t = env_t(n)
    tone = 0.6 * np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.06)
    tone += 0.3 * np.sin(2 * np.pi * 320 * t) * np.exp(-t / 0.035)
    nz = filt(noise(n), "bandpass", [1200, 9000])
    nz *= np.exp(-t / 0.11) / np.abs(nz).max()
    return np.tanh(1.5 * (tone + 0.9 * nz)) * vel / 127


def clap(vel):
    n = int(0.4 * SR)
    t = env_t(n)
    nz = filt(noise(n), "bandpass", [900, 5000])
    nz /= np.abs(nz).max()
    env = sum(np.where(t >= d, np.exp(-(t - d) / 0.0045), 0) for d in (0, 0.012, 0.024))
    env += 0.8 * np.where(t >= 0.034, np.exp(-(t - 0.034) / 0.13), 0)
    return nz * env * vel / 127


def metal_noise(seconds, decay):
    n = int(seconds * SR)
    t = env_t(n)
    sq = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (205.3, 304.4, 369.6, 522.7, 540.0, 800.0))
    x = filt(0.5 * sq / 6 + 0.5 * noise(n), "highpass", 6500, order=4)
    return x * np.exp(-t / decay) / np.abs(x).max()


HAT = metal_noise(0.25, 0.028)
OPEN_HAT = metal_noise(0.7, 0.22)


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
    n = int(seconds * SR)
    t = env_t(n)
    index = 2.4 * np.exp(-t / 0.10) + 0.35
    x = np.sin(2 * np.pi * freq * t + index * np.sin(2 * np.pi * 2 * freq * t))
    x += 0.12 * np.sin(2 * np.pi * 3.5 * freq * t) * np.exp(-t / 0.05)
    return x * np.exp(-t / 0.6) * np.minimum(1, t / 0.002) * vel / 127


def glass(freq, vel):
    n = int(0.5 * SR)
    t = env_t(n)
    x = np.sin(2 * np.pi * freq * t)
    x += 0.35 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t / 0.03)
    x += 0.2 * np.sin(2 * np.pi * 5.02 * freq * t) * np.exp(-t / 0.015)
    return x * np.exp(-t / 0.12) * np.minimum(1, t / 0.001) * vel / 127


def pad_note(pitch, seconds, vel):
    release = 1.6
    n = int((seconds + release) * SR)
    t = env_t(n)
    f = hz(pitch)
    voices = [saw(f * 2 ** (c / 1200), n) for c in (-14, -7, 0, 7, 14)]
    left = voices[0] + 0.8 * voices[2] + voices[4] * 0.6
    right = voices[1] + 0.8 * voices[2] + voices[3] * 0.6
    env = np.minimum(1, t / 0.4)
    env = np.where(t > seconds, env * np.exp(-(t - seconds) / 0.45), env)
    return np.stack([left, right], axis=1) * env[:, None] * vel / 127 / 3


def render_808(notes, n_total):
    freq = np.zeros(n_total)
    amp = np.zeros(n_total)
    prev_end, prev_f, trig = -1, None, 0
    for n in notes:
        i0 = int(round(n.step * STEP * SR))
        i1 = int(round((n.step + n.length) * STEP * SR))
        end = min(n_total, i1 + int(0.06 * SR))
        idx = np.arange(i0, end)
        f = hz(n.pitch)
        start_val = amp[i0 - 1] if i0 > 0 else 0.0
        if n.glide and prev_end > i0:
            fr = np.full(len(idx), f)
            g = min(int(0.075 * SR), len(idx))
            fr[:g] = prev_f * (f / prev_f) ** (np.arange(g) / g)
            a = np.exp(-(idx - trig) / SR / 1.6) * n.vel / 127
        else:
            trig = i0
            fr = f * (1 + 0.5 * np.exp(-(idx - i0) / SR / 0.012))
            a = np.exp(-(idx - i0) / SR / 1.6) * n.vel / 127
            att = min(int(0.003 * SR), len(a))
            ramp = np.linspace(0, 1, att)
            a[:att] = start_val + (a[:att] - start_val) * ramp
        tail = idx >= i1
        a[tail] *= np.exp(-(idx[tail] - i1) / SR / 0.02)
        freq[i0:end] = fr
        amp[i0:end] = a
        prev_end, prev_f = i1, f
    x = np.sin(2 * np.pi * np.cumsum(freq) / SR) * amp
    y = 0.55 * x + 0.45 * np.tanh(3.0 * x) / np.tanh(3.0)
    return filt(y, "lowpass", 4000)


def make_ir(seconds=3.2, tau=0.55, predelay=0.02, lowpass=6500):
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


def pingpong(x, seconds, feedback, wet, taps=6):
    out = x.copy()
    mono = x.mean(axis=1)
    for k in range(1, taps + 1):
        d = int(k * seconds * SR)
        if d >= len(x):
            break
        out[d:, k % 2] += mono[:-d] * wet * feedback ** (k - 1)
    return out


def bitcrush(x, bits=7, hold=2):
    held = np.repeat(x[::hold], hold, axis=0)[: len(x)]
    q = 2 ** (bits - 1)
    return np.round(held * q) / q


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
MIX = {"808": -13, "kick": -21, "snare": -21, "hats": -30, "perc": -33,
       "pad": -27, "lead": -24, "arp": -32, "riser": -28}


def render(song, stems_dir=None):
    tail = 3.0
    bar_s = 16 * STEP
    n_total = int((SONG_BARS * bar_s + tail) * SR)
    t_of = lambda n: n.step * STEP  # noqa: E731
    bus = {k: np.zeros((n_total, 2)) for k in MIX if k != "808"}

    for n in song["kick"]:
        place(bus["kick"], kick(n.vel), t_of(n))
    for n in song["snare"]:
        place(bus["snare"], snare(n.vel), t_of(n))
    for n in song["clap"]:
        place(bus["snare"], 0.8 * clap(n.vel), t_of(n), pan=0.05)
    for i, n in enumerate(song["hat"]):
        place(bus["hats"], pitched(HAT, n.pitch - DRUM_NOTE) * n.vel / 127, t_of(n), pan=0.15)
    for n in song["openhat"]:
        place(bus["hats"], OPEN_HAT * n.vel / 127, t_of(n), pan=-0.1)
    for i, n in enumerate(song["perc"]):
        place(bus["perc"], pitched(rim(n.vel), n.pitch - DRUM_NOTE), t_of(n), pan=-0.4 if i % 2 else 0.4)
    for n in song["pad"]:
        place(bus["pad"], pad_note(n.pitch, n.length * STEP, n.vel), t_of(n))
    for n in song["lead"]:
        f = hz(n.pitch)
        place(bus["lead"], bell(f, n.vel), t_of(n), pan=-0.35)
        place(bus["lead"], bell(f * 2 ** (6 / 1200), n.vel), t_of(n), pan=0.35)
    for i, n in enumerate(song["arp"]):
        place(bus["arp"], glass(hz(n.pitch), n.vel), t_of(n), pan=-0.5 if i % 2 else 0.5)
    for n in song["riser"]:
        dur = n.length * STEP
        m = int(dur * SR)
        f, t, z = signal.stft(noise(m), fs=SR, nperseg=2048)
        center = 400 * (9000 / 400) ** (t / dur)
        mask = np.exp(-0.5 * (np.log2((f[:, None] + 1) / center[None, :]) / 0.6) ** 2)
        _, x = signal.istft(z * mask * (t / dur) ** 2, fs=SR, nperseg=2048)
        place(bus["riser"], x[:m], t_of(n))

    # Intro: pad and lead start behind a low-pass that opens over bars 7-8.
    ramp = np.clip((np.arange(n_total) / SR - 6 * bar_s) / (2 * bar_s), 0, 1)[:, None]
    for k, cutoff in (("pad", 700), ("lead", 900)):
        bus[k] = filt(bus[k], "lowpass", cutoff) * (1 - ramp) + bus[k] * ramp
    bus["pad"] = filt(bus["pad"], "lowpass", 2600)

    bus["lead"] = filt(bus["lead"], "highpass", 200)
    bus["lead"] = reverb(pingpong(bus["lead"], 3 * STEP, 0.38, 0.28), 0.32)
    bus["arp"] = reverb(filt(bitcrush(bus["arp"]), "highpass", 500), 0.5)
    bus["pad"] = reverb(bus["pad"], 0.4)
    bus["snare"] = reverb(bus["snare"], 0.12)
    bus["riser"] = reverb(bus["riser"], 0.5)

    # Kick-triggered ducking on the washy parts so the drums punch through.
    duck = np.ones(n_total)
    for n in song["kick"]:
        i = int(t_of(n) * SR)
        m = min(int(0.45 * SR), n_total - i)
        duck[i:i + m] = np.minimum(duck[i:i + m], 1 - 0.45 * np.exp(-np.arange(m) / SR / 0.16))
    for k in ("pad", "arp"):
        bus[k] *= duck[:, None]

    b808 = render_808(song["808"], n_total)
    bus["808"] = np.stack([b808, b808], axis=1)

    for k, target in MIX.items():
        bus[k] *= 10 ** ((target - rms_db(bus[k])) / 20)

    # Hats stay crisp but lose some fizz; the reference's top end is dark.
    bus["hats"] = filt(bus["hats"], "lowpass", 11000)
    mix = filt(sum(bus.values()), "highpass", 28)
    fade = np.clip(1 - (np.arange(n_total) / SR - 58 * bar_s) / (6 * bar_s + tail), 0, 1)
    mix *= fade[:, None]
    mix /= np.abs(mix).max()
    mix = np.tanh(1.6 * mix) / np.tanh(1.6)
    mix *= 10 ** (-1 / 20) / np.abs(mix).max()

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
