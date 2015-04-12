EESchema Schematic File Version 2
LIBS:audio2
LIBS:power
LIBS:device
LIBS:TO263_NMOS
LIBS:transistors
LIBS:conn
LIBS:linear2
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:special
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
EELAYER 27 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 4
Title ""
Date "12 apr 2015"
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Sheet
S 8500 1750 900  900 
U 544155F9
F0 "Driver 1" 50
F1 "driver.sch" 50
F2 "VIN" I L 8500 1900 60 
F3 "VCM" B L 8500 2100 60 
F4 "SDN" I L 8500 2300 60 
F5 "MUTE" I L 8500 2500 60 
F6 "OUTP" O R 9400 1900 60 
F7 "OUTN" O R 9400 2100 60 
$EndSheet
$Sheet
S 8500 3750 900  900 
U 5442931E
F0 "Driver 2" 50
F1 "driver.sch" 50
F2 "VIN" I L 8500 3900 60 
F3 "VCM" B L 8500 4100 60 
F4 "SDN" I L 8500 4300 60 
F5 "MUTE" I L 8500 4500 60 
F6 "OUTP" O R 9400 3900 60 
F7 "OUTN" O R 9400 4100 60 
$EndSheet
$Comp
L TL074 U101
U 2 1 544294F6
P 2300 6100
F 0 "U101" H 2350 6300 60  0000 C CNN
F 1 "TLV2464" H 2450 5900 50  0000 C CNN
F 2 "" H 2300 6100 60  0000 C CNN
F 3 "" H 2300 6100 60  0000 C CNN
	2    2300 6100
	1    0    0    -1  
$EndComp
$Comp
L TL074 U101
U 3 1 54429544
P 6400 1900
F 0 "U101" H 6450 2100 60  0000 C CNN
F 1 "TLV2464" H 6550 1700 50  0000 C CNN
F 2 "" H 6400 1900 60  0000 C CNN
F 3 "" H 6400 1900 60  0000 C CNN
	3    6400 1900
	1    0    0    -1  
$EndComp
$Comp
L TL074 U101
U 4 1 5442956C
P 6400 3900
F 0 "U101" H 6450 4100 60  0000 C CNN
F 1 "TLV2464" H 6550 3700 50  0000 C CNN
F 2 "" H 6400 3900 60  0000 C CNN
F 3 "" H 6400 3900 60  0000 C CNN
	4    6400 3900
	1    0    0    -1  
$EndComp
$Comp
L R R116
U 1 1 54429686
P 7450 1900
F 0 "R116" V 7530 1900 40  0000 C CNN
F 1 "1K" V 7457 1901 40  0000 C CNN
F 2 "~" V 7380 1900 30  0000 C CNN
F 3 "~" H 7450 1900 30  0000 C CNN
	1    7450 1900
	0    -1   -1   0   
$EndComp
$Comp
L C C105
U 1 1 54429822
P 7800 2200
F 0 "C105" H 7800 2300 40  0000 L CNN
F 1 "22N" H 7806 2115 40  0000 L CNN
F 2 "~" H 7838 2050 30  0000 C CNN
F 3 "~" H 7800 2200 60  0000 C CNN
	1    7800 2200
	1    0    0    -1  
$EndComp
$Comp
L R R114
U 1 1 54429845
P 6450 2300
F 0 "R114" V 6530 2300 40  0000 C CNN
F 1 "100K" V 6457 2301 40  0000 C CNN
F 2 "~" V 6380 2300 30  0000 C CNN
F 3 "~" H 6450 2300 30  0000 C CNN
	1    6450 2300
	0    -1   -1   0   
$EndComp
$Comp
L R R115
U 1 1 54429887
P 6450 2500
F 0 "R115" V 6530 2500 40  0000 C CNN
F 1 "100K" V 6457 2501 40  0000 C CNN
F 2 "~" V 6380 2500 30  0000 C CNN
F 3 "~" H 6450 2500 30  0000 C CNN
	1    6450 2500
	0    -1   -1   0   
$EndComp
$Comp
L CONN_4 P104
U 1 1 54429943
P 10950 2850
F 0 "P104" V 10900 2850 50  0000 C CNN
F 1 "CONN_4" V 11000 2850 50  0000 C CNN
F 2 "" H 10950 2850 60  0000 C CNN
F 3 "" H 10950 2850 60  0000 C CNN
	1    10950 2850
	1    0    0    -1  
$EndComp
Wire Wire Line
	9400 1900 10500 1900
Wire Wire Line
	10500 1900 10500 2700
Wire Wire Line
	10500 2700 10600 2700
$Comp
L R R122
U 1 1 54429978
P 9950 2100
F 0 "R122" V 10030 2100 40  0000 C CNN
F 1 "1" V 9957 2101 40  0000 C CNN
F 2 "~" V 9880 2100 30  0000 C CNN
F 3 "~" H 9950 2100 30  0000 C CNN
	1    9950 2100
	0    -1   -1   0   
$EndComp
Wire Wire Line
	9400 2100 9700 2100
Wire Wire Line
	10200 2100 10400 2100
Wire Wire Line
	10400 2100 10400 2800
Wire Wire Line
	10400 2800 10600 2800
Wire Wire Line
	6700 2500 8000 2500
Wire Wire Line
	8000 2500 8000 2100
Wire Wire Line
	8000 2100 8500 2100
Wire Wire Line
	7700 1900 8500 1900
Wire Wire Line
	7800 2000 7800 1900
Connection ~ 7800 1900
Wire Wire Line
	7800 2400 7800 2500
Connection ~ 7800 2500
Wire Wire Line
	6900 1900 7200 1900
Wire Wire Line
	5700 2500 6200 2500
Wire Wire Line
	5600 1800 5900 1800
Wire Wire Line
	5700 2500 5700 1800
Wire Wire Line
	5600 2000 5900 2000
Wire Wire Line
	5800 2300 6200 2300
Wire Wire Line
	6700 2300 7000 2300
Wire Wire Line
	7000 2300 7000 1900
Connection ~ 7000 1900
$Comp
L R R108
U 1 1 5442A244
P 5350 1800
F 0 "R108" V 5430 1800 40  0000 C CNN
F 1 "22K" V 5357 1801 40  0000 C CNN
F 2 "~" V 5280 1800 30  0000 C CNN
F 3 "~" H 5350 1800 30  0000 C CNN
	1    5350 1800
	0    -1   -1   0   
$EndComp
$Comp
L R R109
U 1 1 5442A27C
P 5350 2000
F 0 "R109" V 5430 2000 40  0000 C CNN
F 1 "22K" V 5357 2001 40  0000 C CNN
F 2 "~" V 5280 2000 30  0000 C CNN
F 3 "~" H 5350 2000 30  0000 C CNN
	1    5350 2000
	0    -1   -1   0   
$EndComp
Connection ~ 5700 1800
Connection ~ 5800 2000
Wire Wire Line
	4800 1800 5100 1800
Wire Wire Line
	3800 1900 3700 1900
Wire Wire Line
	3700 1900 3700 2300
Wire Wire Line
	3700 2300 4900 2300
Wire Wire Line
	4900 1800 4900 5300
Connection ~ 4900 1800
$Comp
L GND #PWR01
U 1 1 5442AB94
P 4200 2500
F 0 "#PWR01" H 4200 2500 30  0001 C CNN
F 1 "GND" H 4200 2430 30  0001 C CNN
F 2 "" H 4200 2500 60  0000 C CNN
F 3 "" H 4200 2500 60  0000 C CNN
	1    4200 2500
	1    0    0    -1  
$EndComp
$Comp
L +5V #PWR02
U 1 1 5442ABA3
P 4200 1000
F 0 "#PWR02" H 4200 1090 20  0001 C CNN
F 1 "+5V" H 4200 1090 30  0000 C CNN
F 2 "" H 4200 1000 60  0000 C CNN
F 3 "" H 4200 1000 60  0000 C CNN
	1    4200 1000
	1    0    0    -1  
$EndComp
Wire Wire Line
	4200 1000 4200 1400
Wire Wire Line
	4200 2200 4200 2500
$Comp
L C C104
U 1 1 5442AD36
P 4600 1400
F 0 "C104" H 4600 1500 40  0000 L CNN
F 1 "100N" H 4606 1315 40  0000 L CNN
F 2 "~" H 4638 1250 30  0000 C CNN
F 3 "~" H 4600 1400 60  0000 C CNN
	1    4600 1400
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR03
U 1 1 5442AD4F
P 4600 1700
F 0 "#PWR03" H 4600 1700 30  0001 C CNN
F 1 "GND" H 4600 1630 30  0001 C CNN
F 2 "" H 4600 1700 60  0000 C CNN
F 3 "" H 4600 1700 60  0000 C CNN
	1    4600 1700
	1    0    0    -1  
$EndComp
Wire Wire Line
	4600 1600 4600 1700
Wire Wire Line
	4600 1200 4600 1100
Wire Wire Line
	4600 1100 4200 1100
Connection ~ 4200 1100
$Comp
L R R123
U 1 1 5442B455
P 9950 4100
F 0 "R123" V 10030 4100 40  0000 C CNN
F 1 "1" V 9957 4101 40  0000 C CNN
F 2 "~" V 9880 4100 30  0000 C CNN
F 3 "~" H 9950 4100 30  0000 C CNN
	1    9950 4100
	0    -1   -1   0   
$EndComp
Wire Wire Line
	9400 4100 9700 4100
Wire Wire Line
	10200 4100 10500 4100
Wire Wire Line
	10500 4100 10500 3000
Wire Wire Line
	10500 3000 10600 3000
Wire Wire Line
	10600 2900 10400 2900
Wire Wire Line
	10400 2900 10400 3900
Wire Wire Line
	10400 3900 9400 3900
$Comp
L R R117
U 1 1 5442BA34
P 7450 3900
F 0 "R117" V 7530 3900 40  0000 C CNN
F 1 "1K" V 7457 3901 40  0000 C CNN
F 2 "~" V 7380 3900 30  0000 C CNN
F 3 "~" H 7450 3900 30  0000 C CNN
	1    7450 3900
	0    -1   -1   0   
$EndComp
$Comp
L R R112
U 1 1 5442BA6C
P 6350 4300
F 0 "R112" V 6430 4300 40  0000 C CNN
F 1 "100K" V 6357 4301 40  0000 C CNN
F 2 "~" V 6280 4300 30  0000 C CNN
F 3 "~" H 6350 4300 30  0000 C CNN
	1    6350 4300
	0    -1   -1   0   
$EndComp
$Comp
L R R113
U 1 1 5442BAA4
P 6350 4500
F 0 "R113" V 6430 4500 40  0000 C CNN
F 1 "100K" V 6357 4501 40  0000 C CNN
F 2 "~" V 6280 4500 30  0000 C CNN
F 3 "~" H 6350 4500 30  0000 C CNN
	1    6350 4500
	0    -1   -1   0   
$EndComp
$Comp
L C C106
U 1 1 5442BB4C
P 7800 4200
F 0 "C106" H 7800 4300 40  0000 L CNN
F 1 "22N" H 7806 4115 40  0000 L CNN
F 2 "~" H 7838 4050 30  0000 C CNN
F 3 "~" H 7800 4200 60  0000 C CNN
	1    7800 4200
	1    0    0    -1  
$EndComp
$Comp
L R R110
U 1 1 5442BB65
P 5350 3800
F 0 "R110" V 5430 3800 40  0000 C CNN
F 1 "22K" V 5357 3801 40  0000 C CNN
F 2 "~" V 5280 3800 30  0000 C CNN
F 3 "~" H 5350 3800 30  0000 C CNN
	1    5350 3800
	0    -1   -1   0   
$EndComp
$Comp
L R R111
U 1 1 5442BBA7
P 5350 4000
F 0 "R111" V 5430 4000 40  0000 C CNN
F 1 "22K" V 5357 4001 40  0000 C CNN
F 2 "~" V 5280 4000 30  0000 C CNN
F 3 "~" H 5350 4000 30  0000 C CNN
	1    5350 4000
	0    -1   -1   0   
$EndComp
Wire Wire Line
	6900 3900 7200 3900
Wire Wire Line
	7700 3900 8500 3900
Wire Wire Line
	7800 4000 7800 3900
Connection ~ 7800 3900
Wire Wire Line
	7800 4400 7800 4500
Wire Wire Line
	6600 4500 8000 4500
Wire Wire Line
	8000 4500 8000 4100
Wire Wire Line
	8000 4100 8500 4100
Connection ~ 7800 4500
Wire Wire Line
	6600 4300 7000 4300
Wire Wire Line
	7000 4300 7000 3900
Connection ~ 7000 3900
Wire Wire Line
	6100 4300 5800 4300
Wire Wire Line
	5600 4000 5900 4000
Wire Wire Line
	6100 4500 5700 4500
Wire Wire Line
	5700 4500 5700 3800
Wire Wire Line
	5600 3800 5900 3800
Connection ~ 5700 3800
Connection ~ 5800 4000
Wire Wire Line
	4900 3800 5100 3800
Connection ~ 4900 2300
$Comp
L C C101
U 1 1 5442C691
P 3400 2000
F 0 "C101" H 3400 2100 40  0000 L CNN
F 1 "100N" H 3406 1915 40  0000 L CNN
F 2 "~" H 3438 1850 30  0000 C CNN
F 3 "~" H 3400 2000 60  0000 C CNN
	1    3400 2000
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR04
U 1 1 5442C6AA
P 3400 2500
F 0 "#PWR04" H 3400 2500 30  0001 C CNN
F 1 "GND" H 3400 2430 30  0001 C CNN
F 2 "" H 3400 2500 60  0000 C CNN
F 3 "" H 3400 2500 60  0000 C CNN
	1    3400 2500
	1    0    0    -1  
$EndComp
Wire Wire Line
	3400 2200 3400 2500
Wire Wire Line
	3400 1700 3400 1800
Wire Wire Line
	2350 1700 3800 1700
$Comp
L CONN_3 K102
U 1 1 5442CC1F
P 2550 3500
F 0 "K102" V 2500 3500 50  0000 C CNN
F 1 "IN" V 2600 3500 40  0000 C CNN
F 2 "" H 2550 3500 60  0000 C CNN
F 3 "" H 2550 3500 60  0000 C CNN
	1    2550 3500
	-1   0    0    -1  
$EndComp
$Comp
L R R104
U 1 1 5442CD2E
P 3450 3400
F 0 "R104" V 3530 3400 40  0000 C CNN
F 1 "2K2" V 3457 3401 40  0000 C CNN
F 2 "~" V 3380 3400 30  0000 C CNN
F 3 "~" H 3450 3400 30  0000 C CNN
	1    3450 3400
	0    -1   -1   0   
$EndComp
$Comp
L R R105
U 1 1 5442CD70
P 3450 3600
F 0 "R105" V 3530 3600 40  0000 C CNN
F 1 "2K2" V 3457 3601 40  0000 C CNN
F 2 "~" V 3380 3600 30  0000 C CNN
F 3 "~" H 3450 3600 30  0000 C CNN
	1    3450 3600
	0    -1   -1   0   
$EndComp
$Comp
L C C102
U 1 1 5442CD89
P 3800 3900
F 0 "C102" H 3800 4000 40  0000 L CNN
F 1 "10N" H 3806 3815 40  0000 L CNN
F 2 "~" H 3838 3750 30  0000 C CNN
F 3 "~" H 3800 3900 60  0000 C CNN
	1    3800 3900
	1    0    0    -1  
$EndComp
$Comp
L C C103
U 1 1 5442CDA2
P 4200 3900
F 0 "C103" H 4200 4000 40  0000 L CNN
F 1 "10N" H 4206 3815 40  0000 L CNN
F 2 "~" H 4238 3750 30  0000 C CNN
F 3 "~" H 4200 3900 60  0000 C CNN
	1    4200 3900
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR05
U 1 1 5442CDB1
P 3000 4100
F 0 "#PWR05" H 3000 4100 30  0001 C CNN
F 1 "GND" H 3000 4030 30  0001 C CNN
F 2 "" H 3000 4100 60  0000 C CNN
F 3 "" H 3000 4100 60  0000 C CNN
	1    3000 4100
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR06
U 1 1 5442CDC0
P 3800 4300
F 0 "#PWR06" H 3800 4300 30  0001 C CNN
F 1 "GND" H 3800 4230 30  0001 C CNN
F 2 "" H 3800 4300 60  0000 C CNN
F 3 "" H 3800 4300 60  0000 C CNN
	1    3800 4300
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR07
U 1 1 5442CDCF
P 4200 4300
F 0 "#PWR07" H 4200 4300 30  0001 C CNN
F 1 "GND" H 4200 4230 30  0001 C CNN
F 2 "" H 4200 4300 60  0000 C CNN
F 3 "" H 4200 4300 60  0000 C CNN
	1    4200 4300
	1    0    0    -1  
$EndComp
Wire Wire Line
	2900 3400 3200 3400
Wire Wire Line
	2900 3600 3200 3600
Wire Wire Line
	2900 3500 3000 3500
Wire Wire Line
	3000 3500 3000 4100
Wire Wire Line
	3700 3600 4800 3600
Wire Wire Line
	3800 3600 3800 3700
Wire Wire Line
	3800 4100 3800 4300
Wire Wire Line
	4200 4100 4200 4300
Wire Wire Line
	4200 3700 4200 3400
Wire Wire Line
	3700 3400 5000 3400
Wire Wire Line
	5000 3400 5000 2000
Wire Wire Line
	5000 2000 5100 2000
Connection ~ 4200 3400
Wire Wire Line
	4800 3600 4800 4000
Wire Wire Line
	4800 4000 5100 4000
Connection ~ 3800 3600
$Comp
L CONN_3 K101
U 1 1 5442D81C
P 2000 1800
F 0 "K101" V 1950 1800 50  0000 C CNN
F 1 "CONN_3" V 2050 1800 40  0000 C CNN
F 2 "" H 2000 1800 60  0000 C CNN
F 3 "" H 2000 1800 60  0000 C CNN
	1    2000 1800
	-1   0    0    -1  
$EndComp
$Comp
L GND #PWR08
U 1 1 5442D936
P 2450 2500
F 0 "#PWR08" H 2450 2500 30  0001 C CNN
F 1 "GND" H 2450 2430 30  0001 C CNN
F 2 "" H 2450 2500 60  0000 C CNN
F 3 "" H 2450 2500 60  0000 C CNN
	1    2450 2500
	1    0    0    -1  
$EndComp
Wire Wire Line
	2350 1800 2450 1800
Wire Wire Line
	2450 1800 2450 2500
Connection ~ 3400 1700
NoConn ~ 2350 1900
$Comp
L CONN_4 P101
U 1 1 5442DBA5
P 850 950
F 0 "P101" V 800 950 50  0000 C CNN
F 1 "POWER" V 900 950 50  0000 C CNN
F 2 "" H 850 950 60  0000 C CNN
F 3 "" H 850 950 60  0000 C CNN
	1    850  950 
	-1   0    0    -1  
$EndComp
$Comp
L GND #PWR09
U 1 1 5442DBB4
P 1300 1600
F 0 "#PWR09" H 1300 1600 30  0001 C CNN
F 1 "GND" H 1300 1530 30  0001 C CNN
F 2 "" H 1300 1600 60  0000 C CNN
F 3 "" H 1300 1600 60  0000 C CNN
	1    1300 1600
	1    0    0    -1  
$EndComp
$Comp
L +12V #PWR010
U 1 1 5442DBC3
P 1700 800
F 0 "#PWR010" H 1700 750 20  0001 C CNN
F 1 "+12V" H 1700 900 30  0000 C CNN
F 2 "" H 1700 800 60  0000 C CNN
F 3 "" H 1700 800 60  0000 C CNN
	1    1700 800 
	0    1    1    0   
$EndComp
$Comp
L +5V #PWR011
U 1 1 5442DC4D
P 1700 1100
F 0 "#PWR011" H 1700 1190 20  0001 C CNN
F 1 "+5V" H 1700 1190 30  0000 C CNN
F 2 "" H 1700 1100 60  0000 C CNN
F 3 "" H 1700 1100 60  0000 C CNN
	1    1700 1100
	0    1    1    0   
$EndComp
Wire Wire Line
	1200 900  1300 900 
Wire Wire Line
	1300 900  1300 1600
Wire Wire Line
	1200 1000 1300 1000
Connection ~ 1300 1000
Wire Wire Line
	1200 1100 1700 1100
Wire Wire Line
	1200 800  1700 800 
$Comp
L TL074 U101
U 1 1 5443088E
P 4300 1800
F 0 "U101" H 4350 2000 60  0000 C CNN
F 1 "TLV2464" H 4450 1600 50  0000 C CNN
F 2 "" H 4300 1800 60  0000 C CNN
F 3 "" H 4300 1800 60  0000 C CNN
	1    4300 1800
	1    0    0    -1  
$EndComp
$Comp
L R R106
U 1 1 54430AEF
P 2300 6500
F 0 "R106" V 2380 6500 40  0000 C CNN
F 1 "1K" V 2307 6501 40  0000 C CNN
F 2 "~" V 2230 6500 30  0000 C CNN
F 3 "~" H 2300 6500 30  0000 C CNN
	1    2300 6500
	0    -1   -1   0   
$EndComp
$Comp
L R R107
U 1 1 54430B27
P 3250 6100
F 0 "R107" V 3330 6100 40  0000 C CNN
F 1 "220" V 3257 6101 40  0000 C CNN
F 2 "~" V 3180 6100 30  0000 C CNN
F 3 "~" H 3250 6100 30  0000 C CNN
	1    3250 6100
	0    -1   -1   0   
$EndComp
$Comp
L R R103
U 1 1 54430B69
P 1700 6850
F 0 "R103" V 1780 6850 40  0000 C CNN
F 1 "1K2" V 1707 6851 40  0000 C CNN
F 2 "~" V 1630 6850 30  0000 C CNN
F 3 "~" H 1700 6850 30  0000 C CNN
	1    1700 6850
	1    0    0    -1  
$EndComp
$Comp
L R R102
U 1 1 54430B82
P 1450 6850
F 0 "R102" V 1530 6850 40  0000 C CNN
F 1 "1K" V 1457 6851 40  0000 C CNN
F 2 "~" V 1380 6850 30  0000 C CNN
F 3 "~" H 1450 6850 30  0000 C CNN
	1    1450 6850
	1    0    0    -1  
$EndComp
$Comp
L R R101
U 1 1 54430B9B
P 1450 5550
F 0 "R101" V 1530 5550 40  0000 C CNN
F 1 "1K" V 1457 5551 40  0000 C CNN
F 2 "~" V 1380 5550 30  0000 C CNN
F 3 "~" H 1450 5550 30  0000 C CNN
	1    1450 5550
	1    0    0    -1  
$EndComp
Wire Wire Line
	1800 6200 1700 6200
Wire Wire Line
	1700 6200 1700 6600
Wire Wire Line
	1700 6500 2050 6500
Connection ~ 1700 6500
Wire Wire Line
	2550 6500 2900 6500
Wire Wire Line
	2900 6500 2900 6100
Wire Wire Line
	2800 6100 3000 6100
Connection ~ 2900 6100
Wire Wire Line
	1450 6000 1450 6600
$Comp
L CONN_2 P102
U 1 1 5443126D
P 1000 6000
F 0 "P102" V 950 6000 40  0000 C CNN
F 1 "TEMP" V 1050 6000 40  0000 C CNN
F 2 "" H 1000 6000 60  0000 C CNN
F 3 "" H 1000 6000 60  0000 C CNN
	1    1000 6000
	-1   0    0    -1  
$EndComp
Wire Wire Line
	1450 5800 1450 5900
Connection ~ 1450 6100
$Comp
L GND #PWR012
U 1 1 54473818
P 1450 7300
F 0 "#PWR012" H 1450 7300 30  0001 C CNN
F 1 "GND" H 1450 7230 30  0001 C CNN
F 2 "" H 1450 7300 60  0000 C CNN
F 3 "" H 1450 7300 60  0000 C CNN
	1    1450 7300
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR013
U 1 1 54473827
P 1700 7300
F 0 "#PWR013" H 1700 7300 30  0001 C CNN
F 1 "GND" H 1700 7230 30  0001 C CNN
F 2 "" H 1700 7300 60  0000 C CNN
F 3 "" H 1700 7300 60  0000 C CNN
	1    1700 7300
	1    0    0    -1  
$EndComp
Wire Wire Line
	1450 7300 1450 7100
Wire Wire Line
	1700 7100 1700 7300
$Comp
L +5V #PWR014
U 1 1 54473B81
P 1450 5100
F 0 "#PWR014" H 1450 5190 20  0001 C CNN
F 1 "+5V" H 1450 5190 30  0000 C CNN
F 2 "" H 1450 5100 60  0000 C CNN
F 3 "" H 1450 5100 60  0000 C CNN
	1    1450 5100
	1    0    0    -1  
$EndComp
Wire Wire Line
	1450 5100 1450 5300
$Comp
L CONN_2 P103
U 1 1 54474010
P 4050 6200
F 0 "P103" V 4000 6200 40  0000 C CNN
F 1 "TEMP_OUT" V 4100 6200 40  0000 C CNN
F 2 "" H 4050 6200 60  0000 C CNN
F 3 "" H 4050 6200 60  0000 C CNN
	1    4050 6200
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR015
U 1 1 54474076
P 3600 6600
F 0 "#PWR015" H 3600 6600 30  0001 C CNN
F 1 "GND" H 3600 6530 30  0001 C CNN
F 2 "" H 3600 6600 60  0000 C CNN
F 3 "" H 3600 6600 60  0000 C CNN
	1    3600 6600
	1    0    0    -1  
$EndComp
Wire Wire Line
	3500 6100 3700 6100
Wire Wire Line
	3700 6300 3600 6300
Wire Wire Line
	3600 6300 3600 6600
Wire Wire Line
	8500 2300 8200 2300
Wire Wire Line
	8200 4300 8500 4300
Wire Wire Line
	8500 2500 8300 2500
Wire Wire Line
	8300 4500 8500 4500
Wire Wire Line
	5800 2000 5800 2300
$Comp
L CONN_2 J105
U 1 1 54474E92
P 7650 3300
F 0 "J105" V 7600 3300 40  0000 C CNN
F 1 "SDN1" V 7700 3300 40  0000 C CNN
F 2 "" H 7650 3300 60  0000 C CNN
F 3 "" H 7650 3300 60  0000 C CNN
	1    7650 3300
	-1   0    0    -1  
$EndComp
Wire Wire Line
	8200 2300 8200 3200
$Comp
L GND #PWR016
U 1 1 54474FD8
P 8200 3500
F 0 "#PWR016" H 8200 3500 30  0001 C CNN
F 1 "GND" H 8200 3430 30  0001 C CNN
F 2 "" H 8200 3500 60  0000 C CNN
F 3 "" H 8200 3500 60  0000 C CNN
	1    8200 3500
	1    0    0    -1  
$EndComp
Wire Wire Line
	8000 3400 8200 3400
Wire Wire Line
	8200 3400 8200 3500
$Comp
L R R126
U 1 1 544750BA
P 7750 3000
F 0 "R126" V 7650 3150 40  0000 C CNN
F 1 "22K" V 7757 3001 40  0000 C CNN
F 2 "~" V 7680 3000 30  0000 C CNN
F 3 "~" H 7750 3000 30  0000 C CNN
	1    7750 3000
	0    -1   -1   0   
$EndComp
Wire Wire Line
	8200 3200 8000 3200
Wire Wire Line
	8000 3000 8200 3000
Connection ~ 8200 3000
$Comp
L +12V #PWR017
U 1 1 544752F7
P 7300 3000
F 0 "#PWR017" H 7300 2950 20  0001 C CNN
F 1 "+12V" H 7300 3100 30  0000 C CNN
F 2 "" H 7300 3000 60  0000 C CNN
F 3 "" H 7300 3000 60  0000 C CNN
	1    7300 3000
	0    -1   -1   0   
$EndComp
Wire Wire Line
	7300 3000 7500 3000
Wire Wire Line
	5800 4300 5800 4000
$Comp
L CONN_2 J106
U 1 1 54475828
P 7650 5300
F 0 "J106" V 7600 5300 40  0000 C CNN
F 1 "SDN2" V 7700 5300 40  0000 C CNN
F 2 "" H 7650 5300 60  0000 C CNN
F 3 "" H 7650 5300 60  0000 C CNN
	1    7650 5300
	-1   0    0    -1  
$EndComp
Wire Wire Line
	8200 4300 8200 5200
$Comp
L GND #PWR018
U 1 1 5447582F
P 8200 5500
F 0 "#PWR018" H 8200 5500 30  0001 C CNN
F 1 "GND" H 8200 5430 30  0001 C CNN
F 2 "" H 8200 5500 60  0000 C CNN
F 3 "" H 8200 5500 60  0000 C CNN
	1    8200 5500
	1    0    0    -1  
$EndComp
Wire Wire Line
	8000 5400 8200 5400
Wire Wire Line
	8200 5400 8200 5500
$Comp
L R R127
U 1 1 54475837
P 7750 5000
F 0 "R127" V 7650 5150 40  0000 C CNN
F 1 "22K" V 7757 5001 40  0000 C CNN
F 2 "~" V 7680 5000 30  0000 C CNN
F 3 "~" H 7750 5000 30  0000 C CNN
	1    7750 5000
	0    -1   -1   0   
$EndComp
Wire Wire Line
	8200 5200 8000 5200
Wire Wire Line
	8000 5000 8200 5000
Connection ~ 8200 5000
$Comp
L +12V #PWR019
U 1 1 54475840
P 7300 5000
F 0 "#PWR019" H 7300 4950 20  0001 C CNN
F 1 "+12V" H 7300 5100 30  0000 C CNN
F 2 "" H 7300 5000 60  0000 C CNN
F 3 "" H 7300 5000 60  0000 C CNN
	1    7300 5000
	0    -1   -1   0   
$EndComp
Wire Wire Line
	7300 5000 7500 5000
$Comp
L MOS_N Q101
U 1 1 544758C9
P 5300 5300
F 0 "Q101" H 5310 5470 60  0000 R CNN
F 1 "BSS-138" H 5310 5150 60  0000 R CNN
F 2 "~" H 5300 5300 60  0000 C CNN
F 3 "~" H 5300 5300 60  0000 C CNN
	1    5300 5300
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR020
U 1 1 54475A69
P 5400 5700
F 0 "#PWR020" H 5400 5700 30  0001 C CNN
F 1 "GND" H 5400 5630 30  0001 C CNN
F 2 "" H 5400 5700 60  0000 C CNN
F 3 "" H 5400 5700 60  0000 C CNN
	1    5400 5700
	1    0    0    -1  
$EndComp
Wire Wire Line
	5400 5500 5400 5700
Wire Wire Line
	1450 5900 1350 5900
Wire Wire Line
	1450 6100 1350 6100
Wire Wire Line
	1450 6000 1800 6000
Wire Wire Line
	8300 2500 8300 4700
Wire Wire Line
	8300 4700 5400 4700
Wire Wire Line
	5400 4700 5400 5100
Connection ~ 8300 4500
Wire Wire Line
	4900 5300 5100 5300
Connection ~ 4900 3800
$Comp
L R R124
U 1 1 54476C24
P 2900 2050
F 0 "R124" V 2980 2050 40  0000 C CNN
F 1 "1M" V 2907 2051 40  0000 C CNN
F 2 "~" V 2830 2050 30  0000 C CNN
F 3 "~" H 2900 2050 30  0000 C CNN
	1    2900 2050
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR021
U 1 1 54476C33
P 2900 2500
F 0 "#PWR021" H 2900 2500 30  0001 C CNN
F 1 "GND" H 2900 2430 30  0001 C CNN
F 2 "" H 2900 2500 60  0000 C CNN
F 3 "" H 2900 2500 60  0000 C CNN
	1    2900 2500
	1    0    0    -1  
$EndComp
Wire Wire Line
	2900 1700 2900 1800
Connection ~ 2900 1700
Wire Wire Line
	2900 2300 2900 2500
$Comp
L R R125
U 1 1 54477309
P 4550 4150
F 0 "R125" V 4630 4150 40  0000 C CNN
F 1 "1K" V 4557 4151 40  0000 C CNN
F 2 "~" V 4480 4150 30  0000 C CNN
F 3 "~" H 4550 4150 30  0000 C CNN
	1    4550 4150
	1    0    0    -1  
$EndComp
$Comp
L +12V #PWR022
U 1 1 54477322
P 4550 3800
F 0 "#PWR022" H 4550 3750 20  0001 C CNN
F 1 "+12V" H 4550 3900 30  0000 C CNN
F 2 "" H 4550 3800 60  0000 C CNN
F 3 "" H 4550 3800 60  0000 C CNN
	1    4550 3800
	1    0    0    -1  
$EndComp
Wire Wire Line
	4550 5000 5400 5000
Connection ~ 5400 5000
$Comp
L PWR_FLAG #FLG023
U 1 1 54478784
P 1600 750
F 0 "#FLG023" H 1600 845 30  0001 C CNN
F 1 "PWR_FLAG" H 1600 930 30  0000 C CNN
F 2 "" H 1600 750 60  0000 C CNN
F 3 "" H 1600 750 60  0000 C CNN
	1    1600 750 
	1    0    0    -1  
$EndComp
$Comp
L PWR_FLAG #FLG024
U 1 1 54478793
P 1600 1050
F 0 "#FLG024" H 1600 1145 30  0001 C CNN
F 1 "PWR_FLAG" H 1600 1230 30  0000 C CNN
F 2 "" H 1600 1050 60  0000 C CNN
F 3 "" H 1600 1050 60  0000 C CNN
	1    1600 1050
	1    0    0    -1  
$EndComp
Wire Wire Line
	1600 750  1600 800 
Connection ~ 1600 800 
Wire Wire Line
	1600 1050 1600 1100
Connection ~ 1600 1100
$Comp
L PWR_FLAG #FLG025
U 1 1 54475649
P 1400 1350
F 0 "#FLG025" H 1400 1445 30  0001 C CNN
F 1 "PWR_FLAG" H 1400 1530 30  0000 C CNN
F 2 "" H 1400 1350 60  0000 C CNN
F 3 "" H 1400 1350 60  0000 C CNN
	1    1400 1350
	0    1    1    0   
$EndComp
Wire Wire Line
	1400 1350 1300 1350
Connection ~ 1300 1350
$Sheet
S 6500 5900 850  950 
U 544CD45B
F0 "Heater driver" 50
F1 "Heater.sch" 50
F2 "HEAT_IN" I L 6500 6150 60 
F3 "HEAT_OUT" O R 7350 6500 60 
F4 "HEATER_12V" B R 7350 6000 60 
$EndSheet
$Comp
L CONN_2 P105
U 1 1 544CDA94
P 5800 6250
F 0 "P105" V 5750 6250 40  0000 C CNN
F 1 "HEAT_IN" V 5850 6250 40  0000 C CNN
F 2 "" H 5800 6250 60  0000 C CNN
F 3 "" H 5800 6250 60  0000 C CNN
	1    5800 6250
	-1   0    0    -1  
$EndComp
$Comp
L GND #PWR026
U 1 1 544CDB09
P 6250 6650
F 0 "#PWR026" H 6250 6650 30  0001 C CNN
F 1 "GND" H 6250 6580 30  0001 C CNN
F 2 "" H 6250 6650 60  0000 C CNN
F 3 "" H 6250 6650 60  0000 C CNN
	1    6250 6650
	1    0    0    -1  
$EndComp
Wire Wire Line
	6150 6350 6250 6350
Wire Wire Line
	6250 6350 6250 6650
Wire Wire Line
	6150 6150 6500 6150
$Comp
L LED D103
U 1 1 544CE271
P 4550 4700
F 0 "D103" H 4550 4800 50  0000 C CNN
F 1 "LED_RED" H 4550 4600 50  0000 C CNN
F 2 "~" H 4550 4700 60  0000 C CNN
F 3 "~" H 4550 4700 60  0000 C CNN
	1    4550 4700
	0    1    1    0   
$EndComp
Wire Wire Line
	4550 3800 4550 3900
Wire Wire Line
	4550 4400 4550 4500
Wire Wire Line
	4550 4900 4550 5000
$Comp
L R R128
U 1 1 544CF375
P 1200 2750
F 0 "R128" V 1280 2750 40  0000 C CNN
F 1 "330" V 1207 2751 40  0000 C CNN
F 2 "~" V 1130 2750 30  0000 C CNN
F 3 "~" H 1200 2750 30  0000 C CNN
	1    1200 2750
	1    0    0    -1  
$EndComp
$Comp
L R R129
U 1 1 544CF384
P 1600 2750
F 0 "R129" V 1680 2750 40  0000 C CNN
F 1 "1K" V 1607 2751 40  0000 C CNN
F 2 "~" V 1530 2750 30  0000 C CNN
F 3 "~" H 1600 2750 30  0000 C CNN
	1    1600 2750
	1    0    0    -1  
$EndComp
$Comp
L LED D101
U 1 1 544CF393
P 1200 3300
F 0 "D101" H 1200 3400 50  0000 C CNN
F 1 "LED_GREEN" H 1200 3200 50  0000 C CNN
F 2 "~" H 1200 3300 60  0000 C CNN
F 3 "~" H 1200 3300 60  0000 C CNN
	1    1200 3300
	0    1    1    0   
$EndComp
$Comp
L LED D102
U 1 1 544CF438
P 1600 3300
F 0 "D102" H 1600 3400 50  0000 C CNN
F 1 "LED_GREEN" H 1600 3200 50  0000 C CNN
F 2 "~" H 1600 3300 60  0000 C CNN
F 3 "~" H 1600 3300 60  0000 C CNN
	1    1600 3300
	0    1    1    0   
$EndComp
$Comp
L GND #PWR027
U 1 1 544CF537
P 1200 3600
F 0 "#PWR027" H 1200 3600 30  0001 C CNN
F 1 "GND" H 1200 3530 30  0001 C CNN
F 2 "" H 1200 3600 60  0000 C CNN
F 3 "" H 1200 3600 60  0000 C CNN
	1    1200 3600
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR028
U 1 1 544CF546
P 1600 3600
F 0 "#PWR028" H 1600 3600 30  0001 C CNN
F 1 "GND" H 1600 3530 30  0001 C CNN
F 2 "" H 1600 3600 60  0000 C CNN
F 3 "" H 1600 3600 60  0000 C CNN
	1    1600 3600
	1    0    0    -1  
$EndComp
$Comp
L +12V #PWR029
U 1 1 544CF569
P 1600 2300
F 0 "#PWR029" H 1600 2250 20  0001 C CNN
F 1 "+12V" H 1600 2400 30  0000 C CNN
F 2 "" H 1600 2300 60  0000 C CNN
F 3 "" H 1600 2300 60  0000 C CNN
	1    1600 2300
	1    0    0    -1  
$EndComp
$Comp
L +5V #PWR030
U 1 1 544CF578
P 1200 2300
F 0 "#PWR030" H 1200 2390 20  0001 C CNN
F 1 "+5V" H 1200 2390 30  0000 C CNN
F 2 "" H 1200 2300 60  0000 C CNN
F 3 "" H 1200 2300 60  0000 C CNN
	1    1200 2300
	1    0    0    -1  
$EndComp
Wire Wire Line
	1200 3500 1200 3600
Wire Wire Line
	1600 3500 1600 3600
Wire Wire Line
	1600 3100 1600 3000
Wire Wire Line
	1200 3100 1200 3000
Wire Wire Line
	1200 2500 1200 2300
Wire Wire Line
	1600 2500 1600 2300
$Comp
L GNDPWR #PWR031
U 1 1 544D31A6
P 8150 6450
F 0 "#PWR031" H 8150 6500 40  0001 C CNN
F 1 "GNDPWR" H 8150 6370 40  0000 C CNN
F 2 "" H 8150 6450 60  0000 C CNN
F 3 "" H 8150 6450 60  0000 C CNN
	1    8150 6450
	1    0    0    -1  
$EndComp
$Comp
L PWR_FLAG #FLG032
U 1 1 544D34B8
P 7950 6400
F 0 "#FLG032" H 7950 6495 30  0001 C CNN
F 1 "PWR_FLAG" H 7950 6580 30  0000 C CNN
F 2 "" H 7950 6400 60  0000 C CNN
F 3 "" H 7950 6400 60  0000 C CNN
	1    7950 6400
	-1   0    0    1   
$EndComp
$Comp
L GNDPWR #PWR033
U 1 1 544D377E
P 7550 6900
F 0 "#PWR033" H 7550 6950 40  0001 C CNN
F 1 "GNDPWR" H 7550 6820 40  0000 C CNN
F 2 "" H 7550 6900 60  0000 C CNN
F 3 "" H 7550 6900 60  0000 C CNN
	1    7550 6900
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR034
U 1 1 544D378D
P 8300 6900
F 0 "#PWR034" H 8300 6900 30  0001 C CNN
F 1 "GND" H 8300 6830 30  0001 C CNN
F 2 "" H 8300 6900 60  0000 C CNN
F 3 "" H 8300 6900 60  0000 C CNN
	1    8300 6900
	1    0    0    -1  
$EndComp
$Comp
L R R130
U 1 1 544D379C
P 7900 6750
F 0 "R130" V 7980 6750 40  0000 C CNN
F 1 "1K" V 7907 6751 40  0000 C CNN
F 2 "~" V 7830 6750 30  0000 C CNN
F 3 "~" H 7900 6750 30  0000 C CNN
	1    7900 6750
	0    -1   -1   0   
$EndComp
Wire Wire Line
	7550 6900 7550 6750
Wire Wire Line
	7550 6750 7650 6750
Wire Wire Line
	8150 6750 8300 6750
Wire Wire Line
	8300 6750 8300 6900
$Comp
L CONN_4 P106
U 1 1 54551D59
P 8550 6200
F 0 "P106" V 8500 6200 50  0000 C CNN
F 1 "HEATER" V 8600 6200 50  0000 C CNN
F 2 "" H 8550 6200 60  0000 C CNN
F 3 "" H 8550 6200 60  0000 C CNN
	1    8550 6200
	1    0    0    -1  
$EndComp
Wire Wire Line
	7950 6350 8200 6350
Wire Wire Line
	8150 6350 8150 6450
Wire Wire Line
	7950 6350 7950 6400
Connection ~ 8150 6350
Wire Wire Line
	7600 6250 8200 6250
Wire Wire Line
	7600 6250 7600 6000
Wire Wire Line
	7600 6000 7350 6000
Wire Wire Line
	8200 6150 8000 6150
Wire Wire Line
	8000 6150 8000 6250
Connection ~ 8000 6250
Wire Wire Line
	7700 6050 8200 6050
Wire Wire Line
	7700 6050 7700 6500
Wire Wire Line
	7700 6500 7350 6500
$EndSCHEMATC
