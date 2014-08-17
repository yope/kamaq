G-Runner
========

1. Introduction
---------------

This project is an implementation of a G-Code interpreter that can directly
control stepper-motors via an audio device, and receive feedback from end-
switches connected via GPIO pins. It can also control heaters connected via
GPIO outputs (low-frequency PWM) and feedback via lm-sensors interface.

2. Platform requirements
------------------------

This should be able to run on any embedded linux platform such as the beagle-
board, beagle-bone or the raspberry-pi with a suitable audio device, GPIO and
HWmon compatible A/D converters for temperature measurement.
The sound device should have twice the number of channels as the number of
motors that need to be controlled. For example a cheap 7.1 USB audio device
will be enough for controlling 4 stepper-motors.

3. Main application
-------------------

Of course the main goal for this project is controlling 3D-printer hardware,
such as the RepRap Prusa i3 for example.

4. Required hardware
--------------------

4.1 Audio device
----------------

The sound-card will work better if modified slightly, by shorting the DC-
blocking capacitors at the output. On many USB audio devices this is a
trivial task to do. For example the Sweex SC016 contains a C-Media CM6206
7.1 channel USB audio codec. Datasheets can easily be found via Google, and
they contain reference schematics that will be very similar to most
implementations of popular 7.1 USB audio devices that use this chip.
Most of the time they will use cheap through-hole electrolytic capacitors,
that are very easy to short out.

4.2 Current amplifiers
----------------------

Bipolar 2-phase stepper-motors are best driven by a controlled current.
Although in theory, having a good model of the motor that takes into account
inductance and back-EMF at different speeds, one could calculate the correct
voltage-waveform to be applied to the motor windings and just use a voltage-
amplifier wich might be a little easier to build (specially when using class-D
amplifier IC's).
In my case I preferred to build very simple class-B amplifiers with current-
feedback based on a bunch of TDA2030A I had laying around, so I have not
included for motor-modelling of any kind in order to support voltage-
amplifiers. If you think this is a cool idea, feel free to contribute ;-)

