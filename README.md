# SmartFrameDIY
Personal project for python-based slideshow displayed on a Raspberry Pi 4

Materials:
1. Raspberry Pi 4 Model B
2. SunFounder 10.1" (1280x800) HD Screen for Raspberry Pi 4 Model B
3. 256 GB Flash Drive (Better to use mSATA HDD next time)
4. USB Male to Female R/L Angle Extension Cable
5. Command Strip
6. Iphone or Mac with photos

Setting Up the Raspberry Pi and Frame:
1. Follow online set up guides to set up a user
2. Connect RPi to network
3. Set up Samba server on the Pi using: https://www.thedigitalpictureframe.com/installing-samba-on-your-raspberry-pi-buster-and-optimizing-it-for-macos-computers/
4. Create Python environment: https://learn.adafruit.com/python-virtual-environment-usage-on-raspberry-pi/basic-venv-usage
5. Swap from Wayland (installed on RPi) to X11 to be able to get mouse cursor to sleep while frame is running
6. Add slideshow.py and file_transfer.py to `/home`
   Note: Python scripts currently refer to directories I have named, so they would need to be changed if this project is repeated on another RPi
7. Add runFrame.sh to `/home`
8. Make runFrame.sh executable: `sudo chmod +x runFrame.sh`
9. Add frame.service to `/etc/systemd/service/`
10. Enable frame.service: `sudo systemctl enable frame.service`
11. Power Cycle the Raspberry Pi and Slideshow should start on boot

To Stop the Slideshow from another computer:
1. Connect to same network as RPi
2. Open terminal
3. Connect to RPi via SSH: `ssh user@ipaddress`
4. To find python processes: `ps -ef | grep python`
5. To kill one of these processes: `kill -9 [PID from previous step]`
6. Slideshow will stop and you will regain normal control of RPi
7. Slideshow can be restarted anytime by running: `./runFrame.sh` from `/home`
