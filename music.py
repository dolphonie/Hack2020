# Created by Patrick Kao
import subprocess
from time import sleep

import numpy as np
import pandas as pd
import pygame
import pygame.mixer
from midiutil import MIDIFile
from scipy import signal

FILE_PATH = "~/Desktop/test.midi"
SONG_LEN = 15
TOTAL_RANGE = 35
INSTRUMENTS = [0, 42, 72]
BPM = 120
MAX_LEN = int(SONG_LEN * BPM / 60 * 2)  # 2 for eighth notes

def get_pitch(input):
    """

    :param input: number from 0 to
    :return:
    """
    pitches = [36]
    for i in range(5):
        last = len(pitches) - 1
        pitches.append(pitches[last] + 2)
        pitches.append(pitches[last] + 4)
        pitches.append(pitches[last] + 5)
        pitches.append(pitches[last] + 7)
        pitches.append(pitches[last] + 9)
        pitches.append(pitches[last] + 11)
        pitches.append(pitches[last] + 12)
    return pitches[int(input)]


def process_midi(midi_file, play=False, output_wav=None):
    if play:
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            sleep(1)
    if output_wav is not None:
        out_type = "wav"
        sf2 = "Hack2020/orchestra.sf2"
        subprocess.call(['fluidsynth', '-T', out_type, '-F', output_wav, '-ni', sf2, midi_file])
    print("Done!")


def percentile(input_list, element):
    min_el = min(input_list)
    max_el = max(input_list)
    return (element - min_el) / (max_el - min_el)


def write_midi(input_data, output_file, mode="pitch"):
    midi = MIDIFile(1)
    midi.addTrackName(track=0, time=0, trackName="Sample Track")
    midi.addTempo(track=0, time=0, tempo=BPM)

    for track in range(len(input_data)):
        if mode == "both" and track >= len(input_data) // 2:
            break

        midi.addProgramChange(0, track, 0, program=INSTRUMENTS[track])
        track_data = input_data[track]
        time_per_note = SONG_LEN / len(track_data)
        for i, note in enumerate(track_data):
            z = percentile(track_data, note)

            if mode == "both":
                volume_track = input_data[track + len(input_data) // 2]
                index = int(i * len(volume_track) / len(track_data))
                volume_z = percentile(volume_track, volume_track[index])
                volume = int(volume_z * 100) + 1
                assert 127 > volume >= 0
                midi.addNote(track=0,
                             channel=track,
                             pitch=get_pitch(z * TOTAL_RANGE),
                             time=time_per_note * i,
                             duration=time_per_note,
                             volume=volume)
            elif mode == "pitch":
                midi.addNote(track=0,
                             channel=track,
                             pitch=get_pitch(z * TOTAL_RANGE),
                             time=time_per_note * i,
                             duration=time_per_note,
                             volume=100)
            elif mode == "volume":
                midi.addNote(track=0,
                             channel=track,
                             pitch=60 + 12 * track,
                             time=time_per_note * i,
                             duration=time_per_note,
                             volume=int(z * 100))

    with open(output_file, 'wb') as binfile:
        midi.writeFile(binfile)


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def parse_input(input_file):
    pandas_file = pd.read_csv(input_file)
    data = np.asarray(pandas_file)
    proc_data = []
    # moving average
    for track in range(data.shape[1]):
        track_data = data[:, track]
        track_data = track_data[~np.isnan(track_data)]
        if len(track_data) > MAX_LEN:
            print(f"Track too long. Resampling from {len(track_data)} to {MAX_LEN} samples")
            track_data = moving_average(track_data)
            track_data = signal.resample(track_data, MAX_LEN)

        proc_data.append(track_data)

    return proc_data


if __name__ == "__main__":
    output_file = "output.mid"
    input_data = parse_input("scales.csv")
    write_midi(input_data, output_file, mode="both")
    process_midi(output_file, play=True, output_wav="output.wav")
