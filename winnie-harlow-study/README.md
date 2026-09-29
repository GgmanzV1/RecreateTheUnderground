# Winnie Harlow study → "Glasshouse"

A breakdown of how Nettspend's "Winnie Harlow" is built (tempo, key, feel, mix,
arrangement), plus **Glasshouse**, an original FL-ready beat made on the same
framework. The chords, melody and drums are new. Nothing from the song itself
(audio, lyrics, melodies) is in this folder.

| File | What it is |
|---|---|
| [`ANALYSIS.md`](ANALYSIS.md) | The research: 140 BPM half-time, G# minor, +15 cents, dark sub-first mix, loop arrangement, and how to check it yourself in FL |
| [`FL_GUIDE.md`](FL_GUIDE.md) | Step by step: sounds, plugin settings, glides, hat rolls, sidechain, arrangement, mix |
| `audio/glasshouse_preview.mp3` | Rendered preview of the target sound (1:53) |
| `midi/loops/*.mid` | One 8-bar loop per part, drag into FL's piano roll |
| `midi/glasshouse_arrangement.mid` | All parts over the full 64 bars (File → Import → MIDI file) |
| `build_beat.py` | Generates the MIDI and preview. Edit `CHORDS`, `LEAD_NOTES`, patterns or `MIX` and re-run |
| `analyze_reference.py` | Measures tempo, feel, key, 808 notes, tuning and arrangement of any track you own |

## Quick start

```bash
pip install numpy scipy soundfile mido librosa
python3 build_beat.py --wav                 # rebuild MIDI + preview (WAV too)
python3 analyze_reference.py some_song.wav  # study another reference
```
