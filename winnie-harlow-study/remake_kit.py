#!/usr/bin/env python3
"""Remake kit for Nettspend's "Winnie Harlow": an empty FL Studio project set up with the
tempo, tuning, sounds and channel settings measured from the song (see ANALYSIS.md).
There are no notes in it. You add those by ear (see REMAKE_IT_YOURSELF.md).

Build:
  python3 ../tools/build_flp.py remake_kit.py   # -> remake_kit/Winnie Harlow Remake Kit.flp + samples
"""
from build_beat import (HAT, OPEN_HAT, SR, clap, fade_out, filt, kick, one_808, pad_note,  # noqa: F401
                        padded, reverb)

BPM = 140.10               # line up with the file over the whole song
NAME = "Winnie Harlow Remake Kit"


def samples():
    """Sounds built to the measured targets: dark short kick, saturated flat 808 (harmonics
    -15/-6/-16/-28 dB), dry three-burst clap, short dark hats, soft wide chord synth."""
    melody = filt(pad_note(60, 6.0, 127), "lowpass", 4000)
    return {
        "kick": kick(127),
        "808": fade_out(one_808(36)),
        "clap": clap(127),
        "hat": HAT,
        "openhat": OPEN_HAT,
        "melody": fade_out(reverb(padded(melody, 0.8), 0.35)),
    }


FL_PROJECT = dict(
    kit=True,
    out_dir="remake_kit",
    name=NAME,
    genre="Underground rap",
    comment=("Empty remake kit for Winnie Harlow: 140.10 BPM, master pitch +15 cents, G# minor. "
             "Drop your WAV on the Reference track at bar 2 and slide it 0.375 s left. "
             "Fill in the notes by ear (REMAKE_IT_YOURSELF.md)."),
    channels=[("kick", "Kick", 60), ("808", "808", 36), ("clap", "Clap", 60), ("hat", "Hat", 60),
              ("openhat", "Open Hat", 60), ("melody", "Melody", 60)],
    groups=[
        ("Reference (drop your WAV here)", None, []),
        ("Drums", "Drums", ["kick", "clap", "hat", "openhat"]),
        ("808", "808", ["808"]),
        ("Melody", "Melody", ["melody"]),
    ],
    envelopes={
        "808": dict(attack=100, hold=100, decay=30000, sustain=128, release=12000),
        "melody": dict(attack=100, hold=100, decay=30000, sustain=128, release=30000),
    },
    mono={"808"},              # the song's 808 jumps between notes: Mono on, Porta off
    porta=set(),
    cut_group={"hat", "openhat"},
    master_pitch=15,           # the song is 15 cents sharp
    # The beat is one 4-bar loop that never changes; these mark the vocal's changes so
    # you can find your place against the reference.
    markers=[(1, "Beat in: one 4-bar loop, x20"), (41, "Vocal gets louder"), (51, "Vocal gap"),
             (55, "Vocal gap"), (74, "Instrumental outro"), (81, "Hard cut")],
    levels={"kick": -3, "808": -3, "clap": -9, "hat": -18, "openhat": -20, "melody": -14},
    samples=samples,
)
