#!/usr/bin/env python3
"""Remake kit for OsamaSon's "Fkd It Up" (prod. ok): an empty FL Studio project set up with
the tempo, tuning, sounds and channel settings measured from the song (see ANALYSIS.md).
There are no notes in it. You add those by ear (see REMAKE_IT_YOURSELF.md).

Build:
  python3 ../tools/build_flp.py remake_kit.py   # -> remake_kit/Fkd It Up Remake Kit.flp + samples
"""
from build_beat import (HAT, IR, OPEN_HAT, SR, clap, fade_out, kick, one_808, padded, reverb,  # noqa: F401
                        snare, swell, thin)

BPM = 162
NAME = "Fkd It Up Remake Kit"


def samples():
    """Sounds built to the measured targets: clean sub-heavy 808 (harmonics -26/-21/-31/-25 dB),
    54 Hz kick, bright short snare and hats, and the swelling synth open and filtered."""
    synth = swell(72, 4.0, 127)
    return {
        "kick": kick(127),
        "808": fade_out(one_808(36)),
        "snare": snare(127),
        "clap": clap(127),
        "hat": HAT,
        "openhat": OPEN_HAT,
        "synth": fade_out(reverb(padded(synth, 0.8), 0.2, IR)),
        "synth_filtered": fade_out(reverb(padded(thin(synth), 0.8), 0.2, IR)),
    }


FL_PROJECT = dict(
    kit=True,
    out_dir="remake_kit",
    name=NAME,
    genre="Rage",
    comment=("Empty remake kit for Fkd It Up: 162 BPM (snare on beat 3), master pitch +35 cents, "
             "D major / B minor. Drop your WAV on the Reference track at bar 1 and slide it ~0.1 s left. "
             "Fill in the notes by ear (REMAKE_IT_YOURSELF.md)."),
    channels=[("kick", "Kick", 60), ("808", "808", 36), ("snare", "Snare", 60), ("clap", "Clap", 60),
              ("hat", "Hat", 60), ("openhat", "Open Hat", 60), ("synth", "Synth", 72),
              ("synth_filtered", "Synth (filtered)", 72)],
    groups=[
        ("Reference (drop your WAV here)", None, []),
        ("Drums", "Drums", ["kick", "snare", "clap", "hat", "openhat"]),
        ("808", "808", ["808"]),
        ("Synth (808 out)", "Synth", ["synth"]),
        ("Synth (808 in)", "Synth (filtered)", ["synth_filtered"]),
    ],
    envelopes={
        "808": dict(attack=100, hold=100, decay=30000, sustain=128, release=12000),
        "synth": dict(attack=100, hold=100, decay=30000, sustain=128, release=16000),
        "synth_filtered": dict(attack=100, hold=100, decay=30000, sustain=128, release=16000),
    },
    mono={"808"},
    porta={"808"},             # about half the song's 808 moves slide; turn Porta off for slide notes
    slide=250,
    cut_group={"hat", "openhat"},
    master_pitch=35,           # the song is 35 cents sharp
    # Where the song changes, in its own 4-bar blocks (1-based bars at 162 BPM).
    markers=[(1, "Beat in"), (5, "808 out"), (9, "808 back"), (17, "808 + drums out"), (21, "All back"),
             (35, "Melody out"), (41, "Melody back"), (45, "808 out"), (49, "808 back"), (53, "808 out"),
             (57, "808 back"), (65, "808 + drums out"), (69, "All back"), (83, "Melody out"),
             (89, "Melody back"), (93, "Outro: 808 fades, drums thin out"), (105, "End")],
    levels={"kick": -10, "808": -2, "snare": -9, "clap": -13, "hat": -12, "openhat": -14,
            "synth": -16, "synth_filtered": -22},
    samples=samples,
)
