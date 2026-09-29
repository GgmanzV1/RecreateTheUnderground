#!/usr/bin/env python3
"""Measure a reference track before you try to recreate its style.

Prints tempo (and whether it is half-time), key candidates, tuning offset,
an average one-bar drum grid, and an energy timeline you can use to map the
arrangement. Works on any WAV/FLAC/MP3/OGG you have on disk.

Usage:
  pip install numpy scipy librosa soundfile
  python3 analyze_reference.py path/to/song.wav
"""
import argparse

import librosa
import numpy as np
from scipy import signal

SR = 22050
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
BANDS = [("sub", 20, 80), ("low", 80, 250), ("mid", 250, 2000), ("high", 2000, 8000), ("air", 8000, 11000)]


def tempo(perc):
    hop = 128
    fps = SR / hop
    env = librosa.onset.onset_strength(y=perc, sr=SR, hop_length=hop)
    ac = librosa.autocorrelate(env)
    ac /= ac[0]

    def at(lag):
        i = int(lag)
        f = lag - i
        return (1 - f) * ac[i] + f * ac[i + 1] if i + 1 < len(ac) else 0.0

    # Loops repeat every bar, so the bar length is the most reliable period.
    # Searching 80-180 BPM keeps trap/rage beats at 140 instead of 70.
    bpms = np.arange(80, 180, 0.05)
    score = [at(240 / b * fps) + 0.5 * at(60 / b * fps) + 0.5 * at(120 / b * fps) for b in bpms]
    best = float(bpms[int(np.argmax(score))])
    return round(best * 2) / 2, env, hop


def key(harm, cents):
    chroma = librosa.feature.chroma_cqt(y=harm, sr=SR, tuning=cents / 100).mean(axis=1)
    fits = []
    for i in range(12):
        fits.append((np.corrcoef(chroma, np.roll(MAJOR, i))[0, 1], f"{NAMES[i]} major"))
        fits.append((np.corrcoef(chroma, np.roll(MINOR, i))[0, 1], f"{NAMES[i]} minor"))
    ranked = [NAMES[i] for i in np.argsort(chroma)[::-1]]
    return sorted(fits, reverse=True)[:3], ranked


def bass_notes(harm, cents):
    """Which notes the 808/bass sits on. Vocals can't fool this the way they fool full-mix chroma."""
    low = signal.sosfiltfilt(signal.butter(6, 150, "lowpass", fs=SR, output="sos"), harm)
    y = librosa.resample(low, orig_sr=SR, target_sr=4000)
    f0, voiced, prob = librosa.pyin(y, fmin=30, fmax=160, sr=4000, frame_length=1024, hop_length=128)
    ok = voiced & ~np.isnan(f0)
    pc = np.round(librosa.hz_to_midi(f0[ok]) - cents / 100).astype(int) % 12
    share = np.bincount(pc, weights=prob[ok], minlength=12)
    share /= share.sum()
    return [(NAMES[i], share[i]) for i in np.argsort(share)[::-1][:4] if share[i] > 0.02]


def drum_grid(perc, bpm):
    hop = 64
    S = np.abs(librosa.stft(perc, n_fft=1024, hop_length=hop))
    f = librosa.fft_frequencies(sr=SR, n_fft=1024)
    first_beat = librosa.frames_to_time(
        librosa.beat.beat_track(y=perc, sr=SR, start_bpm=bpm, tightness=800)[1][0], sr=SR)
    step = 60 / bpm / 4
    t = np.arange(S.shape[1]) * hop / SR
    slot = np.round((t - first_beat) / step).astype(int) % 16
    grids = {}
    for name, lo, hi in (("kick", 40, 120), ("snare", 1500, 4000), ("hat", 7000, 11000)):
        band = np.log1p(10 * S[(f >= lo) & (f < hi)])
        flux = np.concatenate([[0], np.maximum(0, np.diff(band, axis=1)).sum(axis=0)])
        g = np.bincount(slot, weights=flux, minlength=16) / np.bincount(slot, minlength=16)
        grids[name] = g / g.max()

    # Put the strongest snare slot on beat 3; if another hit sits 8 steps away,
    # it is a 2-and-4 backbeat instead of half-time.
    shift = 8 - int(np.argmax(grids["snare"]))
    rolled = {k: np.roll(v, shift) for k, v in grids.items()}
    if rolled["snare"][0] > 0.8 * rolled["snare"][8]:
        rolled = {k: np.roll(v, 4) for k, v in rolled.items()}
        shift += 4
        feel = "full-time backbeat (snare on 2 and 4)"
    else:
        feel = "half-time (one snare per bar, on beat 3)"
    # Slot 0 of the rolled grid is the downbeat. Its first time in the file is
    # where bar 1 starts, which is what you need to line the song up in a DAW.
    downbeat = (first_beat - shift * step) % (16 * step)
    return rolled, feel, downbeat


def energy_map(y, seconds):
    S = np.abs(librosa.stft(y, n_fft=4096, hop_length=1024))
    f = librosa.fft_frequencies(sr=SR, n_fft=4096)
    t = librosa.frames_to_time(np.arange(S.shape[1]), sr=SR, hop_length=1024)
    rows = []
    for start in np.arange(0, t[-1], seconds):
        m = (t >= start) & (t < start + seconds)
        rows.append((start, [20 * np.log10(S[(f >= lo) & (f < hi)][:, m].mean() + 1e-9) for _, lo, hi in BANDS]))
    return rows


def bar(v, width=10):
    return "#" * int(round(v * width))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    args = ap.parse_args()

    y, _ = librosa.load(args.audio, sr=SR, mono=True)
    harm, perc = librosa.effects.hpss(y, margin=2.0)
    cents = 100 * librosa.estimate_tuning(y=harm, sr=SR)
    bpm, _, _ = tempo(perc)
    fits, ranked = key(harm, cents)
    grids, feel, downbeat = drum_grid(perc, bpm)
    bar_s = 240 / bpm

    print(f"duration   {len(y) / SR // 60:.0f}:{len(y) / SR % 60:04.1f}")
    print(f"tempo      {bpm:g} BPM  (feels like {bpm / 2:g} if the snare is half-time)")
    print(f"tuning     {cents:+.0f} cents from A440")
    print("key        " + ", ".join(f"{name} ({r:.2f})" for r, name in fits))
    print(f"strongest  {' '.join(ranked[:7])}   <- confirm the key by ear against these")
    print("808/bass   " + "  ".join(f"{n} {s:.0%}" for n, s in bass_notes(harm, cents))
          + "   <- the key's root is usually one of these")
    print(f"bar 1      starts {downbeat:.2f}s into the file ({downbeat / (15 / bpm):.1f} sixteenths)"
          "   <- slide the audio this far left in your DAW so bars line up")
    print(f"\ndrum feel  {feel}")
    print("           1 . . . 2 . . . 3 . . . 4 . . .")
    for name, g in grids.items():
        print(f"  {name:6s}   " + " ".join("X" if v > 0.75 else "x" if v > 0.5 else "." for v in g))
    print("  (X strong, x medium; averaged over the whole song, so fills and rolls blur out)")

    print(f"\nenergy per 4 bars ({4 * bar_s:.1f}s), dB, look for jumps to find sections")
    print("  time    " + "  ".join(f"{name:>5s}" for name, _, _ in BANDS))
    rows = energy_map(y, 4 * bar_s)
    means = np.mean([r for _, r in rows], axis=0)
    for start, r in rows:
        flags = [f"{v:5.1f}" + ("*" if abs(v - m) > 3 else " ") for v, m in zip(r, means)]
        print(f"  {int(start // 60)}:{start % 60:04.1f}  " + " ".join(flags))
    print("  (* = more than 3 dB away from that band's average: a drop-out, build or new section)")


if __name__ == "__main__":
    main()
