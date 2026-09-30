"""Shared helpers for the beat scripts: notes, MIDI export, basic synthesis, room reverb
and a master chain (soft clip + look-ahead limiter to a LUFS target).

Every function takes plain numpy arrays at SR (44.1 kHz). Stereo is shape (n, 2).
"""
from dataclasses import dataclass
from pathlib import Path

import mido
import numpy as np
from scipy import ndimage, signal

SR = 44100
PPQ = 96                  # FL Studio's default resolution
RNG = np.random.default_rng(11)


@dataclass
class Note:
    step: float           # start, in 16th notes
    length: float         # in 16th notes
    pitch: int            # MIDI note number, C4 = 60 (FL shows this as C5)
    vel: int
    glide: bool = False   # 808 only: slide into this note from the previous one


# ---------------------------------------------------------------------------
# MIDI
# ---------------------------------------------------------------------------

def midi_track(name, notes):
    events = []
    for n in notes:
        on = round(n.step * PPQ / 4)
        off = max(on + 1, round((n.step + n.length) * PPQ / 4))
        events.append((on, 1, mido.Message("note_on", note=n.pitch, velocity=n.vel)))
        events.append((off, 0, mido.Message("note_off", note=n.pitch, velocity=0)))
    events.sort(key=lambda e: (e[0], e[1]))
    track = mido.MidiTrack([mido.MetaMessage("track_name", name=name)])
    now = 0
    for tick, _, msg in events:
        track.append(msg.copy(time=tick - now))
        now = tick
    track.append(mido.MetaMessage("end_of_track", time=0))
    return track


def write_midi(path, title, bpm, tracks):
    mid = mido.MidiFile(type=1, ticks_per_beat=PPQ)
    mid.tracks.append(mido.MidiTrack([
        mido.MetaMessage("track_name", name=title),
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm)),
        mido.MetaMessage("time_signature", numerator=4, denominator=4),
        mido.MetaMessage("end_of_track", time=0),
    ]))
    for name, notes in tracks.items():
        if notes:
            mid.tracks.append(midi_track(name, notes))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    mid.save(path)


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------

def hz(pitch):
    return 440.0 * 2 ** ((pitch - 69) / 12)


def filt(x, kind, freq, order=2):
    sos = signal.butter(order, freq, btype=kind, fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def noise(n):
    return RNG.standard_normal(n)


def env_t(n):
    return np.arange(n) / SR


def saw(freq, n):
    """Band-limited (polyBLEP) sawtooth with a random start phase."""
    dt = freq / SR
    ph = (RNG.random() + dt * np.arange(n)) % 1.0
    y = 2 * ph - 1
    lo = ph < dt
    t = ph[lo] / dt
    y[lo] -= t + t - t * t - 1
    hi = ph > 1 - dt
    t = (ph[hi] - 1) / dt
    y[hi] -= t * t + t + t + 1
    return y


def stereo(x):
    return np.stack([x, x], axis=1) if x.ndim == 1 else x


def padded(x, seconds):
    return np.concatenate([stereo(x), np.zeros((int(seconds * SR), 2))])


def fade_out(x, seconds=0.05):
    n = int(seconds * SR)
    x = x.copy()
    x[-n:] *= np.linspace(1, 0, n)[:, None] if x.ndim == 2 else np.linspace(1, 0, n)
    return x


def place(bus, x, seconds, pan=0.0):
    i = int(round(seconds * SR))
    if x.ndim == 1:
        a = (pan + 1) * np.pi / 4
        x = np.stack([x * np.cos(a), x * np.sin(a)], axis=1) * np.sqrt(2)
    n = min(len(x), len(bus) - i)
    if n > 0:
        bus[i:i + n] += x[:n]


def rms_db(x):
    active = np.abs(x).max(axis=1) > 1e-4 if x.ndim == 2 else np.abs(x) > 1e-4
    return 20 * np.log10(np.sqrt(np.mean(x[active] ** 2)) + 1e-12)


def make_ir(seconds=1.0, tau=0.08, predelay=0.02, lowpass=6500):
    """Decorrelated stereo room. RT60 is about 6.9 * tau."""
    n = int(seconds * SR)
    t = env_t(n)
    ir = noise(n * 2).reshape(n, 2) * np.exp(-t / tau)[:, None]
    pd = int(predelay * SR)
    ir[:pd] = 0
    ir[pd:pd + int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))[:, None]
    ir = filt(ir, "lowpass", lowpass)
    return ir / np.sqrt((ir ** 2).sum(axis=0))


def reverb(x, wet, ir):
    mono = stereo(x).mean(axis=1)
    wet_sig = np.stack([signal.fftconvolve(mono, ir[:, ch])[: len(mono)] for ch in (0, 1)], axis=1)
    return stereo(x) + wet * wet_sig


# ---------------------------------------------------------------------------
# Master
# ---------------------------------------------------------------------------

def lufs(x):
    import pyloudnorm
    return pyloudnorm.Meter(SR).integrated_loudness(x)


def true_peak_db(x):
    return 20 * np.log10(np.abs(signal.resample_poly(x, 4, 1, axis=0)).max())


def limit(x, ceiling, window=0.02):
    """Look-ahead brickwall: the gain never exceeds what any sample within a window needs."""
    need = np.minimum(1, ceiling / np.maximum(np.abs(x).max(axis=1), 1e-9))
    w = int(window * SR)
    gain = ndimage.minimum_filter1d(need, 2 * w + 1)
    gain = ndimage.uniform_filter1d(gain, w)
    return x * gain[:, None]


def master(mix, target_lufs, ceiling_dbtp=-1.0):
    """Soft clip, then limit, raising the drive until the master reaches target_lufs."""
    mix = mix / np.abs(mix).max()
    ceiling = 10 ** (ceiling_dbtp / 20)
    drive = 1.0
    for _ in range(12):
        y = np.tanh(drive * mix) / np.tanh(drive) * 10 ** (-0.3 / 20)
        y = limit(y, ceiling)
        tp = true_peak_db(y)
        if tp > ceiling_dbtp:
            y = limit(y, ceiling * 10 ** ((ceiling_dbtp - tp) / 20))
        loud = lufs(y)
        if abs(loud - target_lufs) < 0.1:
            break
        drive *= 10 ** ((target_lufs - loud) / 20)
    tp = true_peak_db(y)
    return y * 10 ** (min(0, ceiling_dbtp - tp) / 20)
