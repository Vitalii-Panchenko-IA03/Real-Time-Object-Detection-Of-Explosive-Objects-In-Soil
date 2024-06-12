"""
Used for calculating predistortion and VCO output frequency values for different waveforms
"""

from scipy import interpolate
import numpy as np

# Frequency and voltage values:
N0 = 200  # default number of values
# V_MIN   = 0.0    # V
# V_MAX   = 20.0   # V
# F_MIN   = 1400.0 # MHz
# F_MAX   = 3323.1 # 3323.1 MHz <--> 20.0 V
pic_num = 1

# Approximate data for CVCO55BE-1600-3200 operating under t=+25 C:
V_act = np.array([0.00, 0.5, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00,
                  8.00, 9.00, 10.00, 11.00, 12.00, 13.00, 14.00,
                  15.00, 16.00, 17.00, 18.00, 19.00, 20.00])
f_act = np.array([1400.0, 1474.6, 1500.0, 1650.0, 1780.0, 1920.0, 2050.0, 2150.0, 2250.0,
                  2400.0, 2470.0, 2551.3, 2680.0, 2750.0, 2800.0, 2950.0,
                  3000.0, 3080.0, 3200.0, 3240.0, 3280.0, 3323.1])

# Amplifier scaling coefficient: DAC's 5.5 V are later turned into 20.0 V by the amplifier:
amp_scale = 5.5 / 20.0
V_act = V_act * amp_scale
# Interpolating actual data into a regular grid with N values:
interp_func = interpolate.interp1d(V_act, f_act)
interp_coeff = 4  # interpolation coefficient
V_act_intr = np.linspace(0, 20 * amp_scale, N0 * interp_coeff, endpoint=True)
f_act_intr = interp_func(V_act_intr)


# Triangular wave:
def W_form_triang(f_min_tr, f_max_tr, T, N=N0):
    f_triang = np.empty(N)
    dt = T / N  # ms
    coeff_tr = 2 * (f_max_tr - f_min_tr) / T  # Triangular wave tangent

    # Calculate VCO output frequency values [N] for a triangular wave:
    for i in range(0, N):
        t = i * dt  # Current time value
        if 0 <= t < T / 2:
            f_triang[i] = (coeff_tr * t + f_min_tr)  # The straight line equation
        elif T / 2 <= t < T:
            f_triang[i] = (-coeff_tr * t + 2 * f_max_tr - f_min_tr)  # The straight line equation
    return f_triang


# Rectangular wave:
def W_form_rectang(f_min_rec, f_max_rec, T, N=N0):
    f_rectang = np.empty(N)
    dt = T / N  # ms
    # Calculate VCO output frequency values [N] for a rectangular wave:
    for i in range(0, N):
        t = i * dt  # Current time value
        if 0 <= t < T / 2:
            f_rectang[i] = f_max_rec
        elif T / 2 <= t < T:
            f_rectang[i] = f_min_rec
    return f_rectang


# Sawtooth wave:
def W_form_sawtooth(f_min_s, f_max_s, T, N=N0):
    f_sawtooth = np.empty(N)
    dt = T / N  # ms
    coeff_s = (f_max_s - f_min_s) / ((N - 1) * dt)  # Sawtooth wave tangent
    # Calculate VCO output frequency values [N] for a sawtooth wave:
    for i in range(0, N):
        t = i * dt  # Current time value
        f_sawtooth[i] = (coeff_s * t + f_min_s)  # The straight line equation
    return f_sawtooth


# No transmission:
def W_form_no(f_min_n, N=N0):
    f_no = np.empty(N)
    # Calculate VCO output frequency values [N]:
    for i in range(0, N):
        f_no[i] = f_min_n
    return f_no


# Function for calculation and predistortion of DAC voltages for the desired VCO output:
def find_nearest(array, value):  # Function for finding a value nearest to the given value in the array:
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx  # Returns the nearest value and its index


# Calculates DAC voltages required for the VCO producing f_desired,
# in accordance with the documented non-linear dependence f(V):
def predistort(f_desired):
    N = len(f_desired)
    f_dac = np.empty(N)
    DAC_values = np.empty(N)
    # Correlate desired freq values with the documented ("actual_interpolated") values:
    for i in range(0, N):
        f_dac[i], idx = find_nearest(f_act_intr, f_desired[i])  # find actual freq value nearest to the desired freq
        DAC_values[i] = V_act_intr[idx]
    return DAC_values
