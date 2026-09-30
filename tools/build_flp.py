#!/usr/bin/env python3
"""Build a beat script's song as an FL Studio project, plus one sample per channel.

  python3 tools/build_flp.py winnie-harlow-study/build_beat.py
  -> winnie-harlow-study/fl_project/<Name>.flp and <Name> <channel>.wav

The beat script supplies the notes (loop_patterns, arrange, SECTIONS, MUTES, EXTRAS,
LOOP_BARS, SONG_BARS, BPM, STEP, SR, MIX, rms_db) and an FL_PROJECT dict describing the
project: name, genre, comment, channels [(part, channel name, sample root note)], playlist
groups [(track, pattern, parts)], fx_track, variants, envelopes, mono/porta/cut_group
parts, mix_bus and a samples() function returning one audio array per part. Every channel
is a Sampler loaded with that part's sample, so the project needs no third-party plugins.

FL Studio's .flp format has no public spec. This file writes it by copying events
out of two files FL Studio 20.8.4 saved itself (fl_template/) and filling in the
channels, patterns, playlist and mixer names. Event IDs and layouts follow PyFLP
(https://github.com/demberto/PyFLP).

Usage:
  pip install numpy scipy soundfile mido pyloudnorm
  python3 tools/build_flp.py <study>/build_beat.py
"""
import importlib.util
import struct
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

TEMPLATE = Path(__file__).resolve().parent / "fl_template"
PPQ = 96
TICKS_PER_STEP = PPQ // 4
BAR = 16 * TICKS_PER_STEP


def configure(beat_path):
    """Load the beat script and expose its FL_PROJECT settings as this module's globals."""
    global bb, FL, SR, OUT, CHANNELS, CH, CHANNELS_BY_PART, ROOT, MIX_BUS, GROUPS, FX_TRACK
    global VARIANT_NAMES, ENVELOPES, CUT_PARTS
    beat_path = Path(beat_path).resolve()
    sys.path.insert(0, str(beat_path.parent))
    spec = importlib.util.spec_from_file_location(beat_path.stem, beat_path)
    bb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bb)
    FL = bb.FL_PROJECT
    SR = bb.SR
    OUT = beat_path.parent / "fl_project"
    CHANNELS = FL["channels"]
    CH = {part: i for i, (part, _, _) in enumerate(CHANNELS)}
    CHANNELS_BY_PART = [(part, name) for part, name, _ in CHANNELS]
    ROOT = {part: root for part, _, root in CHANNELS}
    MIX_BUS = FL.get("mix_bus", {})
    GROUPS = FL["groups"]
    FX_TRACK = FL.get("fx_track", "FX")
    VARIANT_NAMES = FL.get("variants", {})
    # Sampler volume envelope for parts whose sound must stop when the note ends.
    # Without it FL's Sampler plays the whole sample regardless of note length.
    # Values are FL's raw knob values: times 100-65536, sustain 0-128.
    ENVELOPES = FL.get("envelopes", {})
    CUT_PARTS = set(FL.get("mono", ())) | set(FL.get("cut_group", ()))


def stereo(x):
    return np.stack([x, x], axis=1) if x.ndim == 1 else x


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
            if part in CUT_PARTS and k + 1 < len(notes):
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
            data = text(f"{FL['name']} {name}.wav")  # FL finds it next to the .flp or in a search folder
        elif eid == 221 and part in FL.get("mono", ()):
            # Mono: each note cuts the last. Porta adds FL's glide between overlapping notes.
            data = struct.pack("<IIB", 0, FL.get("slide", 500), 1 | (2 if part in FL.get("porta", ()) else 0))
        elif eid == 132 and part in FL.get("cut_group", ()):
            data = struct.pack("<HH", 1, 1)        # cut group 1: e.g. the closed hat chokes the open hat
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
    header = replace_event(header, 156, u32(round(bb.BPM * 1000)))
    header = replace_event(header, 67, u16(1))
    header = replace_event(header, 194, text(FL["name"]))
    header = replace_event(header, 206, text(FL["genre"]))
    header = replace_event(header, 195, text(FL["comment"]))
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

    tracks = [name for name, _, _ in GROUPS] + ([FX_TRACK] if bb.EXTRAS else [])
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
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    configure(sys.argv[1])
    loops = bb.loop_patterns()
    song = bb.arrange(loops)
    patterns, clips = build_arrangement(loops)

    got = expand(patterns, clips)
    want = {p: sorted((round(n.step * TICKS_PER_STEP), n.pitch, round(n.length * TICKS_PER_STEP), n.vel)
                      for n in song[p]) for p in CH}
    assert got == want, [p for p in CH if got[p] != want[p]]

    OUT.mkdir(exist_ok=True)
    samples = set_levels(song, FL["samples"]())
    for part, name, _ in CHANNELS:
        sf.write(OUT / f"{FL['name']} {name}.wav", samples[part], SR, subtype="PCM_24")
    flp = OUT / f"{FL['name']}.flp"
    flp.write_bytes(build_flp(patterns, clips))
    print(f"wrote {flp}: {len(CHANNELS)} channels, {len(patterns)} patterns, "
          f"{len(clips)} playlist clips, plus {len(CHANNELS)} samples")


if __name__ == "__main__":
    main()
