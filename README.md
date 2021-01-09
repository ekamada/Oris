# Oris, A Digital Ausculation Device

**Creators:** Eric Kamada, Lucia Iannantuono, Simon Ly, Stefano Vitucci

**MOTIVATION:** <br>
It can be very difficult to identify heart and lung conditions using traditional stethoscopes; it requires a trained specialist, with good hearing and a quiet environment to be able to discern abnormalities. Today, medicine is increasingly making use of technology to enhance collaboration, provide long-distance telemedicine, and provide easily accessible patient history with electronic medical records. An analog stethoscope cannot be easily integrated into a digital 21st century healthcare system. This was the motivation for our design: Oris, a digital auscultation device. 

**OBJECTIVE:** <br>
To create an acoustic analysis tool that can be used by practitioners or even those with only some medical training. It will aid them with hearing and monitoring sounds, perform analysis  for diagnosing cardiovascular conditions, and provide digital conversion for recording, replaying, and sharing the audio. 

**THE DEVICE:** <br>
Our device consists of three components: hardware, embedded software, and a PC user interface. <br>

The preprocessing circuit amplifies, filters and converts sound obtained from a bell held to the patient’s chest, which has a microphone embedded inside. The resulting digital signal is input to a microcontroller where it undergoes more precise digital filtering. At this stage our hand-held device displays basic diagnostic information to the user and offers Bluetooth functionality to transmit the recorded sound data to their PC. The PC user interface software allows practitioners to save sessions, playback sounds with optional frequency shifting, and run diagnostic analyses to see a normal/abnormal classification for the patient’s heart recording.


**THIS REPO:** <br>
This repo contains everything that is needed in order to run the Oris program, which can perform the following tasks:
- Recieves data from the ADC <br>
- Process raw input using filters and detection algorithms to create audible audio and collect basic information about the heartbeat <br>
- Runs a GUI which displays relevant information <br>
- Connects to a PC via bluetooth <br>
- Transmits Heartbeat data to PC for further processing <br>
 
 
**HARDWARE** <br>
The Oris Devices consists of the following components:
- Raspberry Pi Zero WH (Zero W with Headers)
- Adafruit PiTFT Plus 320x240 2.8" TFT + Capacitive Touchscreen
- PCB with signal filtering, amplification, and ADC conversion
  
  
  
