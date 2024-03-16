from tkinter import Tk, Canvas
from collections import deque
import gpustat
import wmi

# Set the temperature thresholds
CAUTION_TEMP= 75
DANGER_TEMP= 90
# Set the polling interval in milliseconds
POLL_INTERVAL_MS = 1000
# Set the number of temperature samples to keep
NUM_SAMPLES = 10

def get_temperatures():
    temps = []
    # Get GPU temperatures
    stats = gpustat.new_query()
    id = 0
    for gpu in stats.gpus:
        device_name = "GPU " + str(id)
        id += 1
        temps.append((device_name, gpu.temperature))
    
    # Get CPU temperature
    # Connect to the OpenHardwareMonitor namespace
    w = wmi.WMI(namespace="root\\LibreHardwareMonitor")

    # Get temperature sensor information
    temperature_infos = w.Sensor()

    # Iterate through sensors and print CPU temperature
    for sensor in temperature_infos:
        if sensor.SensorType == u'Temperature' and sensor.Name == "Core Average":
            temps.append(("CPU  ", sensor.Value))
    
    return temps

# Create a new Tkinter window
window = Tk()
window.attributes('-alpha', 1.0)

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
height=30 * len(temps)
canvas = Canvas(window, width=100, height=height, bd=0, highlightthickness=0, bg='black')

# Pack the canvas with 30% padding
canvas.pack(padx=0.3*window.winfo_width(), pady=0.3*window.winfo_height())
# Create a red "X" in the upper right that closes the window when clicked
close_button = canvas.create_text(window.winfo_width() - 10, 10, anchor='ne', font=("Arial", 8), fill='red', text="X")

def close_window(event):
    window.destroy()

canvas.tag_bind(close_button, '<Button-1>', close_window)
canvas.pack()

# Position the window at the top right of the screen
window.geometry('+%d+%d' % (window.winfo_screenwidth()-120, 10))

# Create a dictionary to store the last 10 temperatures for each GPU
last_n_temps = {}
device_elements = []

def update_temperatures():
    # Fetch the temperatures
    temps = get_temperatures()
    
    # Set the canvas height based on the number of GPUs
    canvas.config(width=100, height=30 * len(temps))
    
    # Set the window height based on the number of GPUs
    window.geometry(f'100x{30 * len(temps)}+{window.winfo_x()}+{window.winfo_y()}')
    window.attributes('-alpha', 1.0)

    # Remove the old Device elements
    for circle, text in device_elements:
        canvas.delete(circle)
        canvas.delete(text)
    device_elements.clear()
    
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
        circle = canvas.create_oval(5, 5 + i * 30, 20, 20 + i * 30, fill=color)
        text = canvas.create_text(25, 15 + i * 30, anchor='w', font=("Arial", 8), fill='yellow', text=f"{device_name}: {avg_temp}°")
    
        # Add the elements to the list
        device_elements.append((circle, text))
    
    # Remember the window's current position and size
    x = window.winfo_x()
    y = window.winfo_y()
    width = window.winfo_width()
    height = window.winfo_height()
    
    # Resize the window and canvas to fit the new elements
    window.geometry(f'{width}x{height}+{x}+{y}')
    canvas.config(width=100, height=30 * len(temps))
    
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