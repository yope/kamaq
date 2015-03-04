Kamaq
=====

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

This project is currently in an early stage and in heavy development.
The software can control 4 motors (X, Y, Z and Extruder), read 3 endswitches
and control the extruder temperature. The G-Code interpreter is still very
simple, but the software is already able to succesfully print an object from a
G-Code-file generated with repsnapper.

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
such as the RepRap Prusa i3 for example, but it may also be suited for other
applications requiring control of motors from G-Codes.

5. Required hardware
--------------------

5.1. Audio device
-----------------

The sound-card will work better if modified slightly, by shorting the DC-
blocking capacitors at the output. On many USB audio devices this is a
trivial task to do. For example the Sweex SC016 contains a C-Media CM6206
7.1 channel USB audio codec. Datasheets can easily be found via Google, and
they contain reference schematics that will be very similar to most
implementations of popular 7.1 USB audio devices that use this chip.
Most of the time they will use cheap through-hole electrolytic capacitors,
that are very easy to short out.

5.2. Audio amplifiers
---------------------

Bipolar 2-phase stepper-motors are best driven by a controlled current.
Although in theory, having a good model of the motor that takes into account
inductance and back-EMF at different speeds, one could calculate the correct
voltage-waveform to be applied to the motor windings and just use a voltage-
amplifier wich might be a little easier to build (specially when using class-D
amplifier IC's).
For my first hardware implementation, I built very simple class-B amplifiers
with current-feedback based on a bunch of TDA2030A I had laying around. This
version didn't require any motor modeling.
The second version which I am currently using is based on class-D audio
amplifier IC's, which save a lot of space and simplify the power supply
enormously. The class-D amplifiers lack current-feedback though, so I am
starting to add software support for voltage control also.

5.3. Heater control
-------------------

To control heater elements (such as for the extruder or the heated-bed of a
3D-printer), simple low-side switches with power-MOSFETS with very low-Rdson
will be perfect.
Temperature feedback is best implemented via simple A/D converters that support
HW-mon drivers, such as the ADS1015 from TI, which has mainline-linux support.

5.4. Hardware implementation
----------------------------

I have implemented all the needed hardware to control a 3D printer using this
software in very little time and effort. If there is enough interest I might
open-source the hardware (Kicad schematics and layout) too, but it is really
simple and straight-forward stuff right now hacked together in very little time.

6. Tools
--------

 * kamaq.py: Main application, starts the web-server.

 * grunner.py: This command-line tool can execude whole G-Code files or single
   movements by specifying relative distance on each axis (including extruder)
   on the command-line. It supports homing on endswitches and extruder
   temperature control. Currently not functional. Use the web-server instead.

 * set_current.py: Very simple tool that sets constant motor currents for all
   motors specified on the command-line. Can be used for adjusting motor
   current via the audio mixer. For each motor, two values are specified from
   -30000 to 30000, corresponding to the currents through each of the two
   coils. If less than 8 values (for 4 motors) are specified, the rest is
   assumed to be 0.

 * adjust_bed.sh: A script that aids in adjusting the for corners of the print-
   bed.

 * clean_extruder.sh: Move to a suitable position (high enough Z), heat
   extruder and start extruding a few cm.

7. TODO:
--------

Features that may or may not be implemented in the near or far future:

 * Implement pause and resume-from-layer-X.
 * Implemet G-code control via SSH or Serial port (to be able to use traditional
   printer control software).

