# OsamaSon – "Fkd It Up" (prod. ok): what's under the hood

Measured from the WAV you uploaded (2:34, 44.1 kHz, 16-bit stereo) with
[`../tools/analyze_reference.py`](../tools/analyze_reference.py), band-filtered onset analysis, and
stem separation (Demucs htdemucs, used only for measuring and then deleted).
Nothing here copies the song's melody, lyrics or note-by-note parts. It's the recipe and the sound targets.
Every number below is an average or a count over the whole song.

## Credits

| | |
|---|---|
| Artist | OsamaSon (Columbus, Ohio) |
| Producer | **ok** (wegonebeok), the same producer as Nettspend's "Winnie Harlow" |
| Status | Unreleased. It circulates through fan uploads (not linked here) titled "fucked it up (unreleased) (prod. ok)", dated May 2024 |

## The numbers

| What | Measured | Why it matters in FL |
|---|---|---|
| Tempo | **162.00 BPM** | Set FL to 162. The snare is on beat 3, so it *feels* like 81. Auto-detectors often report 81. |
| Bar 1 | **~0.1 s** into the file (first sound at 0.124 s) | Almost no lead-in: the song starts on the downbeat. |
| Tuning | **+35 cents** sharp; the bass, the melody and the vocal all agree | Turn FL's master pitch up 35 cents while you compare. ok's "Winnie Harlow" is +15 cents. His sounds seem to sit off standard tuning. A sped-up upload could also explain it, but then the original tempo would be an odd 158.7 BPM. |
| Key | **D major / B minor** | The melody leans on D, F# and A. The 808 spends most of its time on E (20%), G (18%), A (14%), F# (13%) and D (13%). |
| Loudness | **−9.3 LUFS**, crest ~10 dB | Loud. No flat-topped clipping: it's limited, not hard-clipped. |
| Stereo | **Almost mono**: L/R correlation 1.00 below 80 Hz, 0.99 at 80–250 Hz, 0.91 in the mids, 0.95 in the highs | Keep everything near the center. The opposite of "Winnie Harlow"'s wide melody. |
| Tonal balance | The 40–80 Hz octave holds most of the energy; 80–320 Hz is scooped ~15 dB below it | Sub-heavy, with little low-mid mud. |
| Bandwidth | Full, up to 20 kHz | A better-quality file than the "Winnie Harlow" one. |

## The stems (loudness while everything plays)

| Stem | LUFS | Relative to the 808 |
|---|---|---|
| Bass / 808 | −10.5 | — |
| Vocal | −14.0 | 3.5 LU under |
| Drums | −18.1 | 7.6 LU under |
| Melody | −22.3 | 11.8 LU under |

The 808 is the loudest thing in the song by a wide margin, and the melody is quiet.

## The sounds

| Part | What it measures as |
|---|---|
| **808** | **Clean and sub-heavy**: harmonics 2–7 at −26 / −21 / −31 / −25 / −35 / −32 dB below the fundamental, with a faint layer of upper overtones 35–55 dB down. Flat sustain (−1.4 dB/s). Fundamental 42–160 Hz, centred near 51 Hz. Sounding 86% of the time. |
| **808 slides** | **About half of its big pitch moves slide**: 45 slides in the song (~18 a minute), typically 3–4 semitones over ~100 ms. The rest are hard jumps. Porta goes back on for this one. |
| **Drums** | The snare is on **beat 3** of every bar (half-time at 162). Hats, kicks and snares all sit on **straight 8th notes**: no 16ths, no triplets, no swing, **no rolls**. The drum stem is top-heavy: most of its energy is at 5–10 kHz (hats and snare), not in the kick. |
| **Kick** | Peaks near 54 Hz. |
| **Snare** | Strongest near 1.1 kHz, bright, −20 dB in ~47 ms. |
| **Hats** | Very short: −20 dB in ~27 ms. |
| **Melody** | One clean, tonal synth (spectral flatness 0.015), looping every **4 bars**. Range roughly F#2–F#6, centred near 2 kHz, with a **slow ~136 ms swell** on each note. Nearly mono. |
| **Vocal** | Hard-tuned (71% of the time within ±10 cents of a note, no wobble) to the song's +35-cent tuning. |

## The filter trick

The melody changes depending on whether the 808 is playing. With the 808 in, the melody is quieter and thinner.
When the 808 drops out, it comes back full. Comparing the same melody in both situations (without minus with the 808):

| Band | 80–160 | 160–320 | 320–640 | 640–1280 | 1.3–2.6k | 2.6–5k | 5–10k Hz |
|---|---|---|---|---|---|---|---|
| Louder without the 808 by | 12.2 | 13.5 | 10.5 | 5.2 | 6.8 | 6.5 | 1.9 dB |

So while the 808 plays, the melody drops about 6 dB overall, loses another ~6–7 dB below ~640 Hz, and keeps its top.
That leaves the low end to the 808. It's a low-shelf cut plus a volume drop, automated with the 808.

## Arrangement: 4-bar blocks and drop-outs

104 bars at 162 BPM. Unlike "Winnie Harlow", this beat *does* use mute tricks, always in 4-bar blocks:

| Move | Where |
|---|---|
| 808 drops out, drums stay | bars 5–8, 45–48, 53–56 |
| 808 **and** drums drop out, melody alone | bars 17–20, 65–68 |
| Melody drops out for ~6 bars inside a section | around bars 35–40 and 83–88 |
| Outro: 808 fades, drums thin out, melody and vocal carry it | from about bar 93 |

## How Overexposed (the beat in this folder) compares

Overexposed keeps its own chords, melody, drums and 808 line. Its sound and mix are built to the targets above:

| | Fkd It Up | Overexposed |
|---|---|---|
| Tempo / feel / key | 162, snare on 3, D major / B minor | 162, snare on 3, B minor (its own i–VI–III–VII) |
| Loudness / true peak / crest | −9.3 LUFS / +1.0 dBTP / 10.9 dB | −9.4 LUFS / −1.0 dBTP / 8.2 dB |
| Stereo correlation <80 / 80–250 / 250–2k / 2k–8k | 1.00 / 0.99 / 0.91 / 0.95 | 1.00 / 0.98 / 0.91 / 0.96 |
| Tonal balance 40–80 / 80–160 / 160–320 Hz (share) | −1.7 / −16.0 / −16.4 dB | −0.7 / −15.8 / −15.7 dB |
| 808 harmonics 2–7 | −26 / −21 / −31 / −25 / −35 / −32 dB | −27 / −21 / −31 / −25 / −36 / −29 dB |
| 808 on / slides | 86% / about half the pitch moves | 88% / half the pitch moves |
| Stem balance 808 → drums → melody | 7.6 LU, then 4.2 LU | 7.2 LU, then 4.1 LU |
| Filter trick, open minus filtered (80 Hz → 10 kHz bands) | 12 / 14 / 11 / 5 / 7 / 7 / 2 dB | 10 / 10 / 6 / 5 / 6 / 7 / 5 dB |
| Drums | straight 8ths, no rolls | straight 8ths, no rolls |
| Arrangement | 4-bar blocks, 808 drops, 808+drum drops, melody drops | the same moves, in its own 64-bar layout |

The mids (320 Hz – 5 kHz) of Overexposed measure lower than the song's. That's expected: the song has a vocal there.
