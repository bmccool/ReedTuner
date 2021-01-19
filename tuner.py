from fft2 import FFT_Sampler

import time
import board
import digitalio

TUNING_FREQUENCY = 480
SMALL_STEP = 2
SMALL_SLEEP = .25
MED_STEP = 20
MED_SLEEP = 1
BIG_STEP = 50
BIG_SLEEP = 3

STEPPER_DELAY = 4 / 1000.0 #milliseconds, TODO test this to determine which is best, I think 4 was good before

enable_pin = digitalio.DigitalInOut(board.D18)
coil_A_1_pin = digitalio.DigitalInOut(board.D4)
coil_A_2_pin = digitalio.DigitalInOut(board.D17)
coil_B_1_pin = digitalio.DigitalInOut(board.D23)
coil_B_2_pin = digitalio.DigitalInOut(board.D24)

enable_pin.direction = digitalio.Direction.OUTPUT
coil_A_1_pin.direction = digitalio.Direction.OUTPUT
coil_A_2_pin.direction = digitalio.Direction.OUTPUT
coil_B_1_pin.direction = digitalio.Direction.OUTPUT
coil_B_2_pin.direction = digitalio.Direction.OUTPUT

enable_pin.value = True

def forward(delay, steps):
    i = 0
    while i in range(0, steps):
        setStep(1, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(1, 0, 0, 1)
        time.sleep(delay)
        i += 1

def backwards(delay, steps):
    i = 0
    while i in range(0, steps):
        setStep(1, 0, 0, 1)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(1, 0, 1, 0)
        time.sleep(delay)
        i += 1


def setStep(w1, w2, w3, w4):
    coil_A_1_pin.value = w1
    coil_A_2_pin.value = w2
    coil_B_1_pin.value = w3
    coil_B_2_pin.value = w4


if __name__ == "__main__":
    ffts = FFT_Sampler()
    ffts.start()
    import time
    sleep_time = 1 #TODO probably make this a class or enum sleep time.short, med, long...
    while True:
        try:
            #time.sleep(sleep_time) #TODO, unless the motor controller is threaded, we shouldn't need to sleep
            if ffts.freq:
                print('freq: {:7.2f} Hz'.format(ffts.freq))
                difference = abs(ffts.freq - TUNING_FREQUENCY)
                sleep_time = SMALL_SLEEP
                steps = SMALL_STEP
                if difference >  0.5: #TODO magic number
                    sleep_time = MED_SLEEP
                    steps = MED_STEP
                    if difference > 5: #TODO magic number
                        sleep_time = BIG_SLEEP
                        steps = BIG_STEP


                status = "{} / {} Hz".format(str(ffts.freq), str(TUNING_FREQUENCY))
                # Adjust pressure!
                if ffts.freq > TUNING_FREQUENCY:
                    print(status + " Tuning Down {} steps, with {} delay".format(str(steps), str(STEPPER_DELAY)))
                    backwards(STEPPER_DELAY, steps)
                else:
                    print(status + "   Tuning Up {} steps, with {} delay".format(str(steps), str(STEPPER_DELAY)))
                    forward(STEPPER_DELAY, steps)
            else:
                print("No frequency measured yet...")
        except KeyboardInterrupt as e:
            print("We should be done")
            ffts.done = True
            break