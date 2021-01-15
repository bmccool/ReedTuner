#! /usr/bin/env python
######################################################################
# tuner.py - a minimal command-line guitar/ukulele tuner in Python.
# Requires numpy and pyaudio.
######################################################################
# Author:  Matt Zucker
# Date:    July 2016
# License: Creative Commons Attribution-ShareAlike 3.0
#          https://creativecommons.org/licenses/by-sa/3.0/us/
######################################################################

import numpy as np
import pyaudio
import threading

######################################################################
# Feel free to play with these numbers. Might want to change NOTE_MIN
# and NOTE_MAX especially for guitar/bass. Probably want to keep
# FRAME_SIZE and FRAMES_PER_FFT to be powers of two.

NOTE_MIN = 35       # B1
NOTE_MAX = 72       # C5
FSAMP = 22050       # Sampling frequency in Hz
FRAME_SIZE = 2048   # How many samples per frame?
FRAMES_PER_FFT = 16 # FFT takes average across how many frames?

######################################################################
# Derived quantities from constants above. Note that as
# SAMPLES_PER_FFT goes up, the frequency step size decreases (so
# resolution increases); however, it will incur more delay to process
# new sounds.

SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT

######################################################################
# For printing out notes

NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()

######################################################################
# These three functions are based upon this very useful webpage:
# https://newt.phys.unsw.edu.au/jw/notes.html

def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(n/12 - 1)

######################################################################
# Ok, ready to go now.

# Get min/max index within FFT of notes we care about.
# See docs for numpy.rfftfreq()
def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP
imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))

class FFT_Sampler(threading.Thread):
    def __init__(self): #Do we need this?  We can just use the base class init, right?
        super().__init__()
        self.freq = None
        self.done = False # TODO there should be a self.exit() we can call instead of doing this, but it will work for now.

    def run(self):
        print("Starting fft thread...")
        self.run_fft()
        print("Exiting fft thread...")

    def run_fft(self):
        #TODO How to stop this?  Do we need to stop it?
        # Allocate space to run an FFT. 
        buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
        num_frames = 0
        
        # Initialize audio
        stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                        channels=1,
                                        rate=FSAMP,
                                        input=True,
                                        frames_per_buffer=FRAME_SIZE)
        
        stream.start_stream()
        
        # Create Hanning window function
        window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))
        
        # Print initial text
        print('sampling at {} Hz with max resolution of {} Hz'.format(FSAMP, FREQ_STEP))
        
        # As long as we are getting data:
        while(stream.is_active() and not self.done):
        
            # Shift the buffer down and new data in
            buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
            buf[-FRAME_SIZE:] = np.fromstring(stream.read(FRAME_SIZE), np.int16)
        
            # Run the FFT on the windowed buffer
            fft = np.fft.rfft(buf * window)
        
            # Get frequency of maximum response in range
            freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP
        
            # Get note number and nearest note
            n = freq_to_number(freq)
            n0 = int(round(n))
        
            # Console output once we have a full buffer
            num_frames += 1
        
            if num_frames >= FRAMES_PER_FFT:
                self.freq = freq

if __name__ == "__main__":
    ffts = FFT_Sampler()
    ffts.start()
    import time
    while True:
        time.sleep(1)
        if ffts.freq:
            print('freq: {:7.2f} Hz'.format(ffts.freq))
        else:
            print("No frequency measured yet...")