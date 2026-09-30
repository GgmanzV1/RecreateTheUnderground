#!/usr/bin/env python3
"""Overexposed - an original 162 BPM rage beat, built as a study companion to
OsamaSon's "Fkd It Up" (prod. ok).

Every chord, melody, drum pattern and 808 line in here is original. What comes from
the reference is the recipe, measured in ANALYSIS.md: 162 BPM with the snare on
beat 3; straight 8th-note drums with no rolls; a clean, flat-sustain 808 that slides
on about half its pitch changes; one mono, soft-attack synth whose low end is
filtered out while the 808 plays and opens up when it drops out; 808-drop and
melody-drop breakdowns in 4-bar blocks; an almost mono mix mastered to -9.3 LUFS.

Outputs (next to this file):
  midi/loops/*.mid                   one 4-bar loop per part, drag into FL's piano roll
  midi/overexposed_arrangement.mid   every part laid out over the whole song
  audio/overexposed_preview.mp3      the finished, mastered beat
  audio/stages/*.mp3                 the beat built up one step at a time (see HOW_ITS_MADE.md)

Usage:
  pip install numpy scipy soundfile mido pyloudnorm
  python3 build_beat.py
  python3 ../tools/build_flp.py build_beat.py     # the FL Studio project
"""
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from dsp import (SR, Note, env_t, fade_out, filt, hz, make_ir, master, noise, padded,  # noqa: E402
                 place, reverb, rms_db, saw, stereo, write_midi)

BPM = 162
STEP = 60 / BPM / 4       # seconds per 16th note
LOOP_BARS = 4             # the reference's melody repeats every 4 bars
DRUM_NOTE = 60            # FL's sampler plays a one-shot at original pitch on C5
TITLE = "Overexposed"

# ---------------------------------------------------------------------------
# Composition (all original). Positions are 16th-note steps inside the 4-bar loop.
# ---------------------------------------------------------------------------

# One chord per bar in B minor: i - VI - III - VII. (808 root, synth voicing)
CHORDS = [
    (35, [59, 62, 66, 69]),        # Bm7    B3 D4 F#4 A4
    (31, [55, 59, 62, 66]),        # Gmaj7  G3 B3 D4 F#4
    (38, [54, 57, 62, 66]),        # D/F#   F#3 A3 D4 F#4
    (33, [57, 61, 64, 69]),        # A      A3 C#4 E4 A4
]

# Top line on straight 8ths: (8th slot, length in 8ths, pitch), five notes a bar.
MELODY = [
    [(0, 2, 78), (2, 2, 74), (4, 1, 71), (5, 1, 73), (6, 2, 74)],
    [(0, 2, 83), (2, 2, 81), (4, 2, 78), (6, 1, 74), (7, 1, 76)],
    [(0, 2, 78), (2, 2, 81), (4, 2, 86), (6, 1, 81), (7, 1, 78)],
    [(0, 2, 76), (2, 2, 73), (4, 2, 69), (6, 1, 73), (7, 1, 76)],
]

# 808 per bar: (step, length, pitch, glide). Half of the pitch changes slide (3-5
# semitones over one 16th, ~90 ms), the rest jump. A 2-step gap in each bar keeps it on
# ~86% of the time. Roots sit low (41-73 Hz, centred near 55 Hz) like the reference's.
BASS = [
    [(0, 4, 35, False), (6, 3, 35, False), (10, 6, 38, True)],
    [(0, 5, 31, False), (8, 3, 31, False), (12, 4, 35, True)],
    [(0, 4, 30, False), (6, 5, 30, False), (12, 4, 33, True)],
    [(0, 5, 33, False), (8, 3, 33, False), (12, 4, 28, True)],
]

# Drums on straight 8ths only. Kicks never on beat 3 (step 8); snare + clap on beat 3.
KICKS = [[0, 6, 10, 14], [0, 2, 6, 12], [0, 6, 10, 14], [0, 4, 6, 12]]


def loop_patterns():
    p = {name: [] for name in PARTS}
    for bar, (root, voicing) in enumerate(CHORDS):
        b = bar * 16
        for pitch in voicing:
            p["keys"].append(Note(b, 16, pitch, 58))
        for slot, ln, pitch in MELODY[bar]:
            p["keys"].append(Note(b + 2 * slot, 2 * ln, pitch, 100 if slot % 2 == 0 else 86))

        for i, (s, ln, pitch, glide) in enumerate(BASS[bar]):
            nxt = BASS[bar][i + 1] if i + 1 < len(BASS[bar]) else BASS[(bar + 1) % 4][0]
            if nxt[3]:
                ln = nxt[0] - s + 1 if i + 1 < len(BASS[bar]) else ln   # overlap so it slides
            p["808"].append(Note(b + s, ln, pitch, 116 if s == 0 else 104, glide=glide))

        for s in KICKS[bar]:
            p["kick"].append(Note(b + s, 1, DRUM_NOTE, 120 if s == 0 else 104))
        p["snare"].append(Note(b + 8, 1, DRUM_NOTE, 116))
        p["clap"].append(Note(b + 8, 1, DRUM_NOTE, 100))
        for s in range(0, 16, 2):
            if bar == 3 and s == 14:
                p["openhat"].append(Note(b + s, 2, DRUM_NOTE, 90))
            else:
                p["hat"].append(Note(b + s, 1, DRUM_NOTE, 108 if s % 4 == 0 else 72))
    p["snare"].append(Note(3 * 16 + 14, 1, DRUM_NOTE, 70))    # ghost snare turning the loop around
    p["keys_open"] = list(p["keys"])
    return p


PARTS = ["kick", "808", "snare", "clap", "hat", "openhat", "keys", "keys_open"]
DRUMS = {"kick", "snare", "clap", "hat", "openhat"}

# "keys" is the synth with its low end filtered out (while the 808 plays); "keys_open"
# is the full version for sections without the 808. Changes happen in 4-bar blocks.
SECTIONS = [
    ("Intro", 0, 4, {"keys_open"}),
    ("Hook", 4, 20, DRUMS | {"808", "keys"}),
    ("Breakdown", 20, 24, {"keys_open"}),
    ("Verse", 24, 40, DRUMS | {"808", "keys"}),
    ("808 drop", 40, 44, DRUMS | {"keys_open"}),
    ("Hook", 44, 60, DRUMS | {"808", "keys"}),
    ("Outro", 60, 64, {"keys_open"}),
]
SONG_BARS = 64
MUTES = {bar: {"keys"} for bar in range(32, 36)}   # the melody drops out for 4 bars of the verse
EXTRAS = []


def arrange(loops):
    song = {name: [] for name in PARTS}
    for _, b0, b1, parts in SECTIONS:
        for bar in range(b0, b1):
            lb = (bar - b0) % LOOP_BARS
            for part in parts - MUTES.get(bar, set()):
                for n in loops[part]:
                    if lb * 16 <= n.step < (lb + 1) * 16:
                        song[part].append(replace(n, step=n.step + (bar - lb) * 16))
    for part in song:
        song[part].sort(key=lambda n: n.step)
    return song


# ---------------------------------------------------------------------------
# Sounds, each built to the reference's measured targets (see ANALYSIS.md)
# ---------------------------------------------------------------------------

def kick(vel):
    """~200 Hz sweeping to a 54 Hz body; -20 dB at ~110 ms; a little click on top."""
    n = int(0.3 * SR)
    t = env_t(n)
    f = 54 + 150 * np.exp(-t / 0.02)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.047)
    click = filt(noise(n), "bandpass", [2000, 7000]) * np.exp(-t / 0.003) * 0.15
    return fade_out(np.tanh(1.4 * body) + click, 0.02) * vel / 127


def snare(vel):
    """Bright noise over a 200 Hz body: peak ~1.1 kHz, -20 dB in ~47 ms."""
    n = int(0.25 * SR)
    t = env_t(n)
    tone = 0.5 * np.sin(2 * np.pi * 200 * t) * np.exp(-t / 0.03)
    nz = filt(noise(n), "bandpass", [900, 9000])
    nz *= np.exp(-t / 0.02) / np.abs(nz).max()
    return fade_out(np.tanh(1.5 * (tone + nz)), 0.02) * vel / 127


def clap(vel):
    n = int(0.2 * SR)
    t = env_t(n)
    nz = filt(noise(n), "bandpass", [800, 5000])
    nz /= np.abs(nz).max()
    env = sum(np.where(t >= d, np.exp(-(t - d) / 0.004), 0) for d in (0, 0.01, 0.02))
    env += np.where(t >= 0.02, np.exp(-(t - 0.02) / 0.02), 0)
    return fade_out(nz * env, 0.02) * vel / 127


def metal_noise(seconds, decay):
    n = int(seconds * SR)
    t = env_t(n)
    sq = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (205.3, 304.4, 369.6, 522.7, 540.0, 800.0))
    x = filt(0.5 * sq / 6 + 0.5 * noise(n), "highpass", 5500, order=4)
    x = filt(x, "lowpass", 10000)      # bright, but most of the energy stays under 10 kHz
    return x * np.exp(-t / decay) / np.abs(x).max()


HAT = metal_noise(0.12, 0.012)          # -20 dB in ~27 ms
OPEN_HAT = metal_noise(0.5, 0.12)


def pitched(sample, semis):
    ratio = 2 ** (semis / 12)
    idx = np.arange(0, len(sample) - 1, ratio)
    return np.interp(idx, np.arange(len(sample)), sample)


def swell(pitch, seconds, vel):
    """The synth: three detuned saws, low-passed, with a slow ~130 ms swell and a short
    release. Nearly mono: left and right share the middle voice and differ only a little."""
    release = 0.25
    n = int((seconds + release) * SR)
    t = env_t(n)
    f = hz(pitch)
    a, b, c = (saw(f * 2 ** (d / 1200), n) for d in (-8, 0, 8))
    left, right = b + 0.55 * a + 0.45 * c, b + 0.55 * c + 0.45 * a
    env = 1 - np.exp(-t / 0.045)                           # ~130 ms to full level
    env = np.where(t > seconds, env * np.exp(-(t - seconds) / 0.08), env)
    x = np.stack([left, right], axis=1) * env[:, None] * vel / 127 / 2
    return filt(x, "lowpass", 3500)


# Harmonic levels of the reference's 808 relative to its fundamental (dB): a clean,
# sub-heavy 808, much less distorted than "Winnie Harlow"'s.
HARMONICS_808 = [(1, 0), (2, -26), (3, -21), (4, -31), (5, -25), (6, -35), (7, -32)]
SLIDE_SECONDS = 0.09


GRIT_DB = -12             # a faint squared-up layer above 600 Hz: the reference 808's upper overtones


def shape_808(phase):
    y = sum(10 ** (db / 20) * np.cos(k * phase) for k, db in HARMONICS_808)
    return y / sum(10 ** (db / 20) for _, db in HARMONICS_808)


def grit(x):
    sq = np.tanh(12 * x / (np.abs(x).max() + 1e-12))
    return 10 ** (GRIT_DB / 20) * filt(filt(sq, "highpass", 600, order=4), "lowpass", 3000)


def render_808(notes, n_total, glides=True):
    """Flat sustain, mono. Glide notes bend from the previous pitch over SLIDE_SECONDS."""
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
        a = np.full(len(idx), n.vel / 127)
        if glides and n.glide and prev_end > i0:
            fr = np.full(len(idx), f)
            g = min(int(SLIDE_SECONDS * SR), len(idx))
            fr[:g] = prev_f * (f / prev_f) ** (np.arange(g) / g)
            a[:] = start_val
        else:
            fr = f * (1 + 0.2 * np.exp(-(idx - i0) / SR / 0.01))
            att = min(int(0.003 * SR), len(a))
            a[:att] = start_val + (a[:att] - start_val) * np.linspace(0, 1, att)
        tail = idx >= i1
        a[tail] *= np.exp(-(idx[tail] - i1) / SR / 0.02)
        freq[i0:end] = fr
        amp[i0:end] = a
        prev_end, prev_f = i1, f
    x = amp * shape_808(2 * np.pi * np.cumsum(freq) / SR)
    x = x + grit(x)
    return np.stack([x, x], axis=1)


def one_808(pitch, seconds=3.0):
    n = int(seconds * SR)
    x = render_808([Note(0, (seconds - 0.6) / STEP, pitch, 127)], n)
    return x / np.abs(x).max()


IR = make_ir(seconds=1.0, tau=0.07)     # short room


# The filter trick: while the 808 plays, the synth sits lower and loses its low mids;
# in the breakdowns the full version comes back. Measured on the reference, the melody is
# ~12 dB louder below 640 Hz, 5-7 dB louder in the mids and ~2 dB louder up top without
# the 808. Here: a -10 dB low shelf under ~500 Hz, a +4 dB lift above 5 kHz, plus the
# level difference in MIX. Thinner and a little brighter, so it stays out of the 808's way.
THIN_SHELF_HZ, THIN_SHELF_DB = 500, -10
THIN_AIR_HZ, THIN_AIR_DB = 5000, 4


def thin(x):
    """Low shelf down, high shelf up."""
    x = x - (1 - 10 ** (THIN_SHELF_DB / 20)) * filt(x, "lowpass", THIN_SHELF_HZ)
    return x + (10 ** (THIN_AIR_DB / 20) - 1) * filt(x, "highpass", THIN_AIR_HZ)

# Target RMS per bus (dBFS, measured where the part is playing) = the mix balance.
MIX = {"808": -11, "kick": -25, "snare": -26, "hats": -25, "keys": -27, "keys_open": -21}
TARGET_LUFS = -9.3
BUS_OF = {"clap": "snare", "hat": "hats", "openhat": "hats"}


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render_buses(song, glides=True, keys_fx=True):
    bar_s = 16 * STEP
    n_total = int((SONG_BARS * bar_s + 2.0) * SR)
    t_of = lambda n: n.step * STEP  # noqa: E731
    bus = {k: np.zeros((n_total, 2)) for k in MIX if k != "808"}
    for n in song["kick"]:
        place(bus["kick"], kick(n.vel), t_of(n))
    for n in song["snare"]:
        place(bus["snare"], snare(n.vel), t_of(n))
    for n in song["clap"]:
        place(bus["snare"], 0.7 * clap(n.vel), t_of(n))
    for n in song["hat"]:
        place(bus["hats"], HAT * n.vel / 127, t_of(n))
    for n in song["openhat"]:
        place(bus["hats"], OPEN_HAT * n.vel / 127, t_of(n))
    for part in ("keys", "keys_open"):
        for n in song[part]:
            place(bus[part], swell(n.pitch, n.length * STEP, n.vel), t_of(n))
    if keys_fx:
        bus["keys"] = reverb(thin(bus["keys"]), 0.2, IR)
        bus["keys_open"] = reverb(bus["keys_open"], 0.2, IR)
    bus["808"] = render_808(song["808"], n_total, glides)
    return bus


def levels(bus):
    return {k: 10 ** ((MIX[k] - rms_db(x)) / 20) for k, x in bus.items()}


def mixdown(bus, gains, parts=None, bars=None):
    keys = [k for k in bus if parts is None or k in parts]
    mix = filt(sum(bus[k] * gains[k] for k in keys), "highpass", 28)
    if bars:
        mix = mix[int(bars[0] * 16 * STEP * SR): int(bars[1] * 16 * STEP * SR)]
    return mix


def export(path, x, normalize=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    if normalize:
        x = x * 10 ** (-1 / 20) / np.abs(x).max()
    sf.write(path, x, SR, format="MP3")


def render_stages(song, bus, gains):
    """The build-up, one step at a time. Each clip is the first 8 bars of the hook unless noted."""
    out = HERE / "audio" / "stages"
    hook = (4, 12)
    raw = render_buses(song, keys_fx=False)
    open_hook = {"keys_open": raw["keys"]}          # the hook's notes through the unfiltered synth
    export(out / "01_synth_dry.mp3", mixdown(open_hook, {"keys_open": gains["keys_open"]}, bars=hook))
    thin = mixdown(bus, gains, {"keys"}, bars=(4, 8))
    full = mixdown({"keys_open": reverb(raw["keys"], 0.2, IR)}, {"keys_open": gains["keys_open"]}, bars=(4, 8))
    export(out / "02_synth_filter_trick.mp3", np.concatenate([full, thin]) / max(np.abs(full).max(), 1e-9) * 0.89,
           normalize=False)
    export(out / "03_drums.mp3", mixdown(bus, gains, {"kick", "snare", "hats"}, bars=hook))
    no_slide = render_buses(song, glides=False)
    export(out / "04_808_no_slides.mp3", mixdown({"808": no_slide["808"]}, gains, bars=hook))
    export(out / "05_808_with_slides.mp3", mixdown(bus, gains, {"808"}, bars=hook))
    loop = mixdown(bus, gains, bars=hook)
    export(out / "06_all_parts_unmastered.mp3", loop)
    export(out / "07_all_parts_mastered.mp3", master(loop, TARGET_LUFS), normalize=False)
    export(out / "08_hook_breakdown_verse.mp3", master(mixdown(bus, gains, bars=(16, 28)), TARGET_LUFS),
           normalize=False)


# ---------------------------------------------------------------------------
# FL Studio project (tools/build_flp.py reads this)
# ---------------------------------------------------------------------------

FL_CHANNELS = [
    ("kick", "Kick", 60), ("808", "808", 36), ("snare", "Snare", 60), ("clap", "Clap", 60),
    ("hat", "Hat", 60), ("openhat", "Open Hat", 60), ("keys", "Swell (filtered)", 72),
    ("keys_open", "Swell (open)", 72),
]


def fl_samples():
    full = swell(72, 4.0, 127)
    return {
        "kick": kick(127),
        "808": fade_out(one_808(36)),
        "snare": snare(127),
        "clap": 0.7 * clap(127),
        "hat": HAT,
        "openhat": OPEN_HAT,
        "keys": fade_out(reverb(padded(thin(full), 0.8), 0.2, IR)),
        "keys_open": fade_out(reverb(padded(full, 0.8), 0.2, IR)),
    }


FL_PROJECT = dict(
    name=TITLE,
    genre="Rage",
    comment=(f"{TITLE}: an original 162 BPM beat from the Fkd It Up style study. "
             f"Keep the {TITLE} *.wav samples in the same folder as this project."),
    channels=FL_CHANNELS,
    groups=[
        ("Drums", "Drums", ["kick", "snare", "clap", "hat", "openhat"]),
        ("808", "808", ["808"]),
        ("Swell (filtered)", "Swell (filtered)", ["keys"]),
        ("Swell (open)", "Swell (open)", ["keys_open"]),
    ],
    envelopes={
        "808": dict(attack=100, hold=100, decay=30000, sustain=128, release=12000),
        "keys": dict(attack=100, hold=100, decay=30000, sustain=128, release=16000),
        "keys_open": dict(attack=100, hold=100, decay=30000, sustain=128, release=16000),
    },
    mono={"808"},
    porta={"808"},             # this 808 slides a lot; FL's Porta glides every pitch change
    slide=250,
    cut_group={"hat", "openhat"},
    mix_bus=BUS_OF,
    samples=fl_samples,
)


def main():
    loops = loop_patterns()
    for i, name in enumerate(p for p in PARTS if p != "keys_open"):
        write_midi(HERE / "midi" / "loops" / f"{i + 1:02d}_{name}.mid", TITLE, BPM, {name: loops[name]})
    song = arrange(loops)
    write_midi(HERE / "midi" / "overexposed_arrangement.mid", TITLE, BPM, song)
    print("wrote MIDI to", HERE / "midi")

    bus = render_buses(song)
    gains = levels(bus)
    total = SONG_BARS * 16 * STEP + 2.0
    fade = np.clip((total - np.arange(int(total * SR)) / SR) / 2.0, 0, 1)[:, None]
    mix = master(mixdown(bus, gains) * fade[: len(bus["808"])], TARGET_LUFS)
    export(HERE / "audio" / "overexposed_preview.mp3", mix, normalize=False)
    sf.write(HERE / "audio" / "overexposed_preview.wav", mix, SR, subtype="PCM_16")
    print(f"wrote preview ({len(mix) / SR:.1f}s)")
    render_stages(song, bus, gains)
    print("wrote stages to", HERE / "audio" / "stages")


if __name__ == "__main__":
    main()
