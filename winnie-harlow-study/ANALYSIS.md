# Nettspend – "Winnie Harlow": what's under the hood

Measured from the WAV you uploaded (2:17, 44.1 kHz stereo) with [`../tools/analyze_reference.py`](../tools/analyze_reference.py) and the deeper
measurements behind the full study in [`../reports/Winnie Harlow production study.md`](../reports/Winnie%20Harlow%20production%20study.md).
Nothing here copies the song's melodies, lyrics or note-by-note parts. It's the framework and the sound targets.

## Credits and release info

| | |
|---|---|
| Producer | **ok** (wegonebeok, credited as William Dale Minnix III), Nettspend's main producer: about 10 of the 15 tracks on *Bad Ass F\*cking Kid*, plus "Nothing Like Uuu" and "F\*ck Swag" |
| Release | Official: track 16, a bonus on the webstore-only "Winnie Version" of *Bad Ass F\*cking Kid* (Dec 2024). Not on streaming services. The SoundCloud/Audiomack "archive" copies are fan re-uploads from Dec 12 and 14, 2024 |
| "KwickedOnAllPlats" | Not a credit. It's the bio text of a small TikTok remake account that search summaries mistook for a producer |
| Listed BPM / key | Chordify: 136 BPM, G# minor. The key is right; the tempo is a machine-estimate miss |

## The numbers

| What | Measured | Why it matters in FL |
|---|---|---|
| Tempo | **140.10 BPM** | Build at 140. When you A/B against the file, set FL to **140.10**, or it drifts ~0.1 s (almost a 16th) by the end. |
| Feel | **Half-time**: the clap is on beat 3 of every bar | Counts like 70 BPM, so it sounds slow and heavy even though the hats move at 140. |
| Bar 1 | **0.375 s** into the file (~3.5 sixteenths), right after the silence | Slide the clip left this much so the song sits on FL's grid. |
| Key | **G# natural minor** | The synths between 200 Hz and 4 kHz use A#, not A. A full-mix key guess says E major only because the 808 sits on E so much. |
| Tuning | **+15 cents** sharp (A ≈ 443.8 Hz) | Turn FL's master pitch up 15 cents while you compare. It's in the sounds themselves, not from a sped-up upload. |
| Harmony | The 808 spends ~37% of the time on **E**, ~32% on **F#**, ~21% on **G#** | **VI – VII – i** in G# minor, the "rising into the home note" move. |
| Loudness | **−9.2 LUFS**, crest ~10 dB, loudness range 1.1 LU | Loud and flat. Soft clipper then limiter on the master, ceiling −1 dBTP. |
| Stereo | **Mono below 80 Hz**; the 808's harmonics (80–250 Hz) are partly wide; the melody is very wide; drums and vocal are mono | Keep the sub mono, the drums centered, and spread the melody. |
| Top end | Rolled off above 8 kHz, and cut completely at **~16 kHz** | Part of the "dark" top end is dark mixing. The 16 kHz wall is the ~128 kbps file you have, so don't copy it into your master. |

## The sounds

| Part | What it measures as |
|---|---|
| **808** | Fundamental ~41–54 Hz. **Flat sustain**, moderately saturated: harmonics 2–5 at −15 / −6 / −16 / −28 dB below the fundamental. Sounds ~77% of the time, in phrases with short (~190 ms) gaps. **It jumps between notes**: only about one audible glide in the whole song. |
| **Kick** | Its own layer, not a copy of the 808's rhythm. ~2.4 per bar, never on beat 3. Short (130–150 ms), dark, sweeping ~250 Hz down to a 55–60 Hz body in ~80 ms. Peaks 8–10 dB above the 808's sustain. |
| **Clap** | Beat 3 of every bar. Three bursts ~12 ms apart, peak ~1.3 kHz, almost nothing under 600 Hz. **Dry**: −20 dB in ~40–50 ms, −40 dB by ~75 ms. |
| **Hats** | 8th-note base, ~11–12 hits per bar. Rolls (mostly 32nds and 16th-triplets) in about **two bars out of three**. Energy peaks ~6.3 kHz, very short decay (~37 ms), ~21 dB between the loudest and softest hit. **No pitched rolls.** |
| **Melody** | One chordal layer looping every 4 bars, energy centered around 1–2.5 kHz. Soft ~46 ms attack, a short 0.4–0.7 s ambience, no ducking, almost no pitch wobble. Sits far under the beat (~13 LU). |
| **Vocal** | Hard-tuned to G# minor at the song's +15-cent tuning, mono, with a faint tail. |

## Arrangement: the beat never changes

The beat is **one 4-bar loop played 20 times**. No drum, 808 or melody layer ever drops out. Every change you
hear comes from the vocal:

| Bars | Time | What changes |
|---|---|---|
| 1 | 0:00.4 | Everything starts at once |
| 41–43 | ~1:08 | The vocal gets louder |
| 51–52, 55–56 | ~1:26, ~1:33 | Short vocal gaps |
| 74–80 | 2:05–2:17 | Vocal gone, beat alone, then a hard cut |

**Lesson:** in this lane the beat is a strong loop that the rapper arranges. As a producer, get the loop and
the sounds right first. For an instrumental with no vocal, add small changes (an intro, dropping the lead in
the verse, one 808 stop), but don't overdo it.

## Style conventions vs. this song

The genre playbook (see the report's playbook section) says: distorted 808s with glides, pitched hat rolls,
melodies washed in reverb and delay, lo-fi textures, sidechained pads. **This song skips most of that.** The 808
jumps instead of gliding, the rolls stay on one pitch, the reverb is short, there's no measurable wobble, and nothing ducks.
Treat those moves as options, not requirements.

## How Glasshouse (the beat in this folder) compares

Glasshouse keeps its own chords, melody and drum patterns. Its sound and mix are built to the targets above:

| | Winnie Harlow | Glasshouse |
|---|---|---|
| Tempo / feel / key | 140.10, half-time, G# minor | 140, half-time, G# minor |
| Loudness / peak / crest | −9.2 LUFS / +0.4 dBTP (lossy file) / 10.5 dB | −9.4 LUFS / −1.0 dBTP / 9.6 dB |
| Stereo correlation: below 80 Hz / 80–250 Hz | 0.98 / 0.83 | 1.00 / 0.89 |
| 808 harmonics 2–5 | −15 / −6 / −16 / −28 dB | −15.0 / −5.5 / −15.7 / −28.1 dB |
| 808 glides | ~1 in the song | 1 per 8-bar loop |
| Kick punch over the 808 (same method on both) | 6.9 dB | 7.4 dB |
| Clap peak / centroid / −40 dB | 1.3 kHz / 2.5 kHz / ~75 ms | 1.5 kHz / 2.6 kHz / 81 ms |
| Hat energy peak / −20 dB decay | 6.3 kHz / 37 ms | 5.9 kHz / 32 ms |
| Hat rolls | ~2 bars in 3, no pitch ramps | 5 bars in 8, no pitch ramps |
| Harmony | VI – VII – i | i – VI – iv – v (its own) |
| Arrangement | one loop, vocal makes the changes | 4-bar intro, lead drops in the verse, one 808 stop, melody-only outro |

## Check it yourself in FL (this is the skill to practise)

1. Drag the song into the **Playlist**, set the project to **140.10 BPM**, and turn off stretching so it plays at its real speed.
   Start the clip at bar 2 and slide it left 0.375 s (Alt-drag) so its first beat sits on the bar line.
2. Put **Fruity Parametric EQ 2** on the song's mixer track and solo bands:
   - Low-pass at ~120 Hz → you hear only the 808/kick. Hum the notes and find them on your keyboard.
   - High-pass at ~6 kHz → only hats and air. Count the rolls.
   - Band-pass 1–2 kHz → the clap. Count where it lands in the bar.
3. Loop 4 bars (select them in the Playlist timeline) and play along on the piano roll's preview keyboard until your notes match.
4. Use a tuner plugin on the low-passed track to confirm the 808 notes. Remember the song is +15 cents sharp.
5. For a second opinion, run `python3 tools/analyze_reference.py song.wav` on any track you own. It prints the tempo,
   where bar 1 starts, the key, the 808's notes, an averaged drum grid and an energy map.
