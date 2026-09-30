# Fkd It Up study → "Overexposed"

A breakdown of how OsamaSon's unreleased "Fkd It Up" (produced by ok) is built, plus **Overexposed**, an original
FL-ready beat made with the same recipe and built up one layer at a time so you can hear how it's made.
The chords, melody, drums and 808 line are new. Nothing from the song itself (audio, lyrics, melodies) is in this folder.

| File | What it is |
|---|---|
| [`ANALYSIS.md`](ANALYSIS.md) | The measurements: 162 BPM with the snare on 3, D major / B minor, +35 cents, a clean sliding 808, straight-8th drums, the melody's filter trick, the 4-bar-block arrangement, and how Overexposed compares |
| [`REMAKE_IT_YOURSELF.md`](REMAKE_IT_YOURSELF.md) | How to pull the song's own notes out by ear in FL: tuning to +35 cents, reading the 808 off the spectrum, transcribing the melody from a breakdown, with measured checkpoints |
| [`HOW_ITS_MADE.md`](HOW_ITS_MADE.md) | **Start here.** Each layer of Overexposed with its sound, settings and FL steps, next to an audio file of that stage |
| `audio/stages/*.mp3` | The build-up: dry synth → filter trick → drums → 808 without and with slides → full mix → mastered → hook into breakdown |
| `audio/overexposed_preview.mp3` | The finished, mastered beat (1:37) |
| `fl_project/Overexposed.flp` | The FL Studio project with one sample per channel. Setup is at the end of `HOW_ITS_MADE.md` |
| `midi/loops/*.mid` | One 4-bar loop per part, drag into FL's piano roll |
| `midi/overexposed_arrangement.mid` | All parts over the full 64 bars (File → Import → MIDI file) |
| `build_beat.py` | Generates the MIDI, preview and stages. Edit `CHORDS`, `MELODY`, `BASS`, `KICKS` or `MIX` and re-run |

## Quick start

```bash
pip install numpy scipy soundfile mido librosa pyloudnorm
python3 build_beat.py                               # MIDI, preview, stages
python3 ../tools/build_flp.py build_beat.py         # the FL project + samples
python3 ../tools/analyze_reference.py some_song.wav # study another reference
```
