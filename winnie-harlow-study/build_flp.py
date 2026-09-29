#!/usr/bin/env python3
"""Build Glasshouse as an FL Studio project: fl_project/Glasshouse.flp plus its samples.

The notes and arrangement come from build_beat.py, so the project plays the same
parts as the MIDI files. Every channel is a Sampler loaded with a one-shot rendered
from the same synthesis as the preview, so it plays with no third-party plugins.

FL Studio's .flp format has no public spec. This file writes it by copying events
out of two files FL Studio 20.8.4 saved itself (fl_template/) and filling in
Glasshouse's channels, patterns, playlist and mixer names. Event IDs and layouts
follow PyFLP (https://github.com/demberto/PyFLP).

Outputs (next to this file):
  fl_project/Glasshouse.flp
  fl_project/Glasshouse <part>.wav   one sample per channel, keep them next to the .flp

Usage:
  pip install numpy scipy soundfile mido
  python3 build_flp.py
"""
import struct
from pathlib import Path

import numpy as np
import soundfile as sf

import build_beat as bb

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "fl_template"
OUT = HERE / "fl_project"
SR = bb.SR
PPQ = 96
TICKS_PER_STEP = PPQ // 4
BAR = 16 * TICKS_PER_STEP

# (part in build_beat, channel name, sample root note). FL names MIDI 60 "C5".
CHANNELS = [
    ("kick", "Kick", 60),
    ("808", "808", 36),
    ("snare", "Snare", 60),
    ("clap", "Clap", 60),
    ("hat", "Hat", 60),
    ("openhat", "Open Hat", 60),
    ("perc", "Rim", 60),
    ("pad", "Pad", 60),
    ("lead", "Bell Lead", 69),
    ("arp", "Glass Arp", 72),
    ("fx", "Zap", 60),
]
CH = {part: i for i, (part, _, _) in enumerate(CHANNELS)}
CHANNELS_BY_PART = [(part, name) for part, name, _ in CHANNELS]
ROOT = {part: root for part, _, root in CHANNELS}
MIX_BUS = {"clap": "snare", "hat": "hats", "openhat": "hats"}   # parts sharing a bus in build_beat.MIX

# Playlist tracks: (track name, pattern name, parts). One 8-bar pattern each.
GROUPS = [
    ("Drums", "Drums", ["kick", "snare", "clap", "hat", "openhat", "perc"]),
    ("808", "808", ["808"]),
    ("Chords", "Chords", ["pad"]),
    ("Lead", "Lead", ["lead"]),
    ("Arp", "Arp", ["arp"]),
]
FX_TRACK = "FX"
VARIANT_NAMES = {frozenset({"snare", "clap", "hat", "openhat", "perc"}): "Drums (no kick)"}

# Sampler volume envelope for parts whose sound must stop when the note ends.
# Without it FL's Sampler plays the whole sample regardless of note length.
# Values are FL's raw knob values: times 100-65536, sustain 0-128.
ENVELOPES = {
    "808": dict(attack=100, hold=100, decay=30000, sustain=128, release=12000),
    "pad": dict(attack=100, hold=100, decay=30000, sustain=128, release=30000),
}


# ---------------------------------------------------------------------------
# Samples
# ---------------------------------------------------------------------------

def stereo(x):
    return np.stack([x, x], axis=1) if x.ndim == 1 else x


def padded(x, seconds):
    return np.concatenate([stereo(x), np.zeros((int(seconds * SR), 2))])


def fade_out(x, seconds=0.05):
    n = int(seconds * SR)
    x = x.copy()
    x[-n:] *= np.linspace(1, 0, n)[:, None] if x.ndim == 2 else np.linspace(1, 0, n)
    return x


def render_samples():
    """Dry, mono drums; the melodic layers and FX keep the short room build_beat gives them."""
    lead = bb.filt(bb.wide_bell(bb.hz(ROOT["lead"]), 127), "highpass", 200)
    arp = bb.filt(stereo(bb.glass(bb.hz(ROOT["arp"]), 127)), "highpass", 500)
    pad = bb.filt(bb.pad_note(ROOT["pad"], 8.0, 127), "lowpass", 4000)
    return {
        "kick": bb.kick(127),
        "808": fade_out(bb.one_808(ROOT["808"])),
        "snare": bb.snare(127),
        "clap": 0.8 * bb.clap(127),
        "hat": bb.HAT,
        "openhat": bb.OPEN_HAT,
        "perc": bb.rim(127),
        "pad": fade_out(bb.reverb(padded(pad, 0.5), 0.35)),
        "lead": fade_out(bb.reverb(padded(lead, 1.0), 0.4)),
        "arp": fade_out(bb.reverb(padded(arp, 1.0), 0.4)),
        "fx": fade_out(bb.reverb(padded(bb.zap(127), 1.0), 0.3)),
    }


# ---------------------------------------------------------------------------
# Rough FL Sampler playback, used only to set sample levels to build_beat.MIX
# ---------------------------------------------------------------------------

def play(song, samples):
    n_total = int((bb.SONG_BARS * 16 * bb.STEP + 4) * SR)
    buses = {}
    for part, notes in song.items():
        x = stereo(samples[part])
        bus = buses.setdefault(MIX_BUS.get(part, part), np.zeros((n_total, 2)))
        starts = [int(round(n.step * bb.STEP * SR)) for n in notes]
        for k, n in enumerate(notes):
            idx = np.arange(0, len(x) - 1, 2 ** ((n.pitch - ROOT[part]) / 12))
            y = np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in (0, 1)], axis=1)
            stop = len(y)
            if part in ENVELOPES:
                stop = int(n.length * bb.STEP * SR) + int(0.15 * SR)
            if part in ("808", "hat", "openhat") and k + 1 < len(notes):
                stop = min(stop, starts[k + 1] - starts[k])   # mono / cut group
            y = y[:max(stop, 1)] * n.vel / 127
            i = starts[k]
            m = min(len(y), n_total - i)
            bus[i:i + m] += y[:m]
    return buses


def set_levels(song, samples):
    buses = play(song, samples)
    gain = {bus: 10 ** ((bb.MIX[bus] - bb.rms_db(x)) / 20) for bus, x in buses.items()}
    out = {p: x * gain[MIX_BUS.get(p, p)] for p, x in samples.items()}
    mix_peak = np.abs(sum(b * gain[k] for k, b in buses.items())).max()
    sample_peak = max(np.abs(x).max() for x in out.values())
    scale = min(10 ** (-3 / 20) / mix_peak, 0.98 / sample_peak)
    return {p: x * scale for p, x in out.items()}


# ---------------------------------------------------------------------------
# FLP events
# ---------------------------------------------------------------------------

def read_events(path):
    b = path.read_bytes()
    assert b[:4] == b"FLhd" and b[14:18] == b"FLdt", f"{path} is not an FL Studio file"
    i, end = 22, 22 + struct.unpack("<I", b[18:22])[0]
    events = []
    while i < end:
        eid = b[i]
        i += 1
        if eid < 192:
            size = 1 if eid < 64 else 2 if eid < 128 else 4
        else:
            size = shift = 0
            while True:
                c = b[i]
                i += 1
                size |= (c & 0x7F) << shift
                shift += 7
                if not c & 0x80:
                    break
        events.append((eid, b[i:i + size]))
        i += size
    return events


def encode(events):
    out = bytearray()
    for eid, data in events:
        out.append(eid)
        if eid >= 192:
            n = len(data)
            while True:
                out.append((n & 0x7F) | (0x80 if n > 0x7F else 0))
                n >>= 7
                if not n:
                    break
        else:
            assert len(data) == (1 if eid < 64 else 2 if eid < 128 else 4), eid
        out += data
    return bytes(out)


def u8(v):
    return struct.pack("<B", v)


def u16(v):
    return struct.pack("<H", v)


def u32(v):
    return struct.pack("<I", v & 0xFFFFFFFF)


def text(s):
    return s.encode("utf-16-le") + b"\0\0"


def replace_event(events, eid, data):
    return [(e, data if e == eid else d) for e, d in events]


def notes_event(notes):
    """notes: (tick, channel, length ticks, key, velocity 0-127). FL velocity runs 0-128."""
    out = bytearray()
    for tick, chan, length, key, vel in sorted(notes):
        out += struct.pack("<IHHIHHBBBBBBBB", tick, 0x4000, chan, max(1, length), key, 0,
                           120, 0, 64, 0, 64, min(128, round(vel * 128 / 127)), 128, 128)
    return 224, bytes(out)


def channel_block(iid, part, name, sampler, wrapper):
    events = []
    for eid, data in sampler:
        if eid == 64:
            data = u16(iid)
        elif eid == 212:
            data = wrapper                        # as saved inside a project, not a preset
        elif eid == 203:
            data = text(name)
        elif eid == 22:
            data = u8(iid + 1)                    # mixer insert
        elif eid == 196:
            data = text(f"Glasshouse {name}.wav")  # FL finds it next to the .flp or in a search folder
        elif eid == 221 and part == "808":
            data = struct.pack("<IIB", 0, 500, 1)  # Mono: each note cuts the last, no glide
        elif eid == 132 and part in ("hat", "openhat"):
            data = struct.pack("<HH", 1, 1)        # cut group 1: the closed hat chokes the open hat
        events.append((eid, data))
        if eid == 145:
            events.append((32, u8(0)))            # "locked" flag, present in project files
        if eid == 215 and ROOT[part] != 60:
            events.append((135, u32(ROOT[part])))  # sample root note
    if part in ENVELOPES:
        envs = [i for i, (e, _) in enumerate(events) if e == 218]
        i = envs[1]                                # order: pan, volume, mod X, mod Y, pitch
        v = list(struct.unpack("<17i", events[i][1]))
        e = ENVELOPES[part]
        v[1:8] = [-1, 100, e["attack"], e["hold"], e["decay"], e["sustain"], e["release"]]
        events[i] = (218, struct.pack("<17i", *v))
    return events


# ---------------------------------------------------------------------------
# Patterns and playlist
# ---------------------------------------------------------------------------

def build_arrangement(loops):
    """Patterns (name, notes) and playlist clips (bar, bars, pattern, track, start bar)."""
    patterns, clips = [], []

    def pattern(name, notes):
        for i, (n, _) in enumerate(patterns):
            if n == name:
                return i + 1
        patterns.append((name, notes))
        return len(patterns)

    def loop_notes(parts, bar=None):
        """Notes of the 8-bar loop, or of one bar of it moved to the start."""
        out = []
        for p in parts:
            for n in loops[p]:
                step = n.step
                if bar is not None:
                    if not bar * 16 <= step < (bar + 1) * 16:
                        continue
                    step -= bar * 16
                out.append((round(step * TICKS_PER_STEP), CH[p], round(n.length * TICKS_PER_STEP), n.pitch, n.vel))
        return out

    # Main loops first so they sit at the top of FL's pattern list; variations follow.
    for _, pname, parts in GROUPS:
        pattern(pname, loop_notes(parts))

    for track, (_, pname, parts) in enumerate(GROUPS):
        full = pattern(pname, None)
        for _, b0, b1, active in bb.SECTIONS:
            if not set(parts) & active:
                continue
            playing = lambda bar: [p for p in parts if p in active and p not in bb.MUTES.get(bar, set())]  # noqa: E731
            bar = b0
            while bar < b1:
                lb = (bar - b0) % bb.LOOP_BARS
                on = playing(bar)
                if len(on) == len(parts):
                    # One clip per loop pass, cut short where a muted bar interrupts it.
                    end = bar + 1
                    while end < b1 and (end - b0) % bb.LOOP_BARS and len(playing(end)) == len(parts):
                        end += 1
                    clips.append((bar, end - bar, full, track, lb))
                    bar = end
                    continue
                if on:
                    name = VARIANT_NAMES.get(frozenset(on), f"{pname} bar {lb + 1}")
                    clips.append((bar, 1, pattern(name, loop_notes(on, lb)), track, 0))
                bar += 1

    # One-off hits (build_beat.EXTRAS) go on their own track, one 1-bar pattern per sound.
    for part, bar, pitch, length, vel in bb.EXTRAS:
        name = dict(CHANNELS_BY_PART)[part]
        pat = pattern(name, [(0, CH[part], length * TICKS_PER_STEP, pitch, vel)])
        clips.append((bar, 1, pat, len(GROUPS), 0))
    return patterns, clips


def playlist_event(clips, patterns):
    out = bytearray()
    for bar, bars, pat, track, start in sorted(clips):
        full = start == 0 and bars * BAR >= pattern_length(patterns[pat - 1][1])
        offsets = (-1, -1) if full else (start * BAR, (start + bars) * BAR)
        out += struct.pack("<IHHIHH2sH4sii", bar * BAR, 20480, 20480 + pat, bars * BAR, 499 - track, 0,
                           b"x\0", 64, b"@d\x80\x80", *offsets)
    return 233, bytes(out)


def pattern_length(notes):
    end = max(t + ln for t, _, ln, _, _ in notes)
    return -(-end // BAR) * BAR


def expand(patterns, clips):
    """What the playlist plays, per part, as (tick, key, length, velocity). Used to check the build."""
    part_of = {i: p for p, i in CH.items()}
    out = {p: [] for p in CH}
    for bar, bars, pat, _, start in clips:
        for t, chan, ln, key, vel in patterns[pat - 1][1]:
            if start * BAR <= t < (start + bars) * BAR:
                out[part_of[chan]].append((bar * BAR + t - start * BAR, key, ln, vel))
    return {p: sorted(v) for p, v in out.items()}


def build_flp(patterns, clips):
    project = read_events(TEMPLATE / "project.flp")
    sampler = read_events(TEMPLATE / "sample_channel.fst")
    sampler = sampler[[e for e, _ in sampler].index(64):]
    wrapper = next(d for e, d in project if e == 212)

    first_pattern = [e for e, _ in project].index(65)
    header = project[:first_pattern]
    header = replace_event(header, 156, u32(bb.BPM * 1000))
    header = replace_event(header, 67, u16(1))
    header = replace_event(header, 194, text("Glasshouse"))
    header = replace_event(header, 206, text("Underground rap"))
    header = replace_event(header, 195, text(
        "Glasshouse: an original 140 BPM beat from the Winnie Harlow style study. "
        "Keep the Glasshouse *.wav samples in the same folder as this project."))
    controllers = [(e, d) for e, d in project if e == 226]

    events = list(header)
    for i, (_, notes) in enumerate(patterns):
        events += [(65, u16(i + 1)), notes_event(notes)]
        if i == 0:
            events += controllers
    blocks = [channel_block(i, part, name, sampler, wrapper) for i, (part, name, _) in enumerate(CHANNELS)]
    events += blocks[0]
    for i, (name, _) in enumerate(patterns):
        events += [(65, u16(i + 1)), (193, text(name))]
    for block in blocks[1:]:
        events += block

    tracks = [name for name, _, _ in GROUPS] + [FX_TRACK]
    events += [(99, u16(0)), (241, text("Arrangement")), (36, u8(0)), playlist_event(clips, patterns)]
    for i, data in enumerate(d for e, d in project if e == 238):
        events.append((238, data))
        if i < len(tracks):
            events.append((239, text(tracks[i])))

    mixer = project[[e for e, _ in project].index(100):]
    insert = 0
    for eid, data in mixer:
        if eid == 236:
            if 1 <= insert <= len(CHANNELS):
                events.append((204, text(CHANNELS[insert - 1][1])))
            insert += 1
        events.append((eid, data))

    body = encode(events)
    head = b"FLhd" + u32(6) + struct.pack("<hHH", 0, len(CHANNELS), PPQ)
    return head + b"FLdt" + u32(len(body)) + body


def main():
    loops = bb.loop_patterns()
    song = bb.arrange(loops)
    patterns, clips = build_arrangement(loops)

    got = expand(patterns, clips)
    want = {p: sorted((round(n.step * TICKS_PER_STEP), n.pitch, round(n.length * TICKS_PER_STEP), n.vel)
                      for n in song[p]) for p in CH}
    assert got == want, [p for p in CH if got[p] != want[p]]

    OUT.mkdir(exist_ok=True)
    samples = set_levels(song, render_samples())
    for part, name, _ in CHANNELS:
        sf.write(OUT / f"Glasshouse {name}.wav", samples[part], SR, subtype="PCM_24")
    (OUT / "Glasshouse.flp").write_bytes(build_flp(patterns, clips))
    print(f"wrote {OUT / 'Glasshouse.flp'}: {len(CHANNELS)} channels, {len(patterns)} patterns, "
          f"{len(clips)} playlist clips, plus {len(CHANNELS)} samples")


if __name__ == "__main__":
    main()
