G-Runner
========

1. Introduction
---------------

This project is an implementation of a G-Code interpreter that can directly
control stepper-motors via an audio device, and receive feedback from end-
switches connected via GPIO pins. It can also control heaters connected via
GPIO outputs (low-frequency PWM) and feedback via lm-sensors interface.
Why do it like this when there are already so many different hard- and software
projects dedicated to 3D printers (RepRap and all its derivates)?
Well, because as is the case with all engineers, I always know better ;-)

2. Status of this project
-------------------------

This project is currently in a very early stage and in heavy development.
The software is able to drive 4 stepper-motors currently from data read out
of a supplied G-Code command file. No support for heaters or end-stops yet.
Most G-codes are ignored, only G1/G0 movements are executed right now.

3. Platform requirements
------------------------

This should be able to run on any embedded linux platform such as the beagle-
board, beagle-bone or the raspberry-pi with a suitable audio device, GPIO and
HWmon compatible A/D converters for temperature measurement.
The sound device should have twice the number of channels as the number of
motors that need to be controlled. For example a cheap 7.1 USB audio device
will be enough for controlling 4 stepper-motors.

4. Main application
-------------------

Of course the main goal for this project is controlling 3D-printer hardware,
such as the RepRap Prusa i3 for example, but it may very well be suited for
other applications.

5. Required hardware
--------------------

5.1 Audio device
----------------

The sound-card will work better if modified slightly, by shorting the DC-
blocking capacitors at the output. On many USB audio devices this is a
trivial task to do. For example the Sweex SC016 contains a C-Media CM6206
7.1 channel USB audio codec. Datasheets can easily be found via Google, and
they contain reference schematics that will be very similar to most
implementations of popular 7.1 USB audio devices that use this chip.
Most of the time they will use cheap through-hole electrolytic capacitors,
that are very easy to short out.

5.2 Current amplifiers
----------------------

Bipolar 2-phase stepper-motors are best driven by a controlled current.
Although in theory, having a good model of the motor that takes into account
inductance and back-EMF at different speeds, one could calculate the correct
voltage-waveform to be applied to the motor windings and just use a voltage-
amplifier wich might be a little easier to build (specially when using class-D
amplifier IC's).
In my case I preferred to build very simple class-B amplifiers with current-
feedback based on a bunch of TDA2030A I had laying around, so I have not
included support for motor-modelling of any kind in order to support voltage-
amplifiers. If you think this is a cool idea, feel free to contribute ;-)

5.3 Heater control
------------------

To control heater elements (such as for the extruder or the heated-bed of a
3D-printer), simple low-side switches with power-MOSFETS with very low-Rdson
will be perfect.
Temperature feedback is best implemented via simple A/D converters that support
HW-mon drivers, such as the ADS1015 from TI, which has mainline-linux support.

5.4 Hardware implementation
---------------------------

I have implemented all the needed hardware to control a 3D printer using this
software in very little time and effort. If there is enough interest I might
open-source the hardware (Kicad schematics and layout) too, but it is really
simple and straight-forward stuff right now hacked together in very little time.

