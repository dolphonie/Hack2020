# Created by Patrick Kao
from time import sleep

import numpy as np
import pandas as pd
import pygame
import pygame.mixer
from midiutil import MIDIFile
from midi2audio import FluidSynth
import subprocess

FILE_PATH = "~/Desktop/test.midi"
SONG_LEN = 10
pitches = None
TOTAL_RANGE = 35
INSTRUMENTS = [0, 42, 72, 57, 74]

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
        pitches.append(pitches[last] + 6)
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
        sf2 = "piano.sf2"
        subprocess.call(['fluidsynth', '-T', out_type, '-F', output_wav, '-ni', sf2, midi_file])
    print("Done!")


def write_midi(input, output_file):
    bpm = 60

    midi = MIDIFile(1)
    midi.addTrackName(track=0, time=0, trackName="Sample Track")
    midi.addTempo(track=0, time=0, tempo=bpm)
    midi.addProgramChange(0, 0, 0, program=42)
    for track in range(input.shape[1]):
        track_data = input[:, track]
        track_data = track_data[~np.isnan(track_data)]
        min_note = min(track_data)
        max_note = max(track_data)
        time_per_note = SONG_LEN / len(track_data)
        for i, note in enumerate(track_data):
            z_score = (note - min_note) / (max_note - min_note)
            midi.addNote(track=0,
                         channel=track,
                         pitch=get_pitch(z_score * TOTAL_RANGE),
                         time=time_per_note * i,
                         duration=time_per_note,
                         volume=100)

    with open(output_file, 'wb') as binfile:
        midi.writeFile(binfile)


def parse_input(input_file):
    pandas_file = pd.read_csv(input_file)
    data = np.asarray(pandas_file)
    # TODO: normalize data
    return data


if __name__ == "__main__":
    output_file = "output.mid"
    input = parse_input("scales.csv")
    write_midi(input, output_file)
    process_midi(output_file, play=False, output_wav="output.wav")
