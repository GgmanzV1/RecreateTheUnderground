# Remake "Winnie Harlow" yourself in FL Studio

This folder doesn't have a note-for-note copy of the song's parts. This guide is the
next best thing: a workflow for pulling the beat apart by ear in FL, one layer at a time,
with the numbers measured from your WAV as checkpoints. Remaking by ear is the skill that
makes the next remake faster. Your first one will be slow, and that's normal.

**Order:** set up → line up the grid → split stems → snare → kick → 808 → melody → hats → sounds → A/B.
Don't skip ahead. Every layer is easier once the one before it is locked.

## Start from the remake kit

`remake_kit/Winnie Harlow Remake Kit.flp` is an empty FL project with everything except the notes already set:

- **140.10 BPM** and FL's **master pitch at +15 cents**, so your notes line up with the song in time and in tune.
- Channels with sounds built to the song's measured targets: Kick, **808** (flat, saturated, Mono on, Porta off),
  Clap, Hat and Open Hat (cut group), and **Melody** (a soft, wide chord synth). Each has its own named mixer insert.
- Empty patterns named **Drums**, **808** and **Melody**, and a **Reference** track at the top of the playlist.
- Playlist markers where the song changes (it's one 4-bar loop; the markers follow the vocal).

To use it: keep the WAVs next to the `.flp`, add the folder under **Options → File settings → Browser extra search
folders**, open the project, drag your copy of the song onto the Reference track at bar 2 and slide it 0.375 s left
(step 2 below). Then work through the steps and draw your notes into the empty patterns.

## What you need

- FL Studio **Producer Edition or higher** for built-in stem separation. On Fruity Edition, use the
  EQ-soloing trick in [`ANALYSIS.md`](ANALYSIS.md#check-it-yourself-in-fl-this-is-the-skill-to-practise) instead.
- Your WAV of the song.
- Optional: [Basic Pitch](https://engineering.atspotify.com/2022/6/meet-basic-pitch), Spotify's free
  audio-to-MIDI tool. It runs in your browser and gives you a rough first draft of a melody.

## 1. Project setup

- Tempo **140.10**. That extra 0.1 matters when you line your remake up against the file: at 140.00 the song drifts
  almost a 16th note out by the end. (Chordify's 136 is wrong; at 136 nothing lines up after a few bars.)
- The song is tuned **+15 cents** sharp. While you're comparing, turn FL's **master pitch** up 15 cents
  so your instruments match it. Otherwise every note you find will sound slightly off.
- Key: **G# minor**. Scale: **G# A# B C# D# E F#**. If a melody note sounds almost right but sour, you
  probably have A where it should be **A#**.

## 2. Line up the grid

The first downbeat is **0.375 s** into the file, about **3.5 sixteenth-notes** in. Everything before it is silence.

1. Drag the WAV into the Playlist and start it at **bar 2**.
2. Hold **Alt** (turns off snap) and drag the clip left about 3.5 steps, until the first sound sits on the bar 2 line.
3. Turn on the metronome and play. The **snare should hit on beat 3 of every bar**. If it lands on 1, you're
   half a bar off. If it drifts, check the tempo is exactly 140.10.

## 3. Split it into stems

Clip menu (top-left corner of the audio clip) → **Sample** → **Extract stems from sample**. Tick drums,
bass, instruments and vocals. It takes about a minute per minute of audio and downloads a free model the
first time.

You'll get four tracks. **Mute the vocals.** You're remaking the beat, and the vocals will pull your ear.
Stems aren't perfect: some hat or snare bleeds into "instruments". Use your ears, not the waveform.

**Loop a small piece.** Select **2 or 4 bars** in the Playlist timeline so only that piece repeats.
Work on one loop until it's right, then check whether the next loop is the same (in this song it mostly is).

**Slow it down** when it's too fast to hear: double-click the clip to open its channel settings, set the
time-stretch **Mode** to an Elastique option, and turn **TIME** up to double the length. Remember to put it back.

## 4. Snare + clap (easiest, do it first)

- Solo the **drums** stem.
- Checkpoint: **one clap per bar, on beat 3, in every bar of the song** (half-time). It's dry: three quick
  bursts and gone in under a tenth of a second, no reverb tail.
- Match its tone before anything else: bright but not fizzy (strongest around 1.3 kHz), nothing boomy under 600 Hz.

## 5. Kick

- Low-pass the drums stem around **120 Hz** (Fruity Parametric EQ 2) so you hear only the kick.
- Program it in the piano roll with snap at **1 step**. Count out loud "1 e & a 2 e & a…".
- Checkpoint: the analyzer's average over the whole song has the kick mostly on these steps
  (`X` strong, `x` medium). Fills blur into the average, so your loop won't match it exactly:

  ```
           1 . . . 2 . . . 3 . . . 4 . . .
    kick   x . x . x . . . . . X . . . X x
  ```

## 6. 808

- Solo the **bass** stem. In this style the 808 usually starts where the kick does, so program it on
  top of your kick pattern, then fix the lengths.
- **Find the notes with the spectrum, not guesses.** Put Parametric EQ 2 on the bass stem and look for the
  tallest peak on the left. With the song's +15-cent tuning, the notes it uses sit at:

  | Note (FL name) | Low octave | One octave up |
  |---|---|---|
  | E  (E2 in FL) | 41.6 Hz | 83.1 Hz |
  | F# (F#2 in FL) | 46.7 Hz | 93.3 Hz |
  | G# (G#2 in FL) | 52.4 Hz | 104.7 Hz |

- Checkpoint: across the song the 808 spends roughly **37% on E, 32% on F#, 21% on G#**. That's
  **VI → VII → i**, the "climb back to home" move. If you've got a C# or a D#, check it again.
- **No glides, mostly.** This 808 **jumps** between notes: out of ~60 pitch changes, about one slides.
  Turn on **Mono** in the 808 channel's Misc tab so each note cuts the last, and leave **Porta off**.
- Match **lengths** by ear. The 808 sounds about three-quarters of the time: phrases of roughly a bar with short
  gaps (about a 16th) between them. Those gaps are half the groove.
- The **kick is its own layer**. It usually lands with an 808 note, but not always, and never on beat 3.

## 7. Melody / synths (hardest, take your time)

- Solo the **instruments** stem and loop **2 bars**.
- **Hum first.** Hum the top line until you can sing it without the track. If you can't hum it, you can't
  program it yet.
- Find the **loudest or most repeated note** first. In this song the upper synths lean on **D#**, the 5th of
  G# minor, so start by checking whether that's the note you're hearing.
- Find the rest one at a time on FL's piano roll keyboard, using only **G# A# B C# D# E F#**.
- **Basic Pitch shortcut:** export the instruments stem for your 2-bar loop, run it through Basic Pitch,
  and drag the MIDI into FL. It will be messy: extra short notes, octave mistakes, reverb tails turned into notes.
  Delete anything shorter than a 32nd, snap starts to the grid, and fix every note by ear against the stem.
  Treat it as a rough first draft.
- **Chords under it:** hold **E**, **F#** and **G#m** triads under the melody along with the 808 roots.
  The one that sounds settled is the chord for that bar.
- Many beats in this lane have **two or three** melodic layers (a main loop, a pad, a quiet counter-line).
  Get the main one first. Then mute your version and listen for what's left.

## 8. Hats

- High-pass the drums stem at **~6 kHz**.
- Base: 8th notes. For rolls, set piano-roll snap to **1/6 step** (16th-note triplets) or **1/2 step**
  (32nds) and count how many hits fit in the roll.
- Checkpoint: rolls show up in about **two bars out of three**, mostly short 32nd or 16th-triplet bursts.
  They **stay on one pitch** in this song, and the loud and soft hits are far apart in level (~21 dB), so use velocity.
- Hats are quiet and short in this mix. Keep yours quieter than feels right.

## 9. Match the sounds

You can't match a sound until the notes are right, so do this last.

- **808:** long decay, **distorted** (Fruity Soft Clipper or Blood Overdrive) so you can hear it on a phone.
  Try 3 or 4 different 808s. The right one is usually obvious in seconds.
- **Synths:** most sounds in this lane are simple (a sine/FM bell, a saw pad, a pluck) with **a lot of reverb
  and delay**, rolled off at the top. Start with FL's FLEX or Sytrus presets, or free [Vital](https://vital.audio).
  If yours sounds too clean, add reverb, cut the highs, and turn it down.
- **Drums:** any royalty-free kit. Pick by **tone and length**, not name: short punchy kick, snare with some
  body, dark hats.
- Overall mix is **dark and 808-first**: sub loudest, mids open for vocals, top end quiet.

## 10. The A/B test (the "90%" check)

1. Put the original on one Playlist track and your remake on another. Set the original's fader so both are
   **equally loud**. Louder always sounds better and will fool you.
2. Flip between them every 4 bars. Your ears adapt quickly, so switch often and take breaks.
3. Go **layer by layer**: solo the drums stem against your drums, the bass stem against your 808, and so on.
   Write down the one layer that's furthest off, fix only that, and repeat.
4. Arrangement: the beat is **one 4-bar loop that never drops a layer**. The changes you hear around **1:08**
   (the vocal gets louder) and at **2:05** (the vocal stops, the beat plays alone to the end) are all vocal
   (see [`ANALYSIS.md`](ANALYSIS.md#arrangement-the-beat-never-changes)). Your remake is finished when one loop matches.

## Checkpoint summary

| Thing | Target |
|---|---|
| Tempo | 140.10 BPM, half-time feel |
| Bar 1 | 0.375 s into the file |
| Tuning | +15 cents |
| Key / scale | G# minor: G# A# B C# D# E F# |
| Clap | Beat 3 of every bar, dry |
| 808 notes | E, F#, G# (VI – VII – i), jumps not glides |
| Hats | 8ths, rolls in ~2 of 3 bars, no pitch ramps |
| Melody focus | Leans on D# |
| Mix | −9.2 LUFS, sub loudest and mono, melody wide and far under the beat, top end dark |

Stuck on a layer? `python3 tools/analyze_reference.py song.wav` (from the repo root) on the original and on a bounce of your remake shows
where the two differ in tempo, key, drum placement and tonal balance.
