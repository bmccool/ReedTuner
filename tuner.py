from fft2 import FFT_Sampler

TUNING_FREQUENCY = 480

if __name__ == "__main__":
    ffts = FFT_Sampler()
    ffts.start()
    import time
    while True:
        try:
            time.sleep(1)
            if ffts.freq:
                print('freq: {:7.2f} Hz'.format(ffts.freq))
                if ffts.freq > TUNING_FREQUENCY:
                    print("Tuning Down")
                else:
                    print("Tuning Up")
            else:
                print("No frequency measured yet...")
        except KeyboardInterrupt as e:
            print("We should be done")
            ffts.done = True
            break