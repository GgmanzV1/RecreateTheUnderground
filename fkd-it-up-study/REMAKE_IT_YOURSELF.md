# Remake "Fkd It Up" yourself in FL Studio

Overexposed uses the song's recipe with its own notes, so it won't sound like "Fkd It Up". To get the song's own
notes, you pull them out by ear. This guide is that workflow, with the numbers measured from your WAV as
checkpoints. Nothing here gives you the notes themselves. The checkpoints tell you when you're close.

**Order:** set up → line up the grid → split stems → 808 → melody → drums → sounds → A/B.
This song is built on the 808, so start there, not with the drums.

## Start from the remake kit

`remake_kit/Fkd It Up Remake Kit.flp` is an empty FL project with everything except the notes already set:

- **162 BPM** and FL's **master pitch at +35 cents**, so your notes line up with the song in time and in tune.
- Channels with sounds built to the song's measured targets: Kick, **808** (clean, Mono + Porta with a short slide),
  Snare, Clap, Hat and Open Hat (cut group), **Synth** (the open, swelling version) and **Synth (filtered)** (the
  thinner version for wherever the 808 plays). Each has its own named mixer insert.
- Empty patterns named **Drums**, **808**, **Synth** and **Synth (filtered)**, and a **Reference** track at the top.
- **17 playlist markers** at every change the song makes: each 808 drop, each 808 + drum drop, each melody drop and
  the outro. Use them to lay out your patterns once one 4-bar loop is right.

To use it: keep the WAVs next to the `.flp`, add the folder under **Options → File settings → Browser extra search
folders**, open the project, drag your copy of the song onto the Reference track and slide it about 0.1 s left.
Then work through the steps and draw your notes into the empty patterns. Put the melody in **Synth** where a marker
says the 808 is out, and in **Synth (filtered)** where it's in.

## What you need

- FL Studio **Producer Edition or higher** for built-in stem separation.
- Your WAV of the song.
- Optional: [Basic Pitch](https://engineering.atspotify.com/2022/6/meet-basic-pitch), Spotify's free
  audio-to-MIDI tool, for a rough first draft of the melody.

## 1. Project setup

- Tempo **162**. Most BPM finders say 81. That's half, because the snare only hits once a bar.
- The whole song is tuned **+35 cents** sharp: the 808, the melody and the vocal all agree. Turn FL's **master pitch**
  up 35 cents while you work, or every note you find will sound sour. This is the most common reason a remake of this
  song "sounds off".
- Key: **D major / B minor**. Scale: **D E F# G A B C#**. If a note sounds almost right but wrong, check C vs **C#**
  and F vs **F#**.

## 2. Line up the grid

Bar 1 starts about **0.1 s** into the file. Drag the WAV into the Playlist at bar 2, then Alt-drag it left about a
16th until the first hit sits on the bar line. With the metronome on, the snare should land on **beat 3 of every bar**.

## 3. Split it into stems

Clip menu → **Sample** → **Extract stems from sample** (drums, bass, instruments, vocals). Mute the vocals. Loop
**4 bars**: the whole beat repeats every 4 bars, so once one loop is right, most of the song is done.

To slow it down, open the clip's channel settings, pick an Elastique time-stretch mode and turn **TIME** up.

## 4. The 808 (do this first)

- Solo the **bass** stem and put Parametric EQ 2 on it. Read the tallest peak on the left. With the song's +35-cent
  tuning, the notes it uses sit at:

  | Note (FL name) | Low octave | One octave up |
  |---|---|---|
  | E  (E2 in FL) | 42.0 Hz | 84.1 Hz |
  | F# (F#2 in FL) | 47.2 Hz | 94.4 Hz |
  | G  (G2 in FL) | 50.0 Hz | 100.0 Hz |
  | A  (A2 in FL) | 56.1 Hz | 112.2 Hz |
  | B  (B2 in FL) | 63.0 Hz | 126.0 Hz |
  | D  (D3 in FL) | 74.9 Hz | 149.8 Hz |

- Checkpoint: across the song the 808 spends roughly **20% on E, 18% on G, 14% on A, 13% on F#, 13% on D**. If your
  loop has a lot of notes outside those five, recheck them.
- **Slides:** about **half** of the bigger pitch moves slide, usually 3–4 semitones over ~100 ms; the rest jump.
  Listen to each change: does the pitch bend into the new note, or snap? Use **slide notes** in the piano roll for the
  ones that bend (Porta would bend all of them).
- **Rhythm and length:** the 808 sounds about **86%** of the time: long notes with short gaps. Get the gaps right.
  They are most of the groove. Most starts fall on 8th-note positions.
- A clean 808 (a sine with a little saturation) matches the tone. Don't reach for a distorted one.

## 5. The melody

- Solo the **instruments** stem and loop 4 bars. Hum the top line until you can sing it without the track.
- Checkpoint: the melody leans on **D, F# and A**, then E and G. It's one layer playing chords and a top line together,
  roughly between F#2 and F#6.
- Find the top line first, one note at a time, on the piano roll keyboard, using only the scale above. Then find the
  chord under it: hold D, G, A, Bm and Em triads underneath and keep the one that sounds settled.
- **Basic Pitch shortcut:** export one 4-bar loop of the instruments stem from a **breakdown** (where the 808 is out,
  so the melody is loudest and cleanest), run it through Basic Pitch, and fix every note by ear. The stem is quieter
  and thinner wherever the 808 plays, so those parts are harder to transcribe.
- **Sound:** a clean, detuned-saw-type synth with a **slow ~130 ms swell** on each note, nearly mono. HOW_ITS_MADE.md
  step 1 shows how to build that sound.

## 6. Drums

- Solo the **drums** stem.
- Checkpoint: everything sits on **straight 8th notes**: no 16ths, no triplets, no rolls. If you're drawing 16ths,
  something's off.
- Snare (with a clap) on **beat 3**. Kick on 8th positions, never beat 3. Hats on the 8ths, short and bright.
- Count out loud "1 & 2 & 3 & 4 &" with piano-roll snap at **1/2 beat**, and put each hit where you hear it.

## 7. Arrangement

The loop repeats in **4-bar blocks**. Mark each block in the Playlist, then listen for what drops out:
the 808 alone, the 808 **and** the drums, or the melody. [`ANALYSIS.md`](ANALYSIS.md#arrangement-4-bar-blocks-and-drop-outs)
lists where each move happens. Remember the **filter trick**: wherever the 808 plays, turn the melody down ~6 dB and
cut its low mids.

## 8. The A/B test

1. Put the original on one track and your remake on another at **equal loudness**.
2. Flip between them every 4 bars, **layer by layer**: bass stem vs your 808, instruments stem vs your melody, drums
   stem vs your drums. Fix the one furthest off, then repeat.
3. When your 808 and melody match with the master pitch at +35 cents, you've got it.

## Checkpoint summary

| Thing | Target |
|---|---|
| Tempo | 162 BPM, snare on beat 3 |
| Bar 1 | ~0.1 s into the file |
| Tuning | +35 cents |
| Key / scale | D major / B minor: D E F# G A B C# |
| 808 notes | E, G, A, F#, D; about half the moves slide |
| Melody | Leans on D, F#, A; 4-bar loop; slow swell |
| Drums | Straight 8ths, no rolls |
| Mix | −9.3 LUFS, almost mono, 808 by far the loudest |

Stuck? `python3 tools/analyze_reference.py` (from the repo root) on the original and on a bounce of your remake shows
where they differ in tempo, key, tuning and 808 notes.
