# Building Glasshouse in FL Studio

Everything here uses FL's stock plugins plus two free ones:
[Vital](https://vital.audio) (synth) and
[Valhalla Supermassive](https://valhalladsp.com/shop/reverb/valhalla-supermassive/) (reverb/delay).
Listen to `audio/glasshouse_preview.mp3` first so you know what you're aiming for.

> **Note names:** FL calls middle C "C5" (standard is C4), so every note in FL
> reads one octave higher than in `build_beat.py`. The 808's G#1 shows as G#2 in FL.

## 0. Project setup

- Tempo **140**, time signature 4/4.
- Pick sounds. You need: a **long 808**, a punchy **kick**, a **snare** and a **clap**,
  a closed **hat**, an **open hat**, a **rim/perc**. Any royalty-free kit works; stock FL
  sounds are fine to start.

## 1. Drums (Pattern "Drums")

1. In the Channel Rack make one Sampler channel per sound: kick, snare, clap, hat, openhat, perc.
2. Drag each file from `midi/loops/` onto the matching channel's piano roll
   (`01_kick.mid` → kick, `03_snare.mid` → snare, etc.). Every loop is **8 bars**.
3. **Hat rolls** are already in `05_hat.mid`. To make your own:
   set the piano roll snap to **1/6 step** (16th-triplet rolls) or **1/2 step** (32nd rolls),
   draw the notes, then raise each note a semitone for a rising roll (bar 6 does this).
4. **Choke the open hat:** open the hat and open-hat channel settings → Misc tab →
   put both in the same **Cut / Cut by** group so a closed hat cuts the open one off.
5. Snare + clap land together on **beat 3 of every bar**. That's the half-time feel.
   Nudge the clap 5–10 ms late for a wider hit.

## 2. 808 (Pattern "808")

1. Load a long 808 into a Sampler channel and drag in `02_808.mid`.
2. **Glides:** channel settings → Misc tab → Polyphony: turn on **Mono** and **Porta**,
   set **Slide** to ~60–80 ms. The MIDI already overlaps the notes that should glide
   (the end of every 2 bars: octave jumps up, and the drop from D# back to G# before the loop restarts).
3. **Tuning:** if it sounds an octave off, select all notes (Ctrl+A) and move them an
   octave (Ctrl+↑/↓). If it sounds *out of tune*, the sample isn't in C. Find its note with a tuner
   and set the sampler's root note to match.
4. FX chain on the 808 mixer track: **Fruity Soft Clipper** or **Fruity Blood Overdrive**
   (gain until it growls on phone speakers) → **Parametric EQ 2** (high-pass ~30 Hz, low-pass ~5 kHz).
5. The kick channel follows the 808 (`01_kick.mid` hits on 808 starts). Keep the kick short
   (~150 ms) so it adds click, not boom.

## 3. Pad (Pattern "Chords")

- Sound: Vital, init preset → saw wave, **Unison 5–7 voices**, detune ~20%, filter
  low-pass ~2.5 kHz. Amp envelope: attack ~0.4 s, sustain full, release ~1.5 s.
  (Stock alternative: a FLEX pad preset.)
- MIDI: `08_pad.mid` (one chord every 2 bars: G#m(add9) → Emaj9 → C#m9 → D#m7).
- FX: **Supermassive** (big, dark: mix ~40%, long decay) → **sidechain** to the kick:
  route the kick's mixer track to the pad's track as a sidechain, put **Fruity Limiter**
  on the pad track, switch it to COMP, set the sidechain input, and pull the
  threshold down until the pad ducks ~4–6 dB on every kick.

## 4. Bell lead (Pattern "Lead")

- Sound: Vital → Osc 1 sine, Osc 2 sine at **2× pitch** routed as **FM** into Osc 1
  (amount ~40%, with its own fast-decaying envelope so the attack is bright and the tail is soft).
  Amp envelope: attack 0, decay ~0.6 s, sustain 0. (Stock alternative: a Sytrus or FLEX bell.)
- MIDI: `09_lead.mid`, a syncopated 3-3-2 / 3-3-2 rhythm (in 16ths) repeated over each chord.
- **Width trick:** clone the channel, pan one left and one right, detune the copy +6 cents.
- FX: Parametric EQ 2 high-pass ~200 Hz → **Fruity Delay 3** (time **3 steps** = dotted 8th,
  feedback ~35%, ping-pong, mix ~25%) → reverb ~30%.

## 5. Glass arp (Pattern "Arp")

- Sound: short sine pluck with a little 3rd and 5th harmonic (Vital: sine + small amount
  of a 3× osc, decay ~120 ms).
- MIDI: `10_arp.mid`, chord tones one octave up, 16th notes, alternating velocity.
- FX: a bitcrusher / lo-fi plugin (light: ~7 bits) → high-pass 500 Hz → heavy reverb (~50%).
  Pan it wide. It should be felt more than heard. Sidechain it like the pad.

## 6. Riser (intro only)

A 2-bar white-noise sweep: 3xOsc with the noise shape, or any riser sample. Automate
a **Fruity Filter** band-pass from ~400 Hz up to ~9 kHz over bars 7–8.

## 7. Arrangement (Playlist, bars as FL numbers them)

| Bars | Section | Patterns |
|---|---|---|
| 1–8 | Intro | Chords + Lead behind a low-pass; riser on 7–8 |
| 9–24 | Hook | Everything except Arp |
| 25–40 | Verse | Drums + 808 + Chords + Arp (no Lead: that's where vocals go) |
| 41–56 | Hook | Everything |
| 57–64 | Outro | Chords + Lead + Arp, one last 808 + kick on bar 57 |

**Mute tricks** (these make the loop feel arranged):
- Bar **32**: no 808, no kick (the "808 stop").
- Bar **40**: only hats play. Everything slams back on bar 41.
- Intro filter: **Fruity Filter** on the Chords and Lead tracks, cutoff ~700 Hz, automate it fully open across bars 7–8.

Shortcut: **File → Import → MIDI file** with `midi/glasshouse_arrangement.mid` lays out
every part over all 64 bars at once, one channel per part.

## 8. Mix

Match the reference's balance: **808 loudest**, kick and snare just under it, bell lead
under the drums, pad and arp tucked behind, hats quiet. Keep the top end dark.

- Put the preview (or the original song) on its own Playlist track and flip between it and
  your beat at matched volume. Your ears adapt fast, so compare often.
- Master: **Fruity Soft Clipper** → **Fruity Limiter** to about -1 dB ceiling.
- `build_beat.py` → `MIX` holds the exact target loudness per part if you want numbers.
