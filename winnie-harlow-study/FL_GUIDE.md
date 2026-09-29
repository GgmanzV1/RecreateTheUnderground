# Building Glasshouse in FL Studio

Everything here uses FL's stock plugins plus one free synth, [Vital](https://vital.audio).
Listen to `audio/glasshouse_preview.mp3` first so you know what you're aiming for.
The targets in each section come from measuring "Winnie Harlow" (see [`ANALYSIS.md`](ANALYSIS.md)).
Glasshouse keeps its own chords, melody and drum patterns; its sounds and mix are built to those targets.

> **Note names:** FL calls middle C "C5" (standard is C4), so every note in FL
> reads one octave higher than in `build_beat.py`. The 808's G#1 shows as G#2 in FL.

## Shortcut: open the ready-made project

`fl_project/` has **`Glasshouse.flp`** plus one WAV per channel. It's the whole beat, already laid out:

1. Download the entire `fl_project` folder and keep the WAVs **in the same folder** as the `.flp`.
2. In FL: **Options → File settings → Browser extra search folders**, add that folder. You only do this once.
   It's how FL finds the samples wherever you saved them.
3. Open `Glasshouse.flp`. If a channel comes up empty, drag its WAV (`Glasshouse Kick.wav` → Kick, etc.)
   from the folder onto the channel.

What's inside:

- **Channels** (all Samplers, no third-party plugins): Kick, 808, Snare, Clap, Hat, Open Hat, Rim, Pad,
  Bell Lead, Glass Arp, Zap. Each channel is routed to its own named mixer insert.
- Already set: 140 BPM, the 808 on **Mono** (each note cuts the last, no Porta glides), Hat and Open Hat in the
  same **cut group**, and the volume envelope on the 808 and Pad so they stop when the note ends.
- The 808 sample already has its saturation and stereo harmonics printed in. The Pad, Bell Lead, Glass Arp and
  Zap samples have their short room reverb printed in. The drums are dry and mono.
- **Patterns:** Drums, 808, Chords, Lead, Arp, plus *Drums (no kick)* for the 808 stop and *Zap* for the FX hits.
- **Playlist:** the full 56-bar arrangement from section 7, on tracks named Drums / 808 / Chords / Lead / Arp / FX.

Not included, because it depends on plugin settings: the master chain (section 8). The preview has it, so
the project will sound quieter until you add it. Swapping the samples for your own sounds (drag a new WAV onto a
channel) is the fastest way to make it yours.

It was built for **FL Studio 20.8 or newer** by `build_flp.py`, not saved from FL itself, so if your FL
won't open it, use the MIDI route below and let me know what error you got.

## 0. Project setup

- Tempo **140**, time signature 4/4.
- Pick sounds. You need: a **long 808**, a short dark **kick**, a **clap** and a light **snare**,
  a closed **hat**, an **open hat**, a **rim/perc**. Any royalty-free kit works; stock FL
  sounds are fine to start.

## 1. Drums (Pattern "Drums")

1. In the Channel Rack make one Sampler channel per sound: kick, snare, clap, hat, openhat, perc.
2. Drag each file from `midi/loops/` onto the matching channel's piano roll
   (`01_kick.mid` → kick, `03_snare.mid` → snare, etc.). Every loop is **8 bars**.
3. **Kick:** short (130–150 ms) and dark: a pitch drop from ~250 Hz into a 55–60 Hz body, little click.
   It's its own layer. It lands with most 808 notes but **never on beat 3**. Keep it loud: its hit should
   stand 8–10 dB above the 808's sustain.
4. **Clap (the main backbeat):** beat 3 of every bar, **dry and mono**. Three quick bursts, gone
   (−40 dB) by ~75 ms, strongest around 1.3 kHz. Cut everything under ~600 Hz with Parametric EQ 2.
   The snare is a quiet, short body layer under it. No reverb on either.
5. **Hats:** 8th notes, with **rolls in 5 of the 8 bars** (the reference rolls in about two bars out of three).
   Set piano-roll snap to **1/6 step** (16th triplets) or **1/2 step** (32nds) and draw them.
   Keep rolls on **one pitch**, and use velocity instead: fade in from very soft or fade out from loud
   (about 20 dB between loudest and softest). A short, dark hat (energy near 6 kHz, ~35 ms decay) fits.
6. **Choke the open hat:** open the hat and open-hat channel settings → Misc tab →
   put both in the same **Cut / Cut by** group so a closed hat cuts the open one off.

## 2. 808 (Pattern "808")

1. Load a long 808 into a Sampler channel and drag in `02_808.mid`.
2. **Mono, no glides:** channel settings → Misc tab → Polyphony: turn on **Mono**, leave **Porta off**.
   The reference 808 **jumps** between notes (about one glide in the whole song). Glasshouse keeps just one
   glide per loop, at the very end. If you want it, use a slide note there (piano roll → slide tool).
3. **Leave gaps.** The 808 should sound about three-quarters of the time: phrases with short gaps between them.
   Enable the volume envelope (INS tab) with sustain full and a short release so notes stop on time.
4. **Tuning:** if it sounds an octave off, select all notes (Ctrl+A) and move them an
   octave (Ctrl+↑/↓). If it sounds *out of tune*, the sample isn't in C. Find its note with a tuner
   and set the sampler's root note to match.
5. **Saturation:** the target is a flat, sustaining 808 whose harmonics sit at **2nd −15, 3rd −6, 4th −16,
   5th −28 dB** under the fundamental. Put **Fruity WaveShaper** (or Soft Clipper) on the 808's mixer track and
   raise it until, in Parametric EQ 2's spectrum, the peak three times the note's frequency is about 6 dB under the
   fundamental. That loud 3rd harmonic is what makes it audible on phone speakers.
6. **Stereo:** keep everything below ~90 Hz **mono**. The harmonics above can be a little wide: send the 808 to two
   inserts, low-pass one at 90 Hz (leave it mono), high-pass the other at 110 Hz and add **Fruity Stereo Enhancer**
   with a small phase offset. Check in mono that nothing disappears.

## 3. Pad (Pattern "Chords")

- Sound: Vital, init preset → saw wave, **Unison 5–7 voices**, detune ~20%, filter
  low-pass ~4 kHz. Amp envelope: attack ~60 ms, sustain full, release ~0.3 s.
  (Stock alternative: a FLEX pad preset.)
- MIDI: `08_pad.mid` (one chord every 2 bars: G#m(add9) → Emaj9 → C#m9 → D#m7).
- FX: **Fruity Reeverb 2** with a short room (decay ~0.5 s, mix ~30%). **No sidechain**: the reference's
  melody never ducks.

## 4. Bell lead (Pattern "Lead")

- Sound: Vital → Osc 1 sine, Osc 2 sine at **2× pitch** routed as **FM** into Osc 1
  (amount ~40%, with its own fast-decaying envelope so the tone is bright at first and soft after).
  Amp envelope: **attack ~40 ms**, decay ~0.6 s, sustain 0. (Stock alternative: a Sytrus or FLEX bell.)
- MIDI: `09_lead.mid`, a syncopated 3-3-2 / 3-3-2 rhythm (in 16ths) repeated over each chord.
  It sits around D#4–E5 (FL: D#5–E6), the same register as the reference's melody.
- **Width:** clone the channel, pan one hard left and one hard right, detune them −7 and +7 cents.
  The reference's melody is almost fully wide.
- FX: Parametric EQ 2 high-pass ~200 Hz → the same short room reverb (~40%). No ping-pong delay.

## 5. Glass arp (Pattern "Arp")

- Sound: short sine pluck with a little 3rd and 5th harmonic (Vital: sine + small amount
  of a 3× osc, attack ~8 ms, decay ~120 ms).
- MIDI: `10_arp.mid`, chord tones one octave up, 16th notes, alternating velocity.
- FX: high-pass 500 Hz → short room reverb (~40%). Pan the notes alternately left and right.
  It should be felt more than heard. No bitcrusher: the reference measures clean.

## 6. Zap (FX hit)

A laser-style hit on the first beat of each hook: a sine sweeping from ~3 kHz down to ~150 Hz in about
a quarter of a second, slightly distorted. In 3xOsc, automate the pitch down, or use any laser/zap one-shot.
One-off FX hits like this (and glass-break sounds) are a common touch in ok's beats.

## 7. Arrangement (Playlist, bars as FL numbers them)

| Bars | Section | Patterns |
|---|---|---|
| 1–4 | Intro | Chords + Lead |
| 5–20 | Hook | Everything except Arp; Zap on bar 5 |
| 21–36 | Verse | Drums + 808 + Chords + Arp (no Lead: that's where vocals go) |
| 37–52 | Hook | Everything; Zap on bar 37 |
| 53–56 | Outro | Chords + Lead + Arp, the beat stops |

One mute trick: bar **36**, no 808 and no kick (the "808 stop"), so the second hook hits harder.
That's deliberately less than most type beats: the reference never drops a layer and lets the vocal carry the
changes. The whole beat is 1:38. Songs in this lane are often under two minutes.

Shortcut: **File → Import → MIDI file** with `midi/glasshouse_arrangement.mid` lays out
every part over all 56 bars at once, one channel per part.

## 8. Mix and master

Balance: **808 and kick loudest** (the kick's hits poking above the 808), clap under them, the bell lead
under the drums, pad and arp tucked behind, hats quiet. The melody should sit far under the beat.

- **Stereo:** kick, clap, snare, hats and the 808's sub all mono and centered. Width comes from the melodic layers.
- **Master:** **Fruity Soft Clipper** → **Fruity Limiter** with the ceiling at **−1 dB**. Push until
  the master reads about **−9 LUFS** (the reference is −9.2). Use the **Youlean Loudness Meter** (free) to read it.
  If the kick stops poking out, back off the clipper and lower the 808 a dB or two instead.
- **Top end:** keep it dark (little above 8 kHz), but don't cut everything at 16 kHz. That wall in the
  reference is just the ~128 kbps file.
- Put the preview (or the original song) on its own Playlist track and flip between it and
  your beat at matched volume. Your ears adapt fast, so compare often.
- `build_beat.py` → `MIX` holds the exact level per part if you want numbers.
