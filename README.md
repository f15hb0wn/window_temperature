# Windows Temperature Overlay

I finished a new rig and am running it hard and wanted to know how hot the hardware is getting.

I wanted a simple widget to display GPU and CPU temperatures to have the following characteristics:
- Green/Yellow/Red indicator on temperature against configured thresholds
- An average of temperature readings to avoid excessive alerting
- Stays on top of windows
- Can be moved

![Interface Screenshot](/demo.png)

# Pre-requisites
- Download, extract and run (as Administrator) Libre Hardware Monitor: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor
- Install Python for Windows (tested on 3.12): https://www.python.org/downloads/
- Download this code and change directory to it.
- Install dependencies: `pip install -r requirements.txt`
- Optional: Edit the constants at the top of `app.py`
- Run `python app.py`

