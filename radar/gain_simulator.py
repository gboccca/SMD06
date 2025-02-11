import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import pi,c

'''


NOTE: this is kinda stupid becasue it turns out we knew all along that gain is roughly a linear function of the number of elements in the array.


'''

################ FUNCTIONS ################

# Calculate sterring vector



# this is the function to edit in case the lobes at singularity angles are actually wrong
def steering_vector(k, xv, yv, theta_deg, phi_deg):

    theta = np.radians(theta_deg)
    phi = np.radians(phi_deg)

    kx = k * np.sin(theta) * np.cos(phi)
    ky = k * np.sin(theta) * np.sin(phi)

    # Calculate the phase shift for each element
    phase_weights = np.exp(1j * (kx * xv + ky * yv))

    return phase_weights



def dBi_to_linear(dBi):
  """Converts dBi to linear scale."""
  return 10**(dBi / 10)



def antenna_element_pattern(theta: np.ndarray, phi: np.ndarray,
                             cos_factor_theta: float = 1.0, cos_factor_phi: float = 1.0,
                             max_gain_dBi: float = 0.0) -> np.ndarray:
  """
  Calculates the radiation pattern of a single antenna element using a raised cosine model.

  Args:
    theta: Elevation angles in radians (numpy.ndarray).
    phi: Azimuth angles in radians (numpy.ndarray).
    cos_factor_theta: Cosine power factor for theta (float, default=1.0).
    cos_factor_phi: Cosine power factor for phi (float, default=1.0).
    max_gain_dBi: Maximum gain of the element pattern in dBi (float, default=0.0).

  Returns:
    A numpy array containing the element pattern values in linear scale.
  """

  # Convert max gain from dBi to linear scale
  max_gain = dBi_to_linear(max_gain_dBi)

  # Calculate the radiation pattern
  pattern = max_gain * np.cos(theta) ** cos_factor_theta * np.cos(phi) ** cos_factor_phi

  return pattern



def test_antenna_element_pattern():

  theta = np.radians(np.linspace(-90, 90, 180))
  phi = np.radians(np.linspace(-90, 90, 180))

  THETA, PHI = np.meshgrid(theta, phi)
  pattern = antenna_element_pattern(THETA, PHI)



def azel_to_thetaphi(az, el):
    """ Az-El to Theta-Phi conversion.

    Args:
        az (float or np.array): Azimuth angle, in radians
        el (float or np.array): Elevation angle, in radians

    Returns:
      (theta, phi): Tuple of corresponding (theta, phi) angles, in radians
    """

    cos_theta = np.cos(el) * np.cos(az)
    # tan_phi = np.where(np.abs(np.sin(az)) < 1e-6, 0, np.tan(el) / np.sin(az)) # Avoid the divide by zero

    theta     = np.arccos(cos_theta)
    phi       = np.arctan2(np.tan(el), np.sin(az))
    phi = (phi + 2 * np.pi) % (2 * np.pi)

    return theta, phi


def thetaphi_to_azel(theta, phi):
    """ Az-El to Theta-Phi conversion.

    Args:
        theta (float or np.array): Theta angle, in radians
        phi (float or np.array): Phi angle, in radians

    Returns:
      (az, el): Tuple of corresponding (azimuth, elevation) angles, in radians
    """


    sin_el = np.sin(phi) * np.sin(theta)
    tan_az = np.cos(phi) * np.tan(theta)
    el = np.arcsin(sin_el)
    az = np.arctan(tan_az)

    return az, el


def AF(theta, phi, x, y, w, k):
  """
  Calculates the array factor for a given set of angles, coordinates, weights, and wave number.

  Args:
    theta: Elevation angle in radians.
    phi: Azimuth angle in radians.
    x: X-coordinates of the antenna elements.
    y: Y-coordinates of the antenna elements.
    w: Complex weights of the antenna elements.
    k: Wave number.

  Returns:
    The array factor as a complex number.
  """

  N = len(x)  # Number of antenna elements

  # Calculate the phase shift for each antenna element
  phase_shift = -1j * k * (x * np.sin(theta) * np.cos(phi) + y * np.sin(theta) * np.sin(phi))

  # Reshape the complex weights into a 1-D vector
  w_vec = w.reshape(-1)

  # Multiply the weights by the phase shift and sum them up
  AF = np.sum(w_vec * np.exp(phase_shift))

  return AF



def wrap_angle(angle):
  """
  Wraps an angle value between 0 and 2 pi.

  Args:
    angle: The angle value in radians.

  Returns:
    The wrapped angle value between 0 and 2 pi.
  """

  return angle % (2 * np.pi)


def test_wrap_angle():
  angle_in_radians = 10  # Example angle
  wrapped_angle = wrap_angle(angle_in_radians)
  print(f"Wrapped angle: {np.round(wrapped_angle, 2)} radians")

# test_wrap_angle()

################### PROCESS ##############################





def calculate_gain(Nx,Ny):
    dx = 0.5  # spacing between elements in the x-direction (in wavelengths)
    dy = dx  # spacing between elements in the y-direction (in wavelengths)
    freq_GHz = 50.0 # frequency (GHz), based on a wavelength of 6mm

    system_losses_dB = 0
    ep_max_gain_dBi = 0 # Max gain of the element pattern (EP)
    cos_factor_theta = 1.2 # Raised cosine factor of the EP in theta
    cos_factor_phi = 1.2 # Raised cosine factor of the EP in phi

    # Derived antenna parameters
    f = 1e9 * freq_GHz  # convert frequency to Hz
    lambda_ = c / f  # wavelength (meters)
    k = 2 * pi / lambda_ # wave vector

    # Express grid spacing in meters
    dx_m = dx * lambda_
    dy_m = dy * lambda_

    # Compute approximate aperture directivity
    aperture_area = Nx * Ny * dx_m * dy_m
    D = 4 * pi * aperture_area / lambda_**2
    D_dBi = 10 * np.log10(D)

    # Estimate 3 dB beamwidth (BW) at broadside for the array aperature
    beamwidth_broadside_x = 0.886 * lambda_ / (Nx * dx_m)
    beamwidth_broadside_y = 0.886 * lambda_ / (Ny * dy_m)

    # Number of Array Elements
    num_elements = Nx * Ny


    # Beam steering angles
    theta0 = 30 # Beam steering angle in theta (degrees)
    phi0 = 45 # 0Beam steering angle in phi (degrees)




    # Define element locations for a triangular array

    # Element positions in x and y directions (assuming origin is at the center)
    x = np.arange(Nx) - (Nx - 1) / 2
    y = np.arange(Ny) - (Ny - 1) / 2

    # Adjust y positions for triangular grid
    y = y * np.sqrt(3) / 2

    # Create mesh grid for triangular array
    X, Y = np.meshgrid(x, y)

    # Offset every other row to create the triangular pattern
    X[1::2, :] += 0.5

    # Scale by element spacing
    X = X * dx_m
    Y = Y * dy_m

    # Transform X and Y into 1-D vectors
    X_vec = X.reshape(-1)
    Y_vec = Y.reshape(-1)



    phase_weights = steering_vector(k=k,
                                    xv=X,
                                    yv=Y,
                                    theta_deg=theta0,
                                    phi_deg=phi0)

    phase_shift_rad = np.angle(phase_weights)
    phase_shift_deg = np.degrees(phase_shift_rad)


    test_antenna_element_pattern()


    # Define observation angles
    theta_deg = np.linspace(-90, 90, 181)
    phi_deg = np.linspace(-90, 90, 181)

    theta = np.deg2rad(theta_deg)
    phi = np.deg2rad(phi_deg)

    # Make a meshgrid of theta and phi
    THETA, PHI = np.meshgrid(theta, phi)

    # Convert to azimuth and elevation
    AZ, EL = thetaphi_to_azel(THETA, PHI)


    array_factor = AF(theta[0], phi[0], x=X_vec, y=Y_vec, w=phase_weights, k=k)


    # Compute element pattern over all THETA, PHI angles
    element_pattern = antenna_element_pattern(THETA, PHI,
                                            cos_factor_theta,
                                            cos_factor_phi,
                                            max_gain_dBi=ep_max_gain_dBi)



    # Calculate the array factor for each angle
    array_factor = np.zeros((len(theta), len(phi)), dtype=complex)

    for i, thi in enumerate(theta):
        for j, phj in enumerate(phi):
            array_factor[i, j] = element_pattern[i, j] * AF(thi, phj, x=X_vec, y=Y_vec, w=phase_weights, k=k)

    array_factor_dB = 10 * np.log10(abs(array_factor))

    # Normalize array_factor_dB
    array_factor_dB_norm = array_factor_dB - np.max(array_factor_dB)


    # Normalize array_factor_dB
    array_gain_dBi = D_dBi - system_losses_dB + array_factor_dB_norm



    # If a value in power_pattern is less than a minimum threshold, set it to the minimum treshold for visualization purposes
    min_thres = np.max(array_factor_dB) - 50
    array_factor_plot_dB = array_factor_dB.clip(min=min_thres)

    min_thres = np.max(array_gain_dBi) - 50
    array_gain_plot_dBi = array_gain_dBi.clip(min=min_thres)




    # For array_factor_plot_dB, plot the theta and phi radiation pattern cuts where the other variable are the steer angles, respectively
    thres_dB = 30

    # Find index where phi_deg and theta_deg are the steer angles, respectively
    phi_zero_index = np.where(phi_deg == phi0)[0][0]
    theta_zero_index = np.where(theta_deg == theta0)[0][0]

    # Find the peak value in the data
    peak_value_theta = np.max(array_gain_plot_dBi[:, phi_zero_index])
    peak_value_phi = np.max(array_gain_plot_dBi[theta_zero_index, :])

    # Set the lower y-axis limit to 30 dB below the peak
    if np.max(array_gain_plot_dBi[:, phi_zero_index]) - np.min(array_gain_plot_dBi[:, phi_zero_index]) > thres_dB:
        lower_limit_theta = peak_value_theta - thres_dB

    if np.max(array_gain_plot_dBi[theta_zero_index, :]) - np.min(array_gain_plot_dBi[theta_zero_index, :]) > thres_dB:
        lower_limit_phi = peak_value_phi - thres_dB



    # print the maximum gain
    dB_max=np.max(array_gain_plot_dBi)
    return dB_max




if __name__ == """__main__""":

  print("Running the gain simulator...")
  print("This may take a while...")

  dB_max = []
  N_list = []

  # Antenna parameters
  Nx = np.round(np.logspace(0,np.log10(500),100)) # number of elements in the x-direction
  Ny = np.round(np.logspace(0,np.log10(500),100)) # number of elements in the y-direction

  for i in range(len(Nx)):
      dB_max.append(calculate_gain(Nx[i],Ny[i]))
      N = Nx[i]*Ny[i]
      print(f"Run #{i+1} completed. N: {N}. Gain: {dB_max[i]}.")
      N_list.append(N)


  # plot the gain
  plt.plot(N,dB_max)
  plt.xlabel('Number of elements')
  plt.ylabel('Gain [dB]')
  plt.title('Gain vs Number of elements')
  plt.show()

