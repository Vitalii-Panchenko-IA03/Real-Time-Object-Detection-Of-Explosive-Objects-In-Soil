"""
Used to show GUI for GPR interaction
"""

from tkinter import Scale, Button, VERTICAL, Tk, Menu, messagebox, Label, TclError
from struct import pack

import serial
from numpy import append
import calculateDACwithPredistortion as dac  # Functions available: W_form_triang, W_form_rectang(),
#                                                                 W_form_sawtooth(), predistort()

# Configure the Serial port:
# Change COM number according to your PC connection
ser = serial.Serial("COM3", baudrate=9600, bytesize=8, parity='N',
                    stopbits=1, timeout=None, rtscts=1)

# Default Signal Parameters:
# (F_max should be changed for the new RF-chain with the voltage amplifier)
num_values = 200  # must be even
F_min_df = 1400.0  # Minimum frequency of the radar signal [MHz]  # 0.0 V <-> 1400.0 MHz
F_max_df = 3323.1  # Maximum frequency of the radar signal [MHz]  # 5.5 V <-> 2100.0 MHz, 20.0 V <-> 3323.1 MHz
T_df = 20  # Period of the signal in [ms]
W_form_df = 1  # 1 - triangular, 2 - rectangular, 3 - sawtooth waveforms, (4 - no transmission)

# Create a main window:
window = Tk()

# Set geometry and title of the main window:
window.geometry('1100x400+200+100')  # Size of the window(x,y) + position on screen (x,y)
window.minsize(width=1000, height=300)
window.title('GPR Control Panel')

explanation = "GUI to interact with GPR"
WelcomeText = Label(window,
                    font=("Baskerville Old Face", "10", "bold"), foreground='blue',
                    text=explanation).pack(side="top")


# Function "HelpBox" to show info about the program:
def helpBox():
    messagebox.showinfo(title="Help", message="To change the frequency range set Fmin[MHz] value with the first slider "
                                              "and Fmax[MHz] value with the second slider. Set the period T[ms] of the waveform with the third slider, "
                                              "set the desired waveform with the fourth slider:\n\n\
                  1. Set the desired values of the four sliders\n\n\
                  2. Press confirm button to send the new instruction to\n         the microcontroller\n\n\
                  3. Press stop button to stop the GPR")


# Function to close the program:
def closeWindow():
    confirmation = messagebox.askokcancel(title="Exit", message="Do you want to exit?")
    if confirmation:
        window.destroy()  # Destroy the main window


# Creation of the MENU:
bar_menu = Menu(window)

menu_file = Menu(bar_menu, tearoff=0)  # tearoff=1 to get external menu
bar_menu.add_cascade(label="File", menu=menu_file)  # Create One Menu
menu_file.add_command(label="Help", command=helpBox)  # Adding Sub-Menu//recall "helpBox" function
menu_file.add_command(label="Exit", command=closeWindow)  # Command to recall   "closeWindow" function
window.config(menu=bar_menu)  # Configuration of the Menu


# Create SLIDER function:
def getSlider():
    if sldFmin.get() < sldFmax.get():
        # Get values from sliders:
        F_min = sldFmin.get()
        F_max = sldFmax.get()
        T = sldT.get()
        W_form = sldW.get()

        # Calculate desired VCO frequencies:
        if W_form == 1:
            f_desired = dac.W_form_triang(F_min, F_max, T)
        elif W_form == 2:
            f_desired = dac.W_form_rectang(F_min, F_max, T)
        elif W_form == 3:
            f_desired = dac.W_form_sawtooth(F_min, F_max, T)

        # Calculate DAC voltage for f_desired:
        DAC_values = dac.predistort(f_desired)

        # Transmit data to microcontroller:
        dt = T * 1000 / num_values  # *1000 - ms-->us, dt is time between DAC's updates
        DAC_values /= 5.5  # normalize by 5.5 V for microcontroller Analog Output ( - accepts 0...1)

        values_to_pack = append(DAC_values, dt)  # uniting two arrays
        str_packed = pack('%sf' % len(values_to_pack), *values_to_pack)  # pack each value into a float - 4 bytes
        num_bytes = ser.write(str_packed)  # Sending data to microcontroller through Serial

        # Warning if F_min < F_max:
    else:
        messagebox.showinfo(title="Warning",
                            message="Minimum frequency value (Fmin) cannot be higher than maximum frequency "
                                    "value (Fmax), please adjust the frequency border")


# Create no-transmission function:
def stopGPR():
    F_min = F_min_df  # Using default values
    T = T_df

    # Calculate desired VCO frequencies:
    f_desired = dac.W_form_no(F_min)
    # Calculate DAC voltage for f_desired:
    DAC_values = dac.predistort(f_desired)

    # Transmit data to microcontroller:
    dt = T * 1000 / num_values  # *1000 - ms-->us, dt is time between DAC's updates
    DAC_values /= 5.5  # normalize by 5.5 V for microcontroller Analog Output ( - accepts 0...1)
    values_to_pack = append(DAC_values, dt)
    str_packed = pack('%sf' % len(values_to_pack), *values_to_pack)  # pack each value into a float - 4 bytes
    num_bytes = ser.write(str_packed)  # Sending data to microcontroller through Serial


# Confirmation buttons to get the Sliders values and send them to microcontroller:
getB = Button(window, text="Confirm and send to Microcontroller", command=getSlider)
getB.pack(side="bottom", expand=1, fill="none")  # Place at the bottom of the window
getB.configure(font=("Baskerville Old Face", "10", "bold"), foreground='blue')

# Stop button:
stopB = Button(window, text="Stop", command=stopGPR)
stopB.pack(side="bottom", expand=1, fill="none")
stopB.configure(font=("Adobe Hebrew", "9", "bold"))

# Create four SLIDERS to set Fmin, Fmax, T  and Waveform:
# 'tickinterval' - desplayed slider steps, 'resolution' - actual slider steps

# F_min Slider
sldFmin = Scale(window, from_=F_min_df, to=F_max_df, orient=VERTICAL, length=300, width=20, sliderlength=50,
                tickinterval=20, resolution=5)
sldFmin.set(0)
sldFmin.pack(side="left", expand=1)  # side = "left" to place all sliders in the same row

freqmin = "Fmin\n[MHz]"
label1 = Label(text=freqmin, font=("Adobe Hebrew", "10", "bold"))  # Insert Label Fmin near its slider
label1.pack(side="left")

# F_max Slider
sldFmax = Scale(window, from_=F_min_df, to=F_max_df, orient=VERTICAL, length=300, width=20, sliderlength=50,
                tickinterval=20, resolution=5)
sldFmax.set(F_max_df)
sldFmax.pack(side="left", expand=1)

freqmax = "Fmax\n[MHz]"
label2 = Label(text=freqmax, font=("Adobe Hebrew", "10", "bold"))
label2.pack(side="left")

# T Slider
sldT = Scale(window, from_=10, to=100, orient=VERTICAL, length=300, width=20, sliderlength=50, tickinterval=10,
             resolution=10)
sldT.set(0)
sldT.pack(side="left", expand=1)

period = "Period\nT[ms]"
label3 = Label(text=period, font=("Adobe Hebrew", "10", "bold"))
label3.pack(side="left", expand=1)

# W_form Slider
sldW = Scale(window, from_=1, to=3, orient=VERTICAL, length=300, width=20, sliderlength=50, tickinterval=1,
             resolution=1)
sldW.set(0)
sldW.pack(side="left", expand=1)

wave = "Waveform:\n\n1=triangular,\n\n2=rectangular,\n\n3=sawtooth"
label4 = Label(text=wave, font=("Adobe Hebrew", "10", "bold"))
label4.pack(side="left", expand=1)

# Start the Main loop:
window.mainloop()
