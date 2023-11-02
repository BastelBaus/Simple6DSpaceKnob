# Initial Design Concept

![design concept](images/Concept_V1.png)

- The heart builds the pretty need XIAO ESP32S with lots of processing power, BLE, WLAN interfaces as well as a modern USB-C connection. It includes an battery management part avoiding extra PCBs.
- The detection principle of the 6D motion will be done with 6 linear HALL sensors measureing the displacement of the neodyn magnets mounted at the knob.
- Adding an IMU in the knobn might increase the stability (using a Kalman filter to fuse the signals) and could be used to wake up the device when it is in sleep mode (which would be mandatory for battery operation).

# Rough estimate of cost (09/2023)

|What | Exact Part | cost <br>full |cost <br> low budget | source/link |
| --- |  --- |   --- |  --- |  --- |
| uC | ESP32S | $7.49 | $7.49 | [seedstudio](https://www.seeedstudio.com/XIAO-ESP32S3-p-5627.html)
| battery | LiPo 3.7V 650mAH | 2.60€ | - |[ALioExpress](https://de.aliexpress.com/item/4000455115915.html)
| switch | 
| hall sensors | 49E SS49E OH49E (6x) | | | [AliExpress](https://de.aliexpress.com/item/1005003468214330.html)
| magnets |
| buttons | 2x | 0.50€ | 0.50€ |[ALiExpress](https://de.aliexpress.com/item/1005004159746274.html)
| springs | 25x6 (3x) | 2,40€ |2,40€ | [AliExpress](https://de.aliexpress.com/item/1005003764665719.html)
| cables |  - | $ | $ | depends on your patience
| 3D housing | - | $ | $ | depends on your patience
| shipping | - | $ | $ | depends on your patience
| working hours | 1000h+ | 0 | 0 | good that thigs is free !
| **sum** | - | **<20€** | **<15€** | -


<br><hr/> 
\>> Back to  **[main page](index.md)** <br>
\>> Go to **[main repository](https://github.com/BastelBaus/Simple6DSpaceKnob)**
