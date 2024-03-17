from tkinter import Tk, Canvas
from collections import deque
import gpustat
import wmi

# Set the temperature thresholds
CAUTION_TEMP= 80 # Set the temperature at which the thermal circle turns yellow
DANGER_TEMP= 90 # Set the temperature at which the themal circle turns red
NETOPS_CAUTION = 200 # Set the network operations caution in Mbps
DISKOPS_CAUTION = 200 # Set the disk operations caution in MBps
UTILIZATION_CAUTION = 95 # Set the utilization caution in percentage
# Set the polling interval in milliseconds
POLL_INTERVAL_MS = 1000
# Set the number of temperature samples to keep
NUM_SAMPLES = 30
# Set the maximum CPU frequency in MHz
MAX_CPU_MHZ = 5500
# Set the ID of the disk to monitor
DISK_ID = "/nvme/2"
# Set width of the window
WIDTH = 280
# Set the height of each row
ROW_HEIGHT = 20
# Set the font size
FONT_SIZE = 8
# Set the Location to load the window
X_LOCATION = 0
Y_LOCATION = 200


def get_temperatures():
    temps = []
    # Get GPU temperatures
    stats = gpustat.new_query()
    id = 0
    for gpu in stats.gpus:
        device_name = "GPU-" + str(id)
        id += 1
        temps.append((device_name, gpu.temperature))
    
    # Get CPU temperature
    # Connect to the OpenHardwareMonitor namespace
    w = wmi.WMI(namespace="root\\LibreHardwareMonitor")

    # Get temperature sensor information
    temperature_infos = w.Sensor()

    # Iterate through sensors and print CPU temperature
    cpu_temp = 0
    system_temp = 0
    hdd_temp = False
    for sensor in temperature_infos:
        if sensor.SensorType == u'Temperature' and sensor.Name == "CPU Socket":
            cpu_temp = sensor.Value
        if sensor.SensorType == u'Temperature' and sensor.Name == "System":
            system_temp = sensor.Value
        if sensor.SensorType == u'Temperature' and sensor.Name == "Temperature" and sensor.Parent == DISK_ID:
            hdd_temp = sensor.Value        
    temps.append(("CPU", cpu_temp))
    temps.append(("RAM", system_temp))
    if hdd_temp:
        temps.append(("DISK", hdd_temp))
    
    return temps

def get_utilizations():
    values = []
    # Get GPU temperatures
    stats = gpustat.new_query()
    id = 0
    for gpu in stats.gpus:
        device_name = "GPU-" + str(id)
        id += 1
        values.append((device_name, gpu.utilization))
    
    # Get CPU temperature
    # Connect to the OpenHardwareMonitor namespace
    w = wmi.WMI(namespace="root\\LibreHardwareMonitor")

    # Get temperature sensor information
    values_infos = w.Sensor()

    # Iterate through sensors and print CPU temperature
    cpu_total = 0
    cpu_speed = MAX_CPU_MHZ
    ram_used = 0
    hdd_used = False
    for sensor in values_infos:
        if sensor.SensorType == u'Load' and sensor.Name == "CPU Total":
            cpu_total = sensor.Value
        if sensor.SensorType == u'Clock' and sensor.Name == "CPU Core #1":
            cpu_speed = sensor.Value
        if sensor.SensorType == u'Load' and sensor.Name == "Memory":
            ram_used = sensor.Value
        if sensor.SensorType == u'Load' and sensor.Name == "Total Activity" and sensor.Parent == DISK_ID:
            hdd_used = sensor.Value
    realized_speed = cpu_speed / MAX_CPU_MHZ
    acutal_cpu = cpu_total * realized_speed
    # Round the CPU utilization to the nearest whole number
    acutal_cpu = round(acutal_cpu)
    values.append(("CPU", acutal_cpu))
    ram_used = round(ram_used)
    values.append(("RAM", ram_used))
    if hdd_used:
        hdd_used = round(hdd_used)
        values.append(("DISK", hdd_used))
    
    return values

def get_network():
    values = []
    
    # Connect to the OpenHardwareMonitor namespace
    w = wmi.WMI(namespace="root\\LibreHardwareMonitor")

    # Get temperature sensor information
    values_infos = w.Sensor()

    # Iterate through sensors and print CPU temperature
    up = 0
    down = 0
    for sensor in values_infos:
        if sensor.Name == "Upload Speed":
            up = sensor.Value + up
        if sensor.Name == "Download Speed":
            down = sensor.Value + down
    up = round(up / 1024 / 128)
    down = round(down / 1024 / 128)
    values.append(up)
    values.append(down)
    
    return values

def get_disk():
    values = []
    
    # Connect to the OpenHardwareMonitor namespace
    w = wmi.WMI(namespace="root\\LibreHardwareMonitor")

    # Get temperature sensor information
    values_infos = w.Sensor()

    # Iterate through sensors and print CPU temperature
    up = 0
    down = 0
    for sensor in values_infos:
        if sensor.Name == "Read Rate":
            up = sensor.Value + up
        if sensor.Name == "Write Rate":
            down = sensor.Value + down
    up = round(up / 1024 / 1024)
    down = round(down / 1024 / 1024)
    values.append(up)
    values.append(down)
    
    return values

# Create a new Tkinter window
window = Tk()
window.attributes('-alpha', 1.0)
window.attributes('-topmost', 1)  # This line keeps the window on top
 
# Hide the window bar
window.overrideredirect(True)

# Variables to store the mouse position
start_x = None
start_y = None

def start_move(event):
    global start_x, start_y
    start_x = event.x
    start_y = event.y

def stop_move(event):
    global start_x, start_y
    x = window.winfo_x() + event.x - start_x
    y = window.winfo_y() + event.y - start_y
    window.geometry("+%s+%s" % (x, y))

# Bind the mouse button press and release events
window.bind('<Button-1>', start_move)
window.bind('<B1-Motion>', stop_move)

# Set the window to be transparent
window.wm_attributes('-alpha', 0.5)


# Make the window always stay on top
window.attributes('-topmost', 1)

# Create a canvas to draw on
# Create a canvas to draw on
temps = get_temperatures()
height=ROW_HEIGHT * (len(temps)+2) +10
canvas = Canvas(window, width=WIDTH, height=height, bd=0, highlightthickness=0, bg='black')


# Create a red "X" in the upper right that closes the window when clicked
close_button = canvas.create_text(window.winfo_width() - 10, 10, anchor='ne', font=("Arial", 8), fill='white', text="X")

def close_window(event):
    window.destroy()

canvas.tag_bind(close_button, '<Button-1>', close_window)
canvas.pack()

# Position the window at the lower left of the screen, 200 pixels from the bottom
window.geometry('+%d+%d' % (X_LOCATION, window.winfo_screenheight() - window.winfo_height() - Y_LOCATION))

# Create a dictionary to store the last 10 temperatures for each GPU
last_n_temps = {}
device_elements = []

def update_temperatures():
    # Fetch the temperatures
    temps = get_temperatures()
    utils = get_utilizations()

    # Check if the window is outside the screen's dimensions
    if window.winfo_x() < 0 or window.winfo_x() > window.winfo_screenwidth() or window.winfo_y() < 0 or window.winfo_y() > window.winfo_screenheight():
        # If it is, reset the window's position to the starting position
        window.geometry('+%d+%d' % (0, window.winfo_screenheight() - window.winfo_height() - 180))

    # Make the window always stay on top, but without taking focus
    window.attributes('-topmost', 1)

    # Prevent the window from taking focus when it is initially created
    window.overrideredirect(True)
    
    # Set the canvas height based on the number of GPUs
    canvas.config(width=WIDTH, height=ROW_HEIGHT * (len(temps)+2))
    
    # Set the window height based on the number of GPUs
    window.geometry(f'{WIDTH}x{ROW_HEIGHT * len(temps)}+{window.winfo_x()}+{window.winfo_y()}')
    window.attributes('-alpha', 1.0)

    # Remove the old Device elements
    for circle, text in device_elements:
        canvas.delete(circle)
        canvas.delete(text)
    device_elements.clear()
    
    net_row = 0
    # Calculate the average temperature for each GPU and create the new elements
    for i, (device_name, temp) in enumerate(temps):
        # If this is a new GPU, create a new deque for it
        if device_name not in last_n_temps:
            last_n_temps[device_name] = deque(maxlen=NUM_SAMPLES)
        
        # Append the temperature to the deque
        last_n_temps[device_name].append(temp)
        
        # Calculate the average temperature and round it to the nearest whole number
        avg_temp = round(sum(last_n_temps[device_name]) / len(last_n_temps[device_name]))
        
        # Determine the color of the circle based on the average temperature
        if avg_temp < CAUTION_TEMP:
            color = 'green'
        elif avg_temp <= DANGER_TEMP:
            color = 'yellow'
        else:
            color = 'red'
        
        # Create the circle and text elements with the color determined above
        try:
            
            if utils[i][1] > UTILIZATION_CAUTION:
                if color == 'red':
                    # Heat overrides utilization warning
                    shape = canvas.create_oval(5, 5 + i * ROW_HEIGHT, ROW_HEIGHT, ROW_HEIGHT + i * ROW_HEIGHT, fill=color)
                else:
                    util_color = 'yellow'
                    shape = canvas.create_rectangle(5, 5 + i * ROW_HEIGHT, ROW_HEIGHT, ROW_HEIGHT + i * ROW_HEIGHT, fill=util_color)
            else:
                shape = canvas.create_oval(5, 5 + i * ROW_HEIGHT, ROW_HEIGHT, ROW_HEIGHT + i * ROW_HEIGHT, fill=color)
            text = canvas.create_text(25, 15 + i * ROW_HEIGHT, anchor='w', font=("Arial", FONT_SIZE), fill='white', text=f"{device_name}\t|\t{avg_temp}°\t|\t{utils[i][1]}%")
        except:
            continue
    
        # Add the elements to the list
        device_elements.append((shape, text))
        net_row = i
    # Add Network Up and Down
    net = get_network()
    i = net_row + 1
    color = 'blue'
    total_net = net[0] + net[1]
    if total_net > 0:
        color = 'green'
    if total_net > NETOPS_CAUTION:
        color = 'yellow'
    shape = canvas.create_rectangle(5, 5 + i * ROW_HEIGHT, ROW_HEIGHT, ROW_HEIGHT + i * ROW_HEIGHT, fill=color)
    text = canvas.create_text(25, 15 + i * ROW_HEIGHT, anchor='w', font=("Arial", FONT_SIZE), fill='white', text=f"NET IO\t|\t{net[0]}Mb ↑\t|\t {net[1]}Mb ↓")
    device_elements.append((shape, text))

    #Add Disk Ops
    disk = get_disk()
    i = i + 1
    color = 'blue'
    total_disk = disk[0] + disk[1]
    if total_disk > 0:
        color = 'green'
    if total_disk > DISKOPS_CAUTION:
        color = 'yellow'
    shape = canvas.create_rectangle(5, 5 + i * ROW_HEIGHT, ROW_HEIGHT, ROW_HEIGHT + i * ROW_HEIGHT, fill=color)
    text = canvas.create_text(25, 15 + i * ROW_HEIGHT, anchor='w', font=("Arial", FONT_SIZE), fill='white', text=f"DISK IO\t|\t{disk[0]}MB ↑\t|\t{disk[1]}MB ↓")
    device_elements.append((shape, text))
    # Remember the window's current position and size
    x = window.winfo_x()
    y = window.winfo_y()

    height = window.winfo_height()
    
    # Resize the window and canvas to fit the new elements
    window.geometry(f'{WIDTH}x{height}+{x}+{y}')
    canvas.config(width=WIDTH, height=30 * (len(temps)+2))
    
    # Schedule the next update
    window.after(POLL_INTERVAL_MS, update_temperatures)

# Schedule the first update
window.after(POLL_INTERVAL_MS, update_temperatures)

def update_close_button_position():
    canvas.coords(close_button, window.winfo_width() - 10, 10)

# Call this function after the window is displayed
window.after(1, update_close_button_position)
# Run the Tkinter main loop
window.mainloop()