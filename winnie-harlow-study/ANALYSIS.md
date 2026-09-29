# Nettspend – "Winnie Harlow": what's under the hood

Measured from the WAV you uploaded (2:17, 44.1 kHz stereo) with `analyze_reference.py`
plus a few one-off checks. Nothing here copies the song's melodies, lyrics or
note-by-note parts. It's the framework you need to make beats in this style.

## Credits and release info

| | |
|---|---|
| Released | Dec 14, 2024 (Audiomack upload date) |
| Producer | Audiomack lists **"ok"**; another listing credits **KwickedOnAllPlats** (unconfirmed) |
| Listed BPM / key online | 136 BPM, G# minor |

## The numbers

| What | Measured | Why it matters in FL |
|---|---|---|
| Tempo | **140 BPM** (bar-length autocorrelation locks on at 140.1) | The 136 listed online is wrong. Set FL to 140. |
| Feel | **Half-time**: one snare per bar, on beat 3 | Counts like 70 BPM, so it sounds slow and heavy even though the hats move at 140. |
| Key | **G# minor** | Matches the online listing. The full-mix key guess says E major because the 808 sits on E so much, but the synths between 200 Hz and 4 kHz fit **G# natural minor** (lots of A#, very little A). |
| Bar 1 | Starts **~0.31 s** into the file (~3 sixteenths) | Slide the clip left this much in the Playlist so the song lines up with FL's grid. |
| Tuning | **+15 cents** sharp of A440 | When you A/B your beat against the song in FL, turn the master pitch up ~15 cents or everything will sound slightly off. |
| Harmony | The 808 spends ~37% of the time on **E**, ~32% on **F#**, ~21% on **G#** | That's **VI – VII – i** in G# minor, the "rising into the home note" move this style lives on. The upper synths lean on **D#** (the 5th). |
| Tonal balance | Sub (20–80 Hz) carries the most energy; the top end (8 kHz+) is ~25 dB below the total | It's a **dark, bass-first** mix. Bright, crispy hats and melodies would sound wrong here. |
| 808 | Sub level is flat from 0:00 to the end | The 808 **never leaves**. There are no long 808-free sections. |

## Arrangement map (energy per 4 bars)

The track is essentially **one loop that runs the whole song**. The sub and low-mid
bands barely move (within ~0.5 dB) from start to finish. The changes come from parts
being added or muted on top:

| Time | What the energy does |
|---|---|
| 0:00 | Beat is in almost immediately, no long intro |
| 0:00 – 2:00 | Flat, steady energy: vocals carry the variation, not the beat |
| ~1:08 | One 4-bar window with ~2 dB more mid-range: an extra layer or denser vocals |
| ~2:03 | Outro: mids drop ~4 dB and highs ~3 dB, but the 808 keeps going |
| 2:17 | Ends without a long fade |

**Lesson:** underground beats like this don't need big drops or builds. A strong
8-bar loop plus small mute tricks (drop the 808 for a bar, strip to hats before a
section) is the whole arrangement.

## Style conventions (genre knowledge, not measured from this file)

These are the standard moves in this lane of underground rap. Use them as a checklist:

- **808:** long, distorted/saturated so it's audible on phone speakers, with **glides** (portamento) between notes. Kicks usually hit on the same notes as the 808.
- **Hats:** 8th-note base with **triplet and 32nd-note rolls**, sometimes pitched up during the roll.
- **Melody:** simple, repetitive motifs on bells, plucks or airy synths, drowned in **reverb and delay** so they feel washed out and far away.
- **Space:** mid-range left open for the vocals. That's why the mix measures dark.
- **Lo-fi texture:** bitcrushing, detune and pitch wobble are common on the melodic layers.

## How Glasshouse (the beat in this folder) compares

| | Winnie Harlow | Glasshouse |
|---|---|---|
| Tempo / feel | 140, half-time | 140, half-time ✔ |
| Key | G# minor | G# minor ✔ |
| Harmony | VI – VII – i home notes | i – VI – iv – v (original progression) |
| Melody | – | Original 3-3-2 syncopated bell motif |
| Drums | – | Original pattern built on the same conventions |
| Tonal balance | Dark, sub-first | Matched within ~0.6 dB from sub to highs (top 8 kHz+ is ~3.5 dB brighter) |
| Arrangement | One loop, mute-based changes | One loop, mute-based changes ✔ |

Want Glasshouse closer to the vibe? Change `CHORDS` in `build_beat.py` to sit on
VI – VII – i (E, F#, G#). That's one of the most common moves in the genre and
is yours to use.

## Check it yourself in FL (this is the skill to practise)

1. Drag the song into the **Playlist**, set the project to **140 BPM**, and turn off stretching so it plays at its real speed. If the bars line up with the grid, the tempo's right.
2. Put **Fruity Parametric EQ 2** on the song's mixer track and solo bands:
   - Low-pass at ~120 Hz → you hear only the 808/kick. Hum the notes and find them on your keyboard.
   - High-pass at ~6 kHz → only hats and air. Count the rolls.
   - Band-pass 1.5–4 kHz → snare/clap. Count where it lands in the bar.
3. Loop 4 bars (select them in the Playlist timeline) and play along on the piano roll's preview keyboard until your notes match.
4. Use a tuner plugin on the low-passed track to confirm the 808 notes. Remember the song is +15 cents sharp.
5. Drop **markers** at each change you hear to build your own arrangement map.
6. For a second opinion, run `python3 analyze_reference.py song.wav` on any track you own.

## Sources

- [Audiomack – winnie harlow by nettspend](https://audiomack.com/bloodcore-1/song/winnie-harlow)
- [Chordify – Nettspend: Winnie Harlow](https://chordify.net/chords/nettspend-winnie-harlow-bafk) (page blocked automated access, not used for any numbers)
- [TikTok – Winnie Harlow Nettspend Instrumental](https://www.tiktok.com/discover/winnie-harlow-nettspend-instrumental)
