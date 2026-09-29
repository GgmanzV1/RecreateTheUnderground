# Remake "Winnie Harlow" yourself in FL Studio

This folder doesn't have a note-for-note copy of the song's parts. This guide is the
next best thing: a workflow for pulling the beat apart by ear in FL, one layer at a time,
with the numbers measured from your WAV as checkpoints. Remaking by ear is the skill that
makes the next remake faster. Your first one will be slow, and that's normal.

**Order:** set up → line up the grid → split stems → snare → kick → 808 → melody → hats → sounds → A/B.
Don't skip ahead. Every layer is easier once the one before it is locked.

## What you need

- FL Studio **Producer Edition or higher** for built-in stem separation. On Fruity Edition, use the
  EQ-soloing trick in [`ANALYSIS.md`](ANALYSIS.md#check-it-yourself-in-fl-this-is-the-skill-to-practise) instead.
- Your WAV of the song.
- Optional: [Basic Pitch](https://engineering.atspotify.com/2022/6/meet-basic-pitch), Spotify's free
  audio-to-MIDI tool. It runs in your browser and gives you a rough first draft of a melody.

## 1. Project setup

- Tempo **140**. The listings that say 136 are wrong; at 136 nothing lines up after a few bars.
- The song is tuned **+15 cents** sharp. While you're comparing, turn FL's **master pitch** up 15 cents
  so your instruments match it. Otherwise every note you find will sound slightly off.
- Key: **G# minor**. Scale: **G# A# B C# D# E F#**. If a melody note sounds almost right but sour, you
  probably have A where it should be **A#**.

## 2. Line up the grid

The first downbeat is **~0.31 s** into the file, about **3 sixteenth-notes** in.

1. Drag the WAV into the Playlist and start it at **bar 2**.
2. Hold **Alt** (turns off snap) and drag the clip left about 3 steps, until its first kick sits on the bar 2 line.
3. Turn on the metronome and play. The **snare should hit on beat 3 of every bar**. If it lands on 1, you're
   half a bar off. If it drifts, check the tempo is exactly 140.

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
- Checkpoint: **one hit per bar, on beat 3** (half-time). The analyzer found some quieter ghost hits
  around it, so listen for extra snares just before or after beat 3 and near the start of the bar.
- Layer a snare and a clap on the same steps. If it sounds wider than one sample, it's probably two.

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
- **Glides:** listen for the pitch bending between notes. Turn on Mono + Porta in the 808 channel's Misc tab
  and overlap the two notes slightly in the piano roll (see [`FL_GUIDE.md`](FL_GUIDE.md#2-808-pattern-808)).
- Match **lengths** by ear. Does each 808 ring until the next one, or cut off early? That's half the groove.

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
- Listen for rolls that **rise in pitch**. That's the note moving up in the piano roll, not a different sample.
- Hats are quiet in this mix (the top end measures ~25 dB under the total). Keep yours quieter than feels right.

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
4. Arrangement: the song is one loop that barely changes. There's an extra layer or denser section around
   **1:08**, and the mids drop out for the **outro at ~2:03** while the 808 keeps going (see the map in
   [`ANALYSIS.md`](ANALYSIS.md#arrangement-map-energy-per-4-bars)).

## Checkpoint summary

| Thing | Target |
|---|---|
| Tempo | 140 BPM, half-time feel |
| Bar 1 | ~0.31 s into the file |
| Tuning | +15 cents |
| Key / scale | G# minor: G# A# B C# D# E F# |
| Snare | Beat 3 of every bar |
| 808 notes | E, F#, G# (VI – VII – i) |
| Melody focus | Leans on D# |
| Mix | Sub loudest, top end dark and quiet |

Stuck on a layer? `python3 analyze_reference.py song.wav` on the original and on a bounce of your remake shows
where the two differ in tempo, key, drum placement and tonal balance.
