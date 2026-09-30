# How Overexposed is made, one layer at a time

Overexposed is an original beat built with the recipe measured from "Fkd It Up" (see [`ANALYSIS.md`](ANALYSIS.md)).
Its chords, melody, drums and 808 line are its own. The point is to show *how this kind of beat is put together*.

Every step has an audio file in `audio/stages/`, so you can hear what each layer adds. Clips 01 and 03–07 are the
first 8 bars of the hook (about 12 seconds). Clip 02 is the synth's first 4 hook bars played twice (open, then
filtered), and clip 08 is 12 bars of the full song. Listen in order.

| File | What you hear |
|---|---|
| `01_synth_dry.mp3` | The synth alone, straight out of the oscillators |
| `02_synth_filter_trick.mp3` | 4 bars of the synth *open* (as in the breakdowns), then 4 bars *filtered* (as when the 808 plays) |
| `03_drums.mp3` | Drums alone |
| `04_808_no_slides.mp3` | The 808 line with every note jumping |
| `05_808_with_slides.mp3` | The same line with half the pitch changes sliding |
| `06_all_parts_unmastered.mp3` | Everything together, before the master chain |
| `07_all_parts_mastered.mp3` | The same, soft-clipped and limited to −9.3 LUFS |
| `08_hook_breakdown_verse.mp3` | The end of the hook, the breakdown (808 and drums gone, synth opens up) and the verse coming in |

Setup in FL: **162 BPM**, 4/4. Everything below uses FL's stock plugins plus the free synth [Vital](https://vital.audio).
The ready-made project is in `fl_project/` (see the end of this page).

## 1. The synth (stage 01)

One synth plays both the chords and the top line, like the reference's single melodic layer.

- **Oscillators:** three saws detuned −8, 0 and +8 cents (Vital: one saw with 3 unison voices, detune small).
  Low-pass the result around **3.5 kHz**.
- **The swell:** amp envelope attack **~130 ms**, sustain full, release ~80–250 ms. That slow attack is what makes each
  note "bloom" instead of plucking. It's the most recognisable part of the sound.
- **Keep it mono.** The three voices are spread only slightly between left and right. The reference's melody is nearly
  mono, and so is everything else in the mix.
- **Notes:** `midi/loops/07_keys.mid`. A 4-bar loop in B minor: one sustained chord per bar
  (Bm7 → Gmaj7 → D/F# → A) under a top line of straight 8th notes, about five notes a bar.
- **Space:** a short room (Fruity Reeverb 2, decay ~0.5 s, mix ~20%).

## 2. The filter trick (stage 02)

This is the most useful thing to learn from "Fkd It Up". The synth isn't the same in every section:

- **When the 808 plays**, the synth drops ~6 dB, loses its low mids (a **−10 dB low shelf under ~500 Hz**), and gets a
  slight top lift (+4 dB above 5 kHz). It gets out of the 808's way.
- **When the 808 drops out** (intro, breakdown, the 808-drop section, outro), the full synth comes back, so the
  breakdown feels bigger even though nothing new plays.

How to do it in FL, either way:

1. **Automation (the usual way):** put **Parametric EQ 2** on the synth's mixer track with band 1 as a low shelf at
   500 Hz. Right-click its gain → *Create automation clip*, then draw it down to −10 dB wherever the 808 plays and back
   to 0 dB wherever it doesn't. Do the same with the mixer fader for the ~6 dB drop.
2. **Two channels (what the ready-made project does):** clone the synth channel, put the EQ and the lower level on the
   clone ("Swell (filtered)"), and use the original ("Swell (open)") in the sections without the 808. It's easier to see
   in the playlist.

## 3. Drums (stage 03)

- **Grid:** straight **8th notes** only. No 16ths, no triplets, no rolls. At 162 BPM, 8th-note hats already move fast.
- **Hats:** every 8th, loud on the beat and softer off it. One open hat at the end of the loop, choked by the closed
  hat (same **Cut / Cut by** group in the channel's Misc tab). Very short (~27 ms decay), bright, but not fizzy above
  10 kHz.
- **Snare + clap:** both on **beat 3** of every bar (half-time). Snare strongest near 1.1 kHz, gone in ~50 ms.
  One ghost snare at the end of the loop.
- **Kick:** on 8th positions, never on beat 3, about four a bar. A 54 Hz body with a short pitch drop.
- **Balance:** in this style the drums are **top-heavy**. The hats and snare carry them, and the kick sits lower than
  you'd expect. The 808 does the low end.
- Files: `01_kick.mid`, `03_snare.mid`, `04_clap.mid`, `05_hat.mid`, `06_openhat.mid`.

## 4. The 808 (stages 04 and 05)

- **Sound:** clean and sub-heavy. Harmonics sit 21–36 dB under the fundamental, so it's mostly a pure sine, with a faint
  layer of upper overtones so it isn't lost on small speakers. No heavy distortion (that's the opposite of "Winnie
  Harlow"). **Flat sustain.** It should hold its level for as long as the note is held.
- **Register:** the notes sit between E1 and D2 (41–73 Hz). Keep it there. Higher 808 notes pile up energy in the
  80–160 Hz range that this style keeps clear.
- **Slides:** about half of the pitch changes slide, 3–5 semitones over one 16th (~90 ms). Compare stages 04 and 05:
  that bend is what makes the 808 feel alive.
- **In FL:** channel settings → Misc → turn on **Mono** and **Porta**, and keep **Slide** short. Porta glides into
  *every* new pitch. To slide only some notes like the MIDI does, turn Porta off and draw **slide notes** (the
  triangle notes in the piano roll) where you want the bend.
- **Gaps:** leave short gaps (a 16th or two each bar). The 808 should sound about 85–90% of the time, not wall to wall.
  Enable the volume envelope (INS tab: sustain full, short release) so notes stop when they end.
- File: `02_808.mid`.

## 5. Mix (stage 06)

- **Levels, loudest to quietest:** 808 → drums (~7 LU under the 808) → synth (~4 LU under the drums). The 808 is by far
  the loudest element. The synth is quiet on purpose.
- **Stereo:** keep everything **near mono**. Check with FL's stereo tools or by flipping the master to mono: almost
  nothing should change.
- **Tonal target:** most of the energy in 40–80 Hz, then a clear dip from 80 to 320 Hz. Put Parametric EQ 2 on the master
  and compare the spectrum against the song with its master pitch raised 35 cents.

## 6. Master (stage 07)

**Fruity Soft Clipper → Fruity Limiter** (ceiling −1 dB). Push until the master reads about **−9.3 LUFS** on a loudness
meter (Youlean Loudness Meter is free). The reference is limited rather than hard-clipped, so if the 808 starts to buzz,
back off the clipper and let the limiter do more.

## 7. Arrangement (stage 08 and the full preview)

Everything changes in **4-bar blocks**. This is the 64-bar layout, as FL numbers the bars:

| Bars | Section | What plays |
|---|---|---|
| 1–4 | Intro | Synth (open) alone |
| 5–20 | Hook | Everything, synth filtered |
| 21–24 | Breakdown | Synth (open) alone: 808 and drums out |
| 25–40 | Verse | Drums, 808, synth filtered; the synth drops out for bars 33–36 |
| 41–44 | 808 drop | Drums and synth (open), no 808 |
| 45–60 | Hook | Everything, synth filtered |
| 61–64 | Outro | Synth (open) alone |

Those are the reference's three moves: **808 drops**, **808 + drum drops**, and a **melody drop** inside a section.
Every time the 808 leaves, the synth opens up to fill the space.

## The ready-made FL project

`fl_project/` has **`Overexposed.flp`** plus one WAV per channel, built by [`../tools/build_flp.py`](../tools/build_flp.py):

1. Download the whole `fl_project` folder and keep the WAVs next to the `.flp`.
2. In FL: **Options → File settings → Browser extra search folders**, add that folder (once).
3. Open `Overexposed.flp`. If a channel comes up empty, drag its WAV onto it.

Inside: Kick, 808 (Mono + Porta), Snare, Clap, Hat and Open Hat (cut group), **Swell (filtered)** and **Swell (open)**,
each routed to its own named mixer insert. Patterns: Drums, 808, Swell (filtered), Swell (open). The playlist has the
whole 64-bar layout above. The master chain isn't included, so it plays quieter than the preview until you add it
(section 6). Built for FL Studio 20.8 or newer and checked with an independent parser, but not opened in FL itself.
