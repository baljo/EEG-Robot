# Applying EEG Data to Machine Learning, Part 3

## Intro

This third and final tutorial in the series about Machine Learning (ML) and EEG-data, walks through how you can control a small mobile robot purely with your brain waves! While this is a stand-alone tutorial, it is still recommended you check [Part 1](https://docs.edgeimpulse.com/experts/prototype-and-concept-projects/eeg-data-machine-learning-part-1) and [Part 2](https://docs.edgeimpulse.com/experts/prototype-and-concept-projects/eeg-data-machine-learning-part-2) for background information.

## Problem Being Solved / Use-case Explanation

The previous two tutorials showed how you, using EEG-data from a consumer EEG-device, can play simple games or use a computer to communicate with the outer world. This tutorial takes it one step further, showing how you can control a small mobile robot, again by the small electric signals your brain emits. Possible users for this type of solution might be people having none or only limited capabilities to move their limbs (but still have "normal" brain functionality), to control physical devices such as wheelchairs, doors, window blinders, televisions etc. In the video this technology is simply used to bring a cold drink to me.

Previously I used a setup with several devices involved: `EEG-device ==> Mobile Phone (MindMonitor/PythonOSC) ==> Wi-Fi ==> Computer`, and while it as such worked well enough, I discovered that using same concept when introducing yet an additional device (appending `==> Wi-Fi ==> Mobile Robot` in the equation) caused more latency. In practice this resulted in undesirable delays between the desired action and the same action performed. E.g., when trying to turn the robot left, the left turn sometimes happened unacceptable late, and it was difficult to understand if it was a misinterpration of the EEG-data, or something else. 

Due to this behavior, and that I wanted to simplify the setup, I explored if it was possible to get rid of the phone in the equation, thus having this setup `EEG-device ==> Computer ==>  Wi-Fi ==> Mobile Robot`. The phone though used MindMonitor and  PythonOSC to communicate with the computer, but also automatically reduced the raw data to spectral bands, so I had to find a way to replace both the technical communication as well as the spectral functionality. The communication challenge got solved by using the Lab Streaming Layer (LSL) protocol, and the spectral challenge by Edge Impulse helping me to use their Python-code for extracting spectral features. Through this I was successful in removing the phone and getting almost no extra delays at all!

The hardware used in this project was a Parallax ActivityBot, equipped with XBee Wi-Fi and a Parallax Ping))) Ultrasonic distance sensor. While more or less any Wi-Fi equipped robot - mobile or not - can be used, I've found the Parallax product line to be very reliable and easy to work with. The microcontroller on the robot is a Propeller P1 processor with 8 separate cores and a shared RAM-memory, which is more than enough for this quite simple use case.   



## Components and Hardware/Software Configuration

### Components Needed

- [Interaxon Muse EEG-device](https://choosemuse.com/pages/shop), any "recent" model, my device is from 2018
- [Parallax Activitybot kit](https://www.parallax.com/product/activitybot-360-robot-kit/)
- [PING))) Ultrasonic Distance Sensor](https://www.parallax.com/product/ping-ultrasonic-distance-sensor/) or [LaserPING 2m Rangefinder](https://www.parallax.com/product/laserping-2m-rangefinder/)
    - note: the distance sensor is not strictly needed for this project, it is only used to reverse the robot in case it comes too close to a hinder, but I still recommend to have a distance sensor for other robot projects
- [Parallax WX ESP8266 WiFi Module – DIP](https://www.parallax.com/product/parallax-wx-esp8266-wifi-module-dip/)
- Computer: Windows, Mac, Linux, even a Raspberry Pi might work. Only tested on Windows 10.

Please note that the components I've used are several years old, and have been replaced with the newer versions linked above. Due to this there's a possibility you'll have to adjust some of the configuration settings, this is of course even more applicable if you use any other brand than Parallax.

### Hardware Configuration

- Assemble the robot, possible distance sensor, and Wi-Fi module according to the instructions distributed py Parallax
- Before trying to replicate this project, familiarize yourself with the robot and how to program it. An excellent starting point is the [Parallax educational site](https://learn.parallax.com/).

### Software Configuration

- The robot is in this project programmed using [SimpleIDE](https://learn.parallax.com/tutorials/language/propeller-c/propeller-c-set-simpleide) which is an open source programming tool for Propeller C. SimpleIDE is no longer maintained since 2018, but was still possible to install and use on Win10 when this tutorial was written (June 2023).
    - You can also use any other language that the Propeller processor family supports as long as you find libraries for the Wi-Fi and distance sensor modules
    - The program controlling the robot in this project is by purpose very simple, it is just receiving a control code and a direction code (2 bytes) through Wi-Fi and taking actions on the direction code. This makes it easy to adjust for other brands or other type of robots.
    - Using SimpleIDE, compile and upload [this program](https://github.com/baljo/EEG-Robot/blob/main/Code/EEG-Robot%20-%20receiver%20side.c) to the robot
        - You'll need to match pin and Wi-Fi settings with your own setup, check the code for pointers
- Computer
    - Python 3.x, I've used v3.11
        - install following Python libraries: tensorflow, muselsl (only used when recording data), pylsl, numpy, nltk, socket, spectral_analysis (this is found from [Edge Impulse GitHub](https://github.com/edgeimpulse/processing-blocks/tree/master/spectral_analysis))
        - download the [Python-program](https://github.com/baljo/EEG-Robot/blob/main/Code/EEG-robot.py) communicating with the EEG-device and with the robot
    - BlueMuse or other software able to stream data from Muse EEG headsets via LSL (Lab Streaming Layer)


## Data Collection Process

In this project I started with the aim of collecting data mainly stemming from the motor cortex in our brains. Thus I collected data when **trying** to move my left hand, when **trying** to move my right hand, and when relaxing. I did though not move any limbs at all, neither did I blink, thus simulating I was paralyzed. I got an accuracy of 88 % as testing result in Edge Impulse, which for this type of project is surprisingly good. 

![](/Images/EI-02.jpg)


## Training and Building the Model
## Model Deployment
## Results
## Conclusion

Intro / Overview
Briefly provide an introduction to your project. Address the following: what you are accomplishing, what the intended outcome is, highlight the use-case, describe the reasons for undertaking this project, and give a high level overview of the build. Provide a sentence or two for each of these aspects.  
Summarize the problem you are addressing in one or two sentences, and how your solution makes an impact.  Be sure to also give a brief introduction to the hardware you have chosen and any key features, or reasons why the selected hardware is a good fit for your project. 
Include a high-quality image of the hardware.

Problem Being Solved / Use-case Explanation
Here we will go deeper into the problem that is being addressed.  We’ll want to provide evidence and data that the problem exists, and provide some possible improved outcomes and what we are hoping to achieve.  We need to establish credibility and demonstrate competence and innovation, so that readers have trust in the solution being presented.  This could be a good place to also further document the hardware features, sensors, or interfaces available on the board, describe what they do or what data they are intended to capture, and why that is important.  An image further detailing the problem or challenge would be useful, but might not be required depending upon the project.

Components and Hardware Configuration
If any additional components are needed to build the project, include a list / Bill of Materials.  Normally this is formatted in a bulleted list, and quantity needed, to build the project.  After that, a description of how to set up the hardware, attach any sensors or secondary devices, flash any firmware or operating systems, install needed applications, and ultimately reach a point where we’re ready for Edge Impulse in the project.  We’ll definitely want some pictures of the hardware build process, showing the journey and setup that will guide readers through the process.

Data Collection Process
Next we need to describe to a reader and demonstrate how data is collected.  Depending upon the type of the project, this might be done directly in the Edge Impulse Studio, via the use of a 3rd-party dataset, or data could be collected out in the field and later uploaded / ingested to Edge Impulse.  Data being captured should be explained, the specific process to capture it should be documented, and the loading of the data into Edge Impulse should be articulated as well.  Images will be helpful here, showing the device capturing data, or if you are making use of a pre-made dataset then you will need to describe where you acquired it, how you prepared the dataset for Edge Impulse, and what your upload process entails.  Pictures of the data capture and/or screenshots of loading the data will be needed.

Training and Building the Model
Similar to the Data Collection Process section, a thorough description of the process used to build and train a model is important, so that readers can follow along and replicate your work.  Describe the elements in the Studio, the actions you take, and why.  Talk about the need for Training and Testing data, and when creating an Impulse,  Processing and Learning block options, Feature generation, and algorithm selection (FOMO, MobileNet, Yolo, etc) available to train and build the model.  Explain the selections you make, and the reasoning behind your choices.  Again images should be used here, screenshots walking a user through the process are very helpful.

Model Deployment
Go into detail about the process of getting your resulting model into your application and onto your hardware.  This will of course vary by the target hardware, but explain what is occurring and how to flash your firmware, import the model if it’s a Linux device, or include a Library directly in your application.  Again describe the options presented to a user, and explain why you make the selections you do.  A few screenshots of the process would be useful.

Results
Now it is time to show the finished project, deployed and running on the device.  Let’s talk about the results of running the model, presenting data, evidence, or statistics as appropriate.  Not all projects may meet their objectives, or perform well, but we should still present the outcomes truthfully.  If the project was extremely successful, then we can articulate on how the project could be scaled to truly make an impact.  If the project fell short of its goal, that is fine as well, and we can discuss what might have gone wrong, how the project could be improved, and provide lessons learned.  Screenshots or images might be needed here, as well.  

Conclusion
A brief summary recapping what you built, why, and the outcome you achieved.  A few sentences wrapping up the project, any next steps you might take, or giving advice to the reader on how they can take your project and replicate it as-is, iterate, expand, or even scale your work.  All Expert Projects should be Public Projects, so explain that a reader can Clone your work and has access to your data, model, and can review the steps you took.  Reinforce the human health or machine health use case, and provide any final links or attribution.  

