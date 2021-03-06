% Biohacking in the medical field
% @kelu124
% May 23, 2017

## Objective

The objective of this project is to propose an open-source, low-cost dev-kit ultrasound imaging __to allow scientists, academics, hackers, makers or open hardware fans to hack ultrasound imaging__.

## What approach ?

* Going back to the time when ultrasound was all mechanical.
* Having a modular "approach"
* Simplify !

## Bases of ultrasound imaging

![](http://openhardware.metajnl.com/articles/10.5334/joh.2/joh-1-2-g2.png)

## Signals

![](https://raw.githubusercontent.com/kelu124/echomods/master/goblin/images/slide_principle.png)

## Architecture

![](http://openhardware.metajnl.com/articles/10.5334/joh.2/joh-1-2-g1.png)

## Proof of concept

![](https://raw.githubusercontent.com/kelu124/echomods/master/doj/images/doj_v2_notes.jpg)

## Cost of the set: 325$

* A probe on ebay: 75$
* High voltage module: 80$ of components
* Analog processing module: 80$ of components
* PCBs: 40$
* Acquisition Raspberry Pi: 40$ 
* Raspberry Pi: 10$

## Example of a probe image  {data-background="https://raw.githubusercontent.com/kelu124/echomods/master/include/20160814/sonde3V_1-4.csv-SC.png"}

## Usage examples

* 2-D mode imaging
* Measurements (bladder, ...)
* Biofeedback for stroke recovery
* Doppler
* ...

## Limitation and opportunity

__Limits__

* Material is not certified
* Probe sensor limits the quality
* Be [careful](https://kelu124.gitbooks.io/echomods/content/caution.html)!

__Opportunity__

* Using a [Raspberry is cool](https://kelu124.gitbooks.io/echomods/content/RPI.html)!
* An open plat-form!

## Lessons

What I learned tinkering with stuff

1. _Build the tools you need_ 
2. _Document_
3. _Do and share_


## Build the tools you need..

Acquisition

* BeagleBone [PRU-DAQ](https://github.com/kelu124/echomods/blob/master/retired/toadkiller/Readme.md)
* BitScope
* STM32 [Feather WICED](https://github.com/kelu124/echomods/tree/master/goblin)
* ... __custom made__ with a [raspberry](https://github.com/kelu124/echomods/blob/master/elmo/data/arduinoffset/20170612-ArduinoFFTed.ipynb)!
* Emulation & calibration tools

## Documentation

* Documentation here is key. 
* A website that builds itself based on proper, simple and un-redondant information is needed. 

## Doing and sharing

* Documentation on [GitHub](https://github.com/kelu124/echomods/) and [GitBook](https://kelu124.gitbooks.io/echomods/content/)
* "Blogging" on [Hackaday](https://hackaday.io/project/9281-murgen-open-source-ultrasound-imaging)
* A summary on [Journal of Open Hardware](http://openhardware.metajnl.com/articles/10.5334/joh.2/) (thanks GOSH!)
* [Tindie](https://www.tindie.com/stores/kelu124/) for sharing "extra" boards

## Issues for "real" medical biohacking and towards medical uses

* Certification
* Sensors sourcing
* Reliability of the device
* Training of users
 
## We can discuss how

* to do a working dev-kit to share knowledge
* implement and efficient (err, lazy) way of documenting. 
* share with a community
* better understand your "product"

## Other approaches?

* Re-using and improving hardware
* Using old hardware for new approaches

## Improving a ["rogue" probe](https://github.com/kelu124/kina/)

![](https://cdn.hackaday.io/images/28321490131782990.jpg)

## Using differently

![](https://ae01.alicdn.com/kf/HTB1U4rfPFXXXXbRXFXXq6xXFXXXL/Prenatal-font-b-Fetal-b-font-font-b-Doppler-b-font-LCD-Screen-Backlight-Built-in.jpg)

## Q&A

Ping me @kelu124 / kelu124@gmail.com !

* Read more on the [gitbook](https://kelu124.gitbooks.io/echomods/content/)
* Fork [this work on github](https://github.com/kelu124/echomods/)
* Buy some modules on [Tindie](https://www.tindie.com/stores/kelu124/)

Presentation at [bit.ly/biohackingcameroun_luc](http://bit.ly/biohackingcameroun_luc)


