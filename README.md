# Recreate the Underground

Production studies of underground rap beats. Each study measures how a reference track is built (tempo, key, tuning,
sounds, mix, arrangement) and then makes an **original** beat with the same recipe, delivered as MIDI, a rendered
preview and an FL Studio project. No audio, lyrics or melodies from the reference songs are included.

| Study | Reference | Original beat |
|---|---|---|
| [`winnie-harlow-study/`](winnie-harlow-study/) | Nettspend, "Winnie Harlow" (prod. ok): 140 BPM, dark, wide melody, distorted 808 that jumps | **Glasshouse** |
| [`fkd-it-up-study/`](fkd-it-up-study/) | OsamaSon, "Fkd It Up" (unreleased, prod. ok): 162 BPM, near-mono, clean sliding 808, filter-automated melody | **Overexposed**, with a stage-by-stage build-up |

The full research report on "Winnie Harlow" and its producer is in [`reports/`](reports/).

## Tools

| File | What it does |
|---|---|
| [`tools/analyze_reference.py`](tools/analyze_reference.py) | Measures a track you own: tempo, where bar 1 starts, key, tuning, 808 notes, drum feel and an energy map |
| [`tools/build_flp.py`](tools/build_flp.py) | Turns a study's `build_beat.py` into an FL Studio project with one sample per channel |
| [`tools/dsp.py`](tools/dsp.py) | Shared synthesis, MIDI and mastering helpers |
| [`tools/fl_template/`](tools/fl_template/) | The FL-saved files the project builder copies from |
