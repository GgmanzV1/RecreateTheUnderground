# Winnie Harlow study → "Glasshouse"

A breakdown of how Nettspend's "Winnie Harlow" (produced by ok) is built, plus **Glasshouse**, an original
FL-ready beat whose sound and mix are built to the targets measured from it. The chords, melody and drums are
new. Nothing from the song itself (audio, lyrics, melodies) is in this folder.

The full research (credits, release history, ok's toolkit, the style's playbook, every measured target) is in
[`../reports/Winnie Harlow production study.md`](../reports/Winnie%20Harlow%20production%20study.md).

| File | What it is |
|---|---|
| [`ANALYSIS.md`](ANALYSIS.md) | The short version: tempo, key, tuning, loudness, stereo, what each sound measures as, the arrangement, and how Glasshouse compares |
| [`REMAKE_IT_YOURSELF.md`](REMAKE_IT_YOURSELF.md) | How to remake the song by ear in FL, one layer at a time: stem separation, finding 808 notes on the spectrum, Basic Pitch for melody drafts, A/B testing, with the measured numbers as checkpoints |
| `remake_kit/Winnie Harlow Remake Kit.flp` | **Empty remake kit**: the song's tempo, +15-cent tuning, matched sounds, 808 settings and markers, ready for your notes. Built by `remake_kit.py` |
| [`FL_GUIDE.md`](FL_GUIDE.md) | Step by step: sounds, plugin settings, glides, hat rolls, sidechain, arrangement, mix |
| `fl_project/Glasshouse.flp` | **The FL Studio project**: all channels, patterns and the full arrangement, with its samples next to it. Setup is in [`FL_GUIDE.md`](FL_GUIDE.md#shortcut-open-the-ready-made-project) |
| `audio/glasshouse_preview.mp3` | Rendered, mastered preview (1:38) |
| `midi/loops/*.mid` | One 8-bar loop per part, drag into FL's piano roll |
| `midi/glasshouse_arrangement.mid` | All parts over the full 64 bars (File → Import → MIDI file) |
| `build_beat.py` | Generates the MIDI and preview. Edit `CHORDS`, `LEAD_NOTES`, patterns or `MIX` and re-run |
| [`../tools/build_flp.py`](../tools/build_flp.py) | Generates the FL project and its samples from `build_beat.py` (its `FL_PROJECT` settings). Shared by every study |
| [`../tools/analyze_reference.py`](../tools/analyze_reference.py) | Measures tempo, feel, key, 808 notes, tuning, where bar 1 starts, and arrangement of any track you own |

## Quick start

```bash
pip install numpy scipy soundfile mido librosa pyloudnorm
python3 build_beat.py --wav                 # rebuild MIDI + preview (WAV too)
python3 ../tools/build_flp.py build_beat.py           # rebuild the FL project + samples
python3 ../tools/analyze_reference.py some_song.wav   # study another reference
```
