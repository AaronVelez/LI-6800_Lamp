#%%                     Load libraries
from pathlib import Path 
import matplotlib.pyplot as plt
import numpy as np
import cv2
import pandas as pd





#%%                     Define functions

def extract_and_align_rectangle(image, target_size, adjustment=0):
    """
    Extracts and aligns a rectangle from a given 2D array with float64 depth, rotating it for minimal alignment adjustment 
    (within 6 degrees). The output is cropped to the specified target size, ensuring that the cropping is centered on the 
    newly oriented rectangle. An adjustment can be made to the cropping to account for small misalignments.

    Parameters:
        image (numpy.ndarray): The input 2D array containing an approximately centered rectangle.
        target_size (tuple): The desired size (height, width) of the output rectangle.
        adjustment (int): Adjustment for the cropping area to shift towards the lower right corner.

    Returns:
        numpy.ndarray: The extracted and aligned rectangle, in float64 depth, resized to target_size.
    """
    if image.dtype != np.float64:
        raise ValueError("Image must be a float64 numpy array.")

    # Normalize the image for processing
    norm_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')

    # Threshold to find contours
    _, thresh = cv2.threshold(norm_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour
    max_contour = max(contours, key=cv2.contourArea)

    # Calculate the centroid of the contour
    M = cv2.moments(max_contour)
    if M["m00"] == 0:
        return None  # Avoid division by zero
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    # Correct angle for minimal rotation
    rect = cv2.minAreaRect(max_contour)
    angle = rect[2]
    if angle < -45:
        angle += 90  # Normalize angle to be within [-45, 45]
    if not (-6 <= angle <= 6):
        angle = 0  # Apply no rotation if within ±6 degrees

    # Rotate the image to align the rectangle using the centroid
    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Adjusted cropping calculations with consideration for the adjustment factor
    target_height, target_width = target_size
    x_start = max(0, cx - (target_width // 2) + adjustment)
    y_start = max(0, cy - (target_height // 2) + adjustment)

    x_end = min(w, x_start + target_width)
    y_end = min(h, y_start + target_height)

    cropped = rotated[y_start:y_end, x_start:x_end]

    return cropped

def load_array_from_csv(file_path):
    """Load a 2D array from a CSV file."""
    return np.genfromtxt(file_path, delimiter='\t')

def load_arrays_by_index(index):
    mirror_path, black_path = path_pairs[index]
    mirror_file_path = base_dir / mirror_path
    black_file_path = base_dir / black_path
    arr_mirror = load_array_from_csv(mirror_file_path)
    arr_black = load_array_from_csv(black_file_path)
    return arr_mirror, arr_black

def find_center(arr):
    """Find the row and column index of the center of the array."""
    rows, cols = arr.shape
    center_row = rows // 2
    center_col = cols // 2
    return center_row, center_col

def trim_arrays(arr1, arr2):
    """Align centers and trim arrays to the minimum overlapping size."""
    center1 = find_center(arr1)
    center2 = find_center(arr2)
    
    # Determine the size of the overlap
    min_rows = min(center1[0], center2[0], arr1.shape[0] - center1[0], arr2.shape[0] - center2[0]) * 2
    min_cols = min(center1[1], center2[1], arr1.shape[1] - center1[1], arr2.shape[1] - center2[1]) * 2
    
    # Extract the subarrays
    sub_arr1 = arr1[center1[0] - min_rows // 2:center1[0] + min_rows // 2, center1[1] - min_cols // 2:center1[1] + min_cols // 2]
    sub_arr2 = arr2[center2[0] - min_rows // 2:center2[0] + min_rows // 2, center2[1] - min_cols // 2:center2[1] + min_cols // 2]
    
    return sub_arr1, sub_arr2

def save_array_to_csv(arr, file_name):
    """Save a 2D array to a CSV file with '_trimmed' suffix."""
    np.savetxt(file_name.replace('.csv', '_trimmed.csv'), arr, delimiter=',')

def cosine_correction(row, column, stepSize, height, maxRow, maxColumn, NA, n):
    # Calculate the center of the grid based on maximum row and column indices
    centerRow = maxRow // 2 
    centerColumn = maxColumn // 2 

    # Check if the array has even dimensions
    if maxRow % 2 == 0:
        # If even, adjust the center row
        if row >= centerRow:
            row += 1
    if maxColumn % 2 == 0:
        # If even, adjust the center column
        if column >= centerColumn:
            column += 1

    # Calculate the distances from the center to the specified row and column
    # Delta values represent the displacement from the center
    deltaRow = row - centerRow
    deltaColumn = column - centerColumn

    # Calculate the effective horizontal and vertical distances from the center
    # of the plane using the step size
    x = deltaColumn * stepSize  # Horizontal distance from center
    y = deltaRow * stepSize     # Vertical distance from center

    # Compute the effective distance (d) from the point to the plane's center
    # beneath the LED. This is calculated as the hypotenuse of a right triangle
    # formed by x and y distances
    d = np.sqrt(x**2 + y**2)

    # Calculate the angle of incidence, theta, using the distance d and the height
    # from the point to the LED. The atan function returns the arc tangent of d/height
    theta_rad = np.arctan(d / height)
    theta_deg = (theta_rad * 180) / np.pi

    # Calculate the cosine correction factor based on the angle of incidence
    # This factor is used to adjust the measured light intensity for the angle of incidence
    cosCorrection = 1 / np.cos(theta_rad)

    return {
        'theta_deg': theta_deg,
        'cosCorrection': cosCorrection,        
    }

# Wanted metrics for each corrected array:
# v2.0
def calculate_homogeneity_cv(corrected, coverage=0.9):
    """
    Calculate the homogeneity of a 2D array using the coefficient of variation (CV),
    which measures the extent of variability in relation to the mean of the sample.
    The function handles both square and non-square arrays by fitting a square region
    for analysis that is centered and scaled according to the specified coverage.

    Parameters:
        corrected (numpy.ndarray): 2D numpy array with light intensity measurements.
        coverage (float): Fraction of the total area for the centered square, default is 90%.

    Returns:
        float: Coefficient of variation (CV) expressed as a percentage.
    """
    # Determine the dimensions of the array
    rows, cols = corrected.shape

    # Calculate the scaling factor for each dimension
    scale_factor = np.sqrt(coverage)

    # Calculate the dimensions of the centered rectangle
    rect_height = int(rows * scale_factor)
    rect_width = int(cols * scale_factor)

    # Calculate start indices for slicing out the centered rectangle
    start_row = (rows - rect_height) // 2
    start_col = (cols - rect_width) // 2

    # Extract the centered rectangle
    centered_rect = corrected[start_row:start_row + rect_height, start_col:start_col + rect_width]

    # Calculate the mean and standard deviation of the values in the centered rectangle
    mean_intensity = np.mean(centered_rect)
    std_deviation = np.std(centered_rect)

    # Calculate the coefficient of variation as a percentage
    cv_percentage = (std_deviation / mean_intensity) * 100

    return cv_percentage

# v2.0
def find_area_for_cv(corrected, target_cv=10, initial_coverage=0.01, step_size=0.01, max_coverage=1):
    """
    Determine the percentage area of a 2D array that results in the coefficient of variation (CV%)
    just surpassing the target CV.

    Parameters:
        corrected (numpy.ndarray): 2D numpy array with light intensity measurements.
        target_cv (float): Target coefficient of variation (CV) expressed as a percentage.
        initial_coverage (float): Initial fractional area to start the search.
        step_size (float): Incremental step for area coverage increase.
        max_coverage (float): Maximum coverage limit for the search area.

    Returns:
        float: The percentage of the total area just before the CV surpasses the target CV.
    """
    rows, cols = corrected.shape
    best_area = 0  # Initialize the best area
    previous_area = 0  # To keep track of the area just before surpassing the target CV

    # Start with initial coverage and incrementally increase to find the appropriate area
    coverage = initial_coverage
    while coverage <= max_coverage:
        # Debug
        if True:
            print("Coverage: ", coverage)
            print("Previous Area: ", previous_area)
            print("Best Area: ", best_area)


        # Calculate dimensions of the centered rectangle
        scale_factor = np.sqrt(coverage)
        rect_height = int(rows * scale_factor)
        rect_width = int(cols * scale_factor)

        # Ensure the rectangle is centered
        start_row = (rows - rect_height) // 2
        start_col = (cols - rect_width) // 2
        centered_rect = corrected[start_row:start_row + rect_height, start_col:start_col + rect_width]

        # Calculate mean and standard deviation within the rectangle
        mean_intensity = np.mean(centered_rect)
        std_deviation = np.std(centered_rect)

        # Calculate current CV%
        current_cv = (std_deviation / mean_intensity) * 100

        # Break condition: current CV surpasses target CV
        if current_cv > target_cv:
            best_area = previous_area  # Use the area just before surpassing
            break

        # Update previous_area to the current coverage before increasing it
        previous_area = coverage * 100  # area percentage is the current coverage scaled up

        # Increment coverage
        coverage += step_size

    # In case current_cv is never more than the target_cv, area should be 100%
    if coverage >= max_coverage:
        best_area = coverage * 100
    
    print("Final coverage:", coverage)

    return best_area  # Return the best area percentage just before surpassing the target CV

def correction_summary(corrected):
    """
    Calculate the mean, median, standard deviation and the min and max values from the corrected array

    Parameters:
        corrected (numpy.ndarray): 2D numpy array with light intensity measurements.
    

    Returns:
        numpy.ndarray: mean, mode, median, standard deviation and the min and max values

    """
    a = np.mean(corrected)
    b = np.median(corrected)
    c = np.std(corrected)
    d = np.min(corrected)
    e = np.max(corrected)
   
    return a, b, c, d, e










#%%                     Create an empty dataframe to save the information form the corrected data
column_names = ['Sample', 'Homogeneity', 'CV', 'Mean', 'Median', 'SD', 'Min','Max']
df = pd.DataFrame(columns=column_names)









#%%                     Load arrays

# Setup paths
current_folder = Path(__file__).resolve().parent
base_dir = current_folder.parent / "Results"
plots_dir = base_dir / "Plots"

# File list
path_pairs = [
    ("4-5-2024_4.02 PM_NA39_Diff_3x3_Mirror_Rep1_RAW.csv", "4-9-2024_12.06 PM_NA39_Diff_3x3_Black_Rep1_RAW.csv"),               # Diffuser 3x3, Index 0
    ("4-8-2024_4.22 PM_NA39_Diff_2x3SS_Mirror_Rep1_RAW.csv", "4-9-2024_8.33 AM_NA39_Diff_2x3SS_Black_Rep1_RAW.csv"),            # Diffuser 2x3, Index 1
    ("4-8-2024_3.04 PM_NA39_Diff_1x3SS_Mirror_Rep1_RAW.csv", "4-9-2024_10.07 AM_NA39_Diff_1x3SS_Black_Rep1_RAW.csv"),           # Diffuser 1x3, Index 2
    ("4-10-2024_11.48 AM_NA39_No_Diff_3x3_Mirror_Rep1_RAW.csv", "4-11-2024_7.04 PM_NA39_No_Diff_3x3_Black_Rep1_RAW.csv"),       # No diffuser 3x3, Index 3
    ("4-10-2024_6.14 PM_NA39_No_Diff_2x3SS_Mirror_Rep1_RAW.csv", "4-11-2024_5.31 PM_NA39_No_Diff_2x3SS_Black_Rep1_RAW.csv"),    # No diffuser 2x3, Index 4
    ("4-10-2024_5.13 PM_NA39_No_Diff_1x3SS_Mirror_Rep1_RAW.csv", "4-11-2024_4.27 PM_NA39_No_Diff_1x3SS_Black_Rep1_RAW.csv")     # No diffuser 1x3, Index 5
]

target_size = [
    (154, 154),
    (104, 154),
    (54, 154),
    (154, 154),
    (104, 154),
    (54, 154),
]

# Distance from LI-6800 leaf chamber top to leaf plane = 16.6 mm
height_list = [
    (65.5 + 16.6),  # Distance from diffuser to LI-6800 leaf chamber top + 16.6 mm 
    (65.5 + 16.6),
    (65.5 + 16.6),
    (68.365 + 16.6), # Distance from LED to LI-6800 leaf chamber top + 16.6 mm 
    (68.365 + 16.6),
    (68.365 + 16.6),
]

index = 0  # Change as needed to load different pairs
arr_mirror_raw, arr_black_raw = load_arrays_by_index(index)

if index <= 2:
    Diff_ver = "_Diff"
else:
    Diff_ver = "_No_diff"

vmin = 0
vmax = 0.4










#%%                     Segment and align RAW measurements

arr_mirror = extract_and_align_rectangle(arr_mirror_raw, target_size[index], adjustment = 1)
plt.imshow(arr_mirror_raw,  cmap='plasma')
plt.title("RAW mirror")
plt.show()
plt.imshow(arr_mirror,  cmap='plasma')
plt.title("Segmented-Aligned mirror")
plt.show()

arr_black = extract_and_align_rectangle(arr_black_raw, target_size[index], adjustment = 1)
plt.imshow(arr_black_raw,  cmap='plasma')
plt.title("RAW black")
plt.show()
plt.imshow(arr_black,  cmap='plasma')
plt.title("Segmented-Aligned black")
plt.show()








#%%
#Mirror
plt.imshow(arr_mirror, cmap='plasma', vmin=vmin, vmax=vmax)

#Adjust the ticks of x and y axis
#X ticks
newx_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
newx_ticks = np.linspace(-0.5, arr_mirror.shape[1]-0.5, len(newx_labels))
plt.xticks(newx_ticks,newx_labels, rotation = 0)

#Y ticks
if arr_mirror.shape[0] >= 150:
    newy_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
    new_ticks = np.linspace(-0.5, arr_mirror.shape[0]-0.5, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
elif arr_mirror.shape[0] < 150 and arr_mirror.shape[0]>=100:
    newy_labels = [0.0, 5.0, 10.0, 15.0, 20.0]
    new_ticks = np.linspace(-0.5, arr_mirror.shape[0]-0.5, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
else :
    newy_labels = [0.0, 2.5, 5.0, 7.5, 10.0]
    new_ticks = np.linspace(-0.5, arr_mirror.shape[0]-0.5, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)




plt.colorbar().set_label('Voltage (mV)',rotation=270, labelpad=10)
plt.xlabel("Front face (mm)")
plt.ylabel("Lateral Face (mm)")
plt.title('Mirror')

filename= "Mirror_" + f"{int(newy_labels[-1]/10)}x{int(newx_labels[-1]/10)}" + Diff_ver + ".svg"
plt.savefig(str(plots_dir /  filename), format='svg', bbox_inches='tight')
plt.show()


#black
plt.imshow(arr_black, cmap='plasma', vmin=vmin, vmax=vmax)
#Adjust the ticks of x and y axis
#X ticks
newx_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
newx_ticks = np.linspace(-0.5, arr_black.shape[1]-0.5, len(newx_labels))
plt.xticks(newx_ticks,newx_labels, rotation = 0)

#Y ticks
if arr_black.shape[0] >= 150:
    newy_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
    new_ticks = np.linspace(-0.5, arr_black.shape[0]-0.5, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
elif arr_black.shape[0] < 150 and arr_black.shape[0]>=100:
    newy_labels = [0.0, 5.0, 10.0, 15.0, 20.0]
    new_ticks = np.linspace(-0.5, arr_black.shape[0]-0.5, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
else :
    newy_labels = [0.0, 2.5, 5.0, 7.5, 10.0]
    new_ticks = np.linspace(-0.5, arr_black.shape[0]-0.5, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)


plt.xlabel("Front face (mm)")
plt.ylabel("Lateral Face (mm)")
plt.colorbar().set_label('Voltage (mV)',rotation=270, labelpad=10)
plt.title('Black')


filename= "Black_" + f"{int(newy_labels[-1]/10)}x{int(newx_labels[-1]/10)}" + Diff_ver + ".svg"
plt.savefig(str(plots_dir /  filename), format='svg', bbox_inches='tight')
plt.show()






#%%
# Trim arrays
trimmed_mirror, trimmed_black = trim_arrays(arr_mirror, arr_black)

#Trim_mirror
plt.imshow(trimmed_mirror, cmap='plasma', vmin=vmin, vmax=vmax)
#Adjust the ticks of x and y axis
#X ticks
newx_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
newx_ticks = np.linspace(2, trimmed_mirror.shape[1]-2, len(newx_labels))
plt.xticks(newx_ticks,newx_labels, rotation = 0)

#Y ticks
if trimmed_mirror.shape[0] >= 150:
    newy_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
    new_ticks = np.linspace(2, trimmed_mirror.shape[0]-2, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
elif trimmed_mirror.shape[0] < 150 and trimmed_mirror.shape[0]>=100:
    newy_labels = [0.0, 5.0, 10.0, 15.0, 20.0]
    new_ticks = np.linspace(2, trimmed_mirror.shape[0]-2, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
else :
    newy_labels = [0.0, 2.5, 5.0, 7.5, 10.0]
    new_ticks = np.linspace(2, trimmed_mirror.shape[0]-2, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)


plt.colorbar().set_label('Voltage (mV)',rotation=270, labelpad=10)
plt.xlabel("Front face (mm)")
plt.ylabel("Lateral Face (mm)")
plt.title('Trimmed Mirror')

filename= "Trim_Mirror_" + f"{int(newy_labels[-1]/10)}x{int(newx_labels[-1]/10)}" + Diff_ver + ".svg"
plt.savefig(str(plots_dir /  filename), format='svg', bbox_inches='tight')
plt.show()


#Trim Black
plt.imshow(trimmed_black, cmap='plasma', vmin=vmin, vmax=vmax)
#X ticks
newx_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
newx_ticks = np.linspace(2, trimmed_black.shape[1]-2, len(newx_labels))
plt.xticks(newx_ticks,newx_labels, rotation = 0)

#Y ticks
if trimmed_black.shape[0] >= 150:
    newy_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
    new_ticks = np.linspace(2, trimmed_black.shape[0]-2, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
elif trimmed_black.shape[0] < 150 and trimmed_black.shape[0]>=100:
    newy_labels = [0.0, 5.0, 10.0, 15.0, 20.0]
    new_ticks = np.linspace(2, trimmed_black.shape[0]-2, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
else :
    newy_labels = [0.0, 2.5, 5.0, 7.5, 10.0]
    new_ticks = np.linspace(2, trimmed_black.shape[0]-2, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
plt.colorbar().set_label('Voltage (mV)',rotation=270, labelpad=10)
plt.xlabel("Front face (mm)")
plt.ylabel("Lateral Face (mm)")
plt.title('Trimmed Black')

filename= "Trim_Black_" + f"{int(newy_labels[-1]/10)}x{int(newx_labels[-1]/10)}" + Diff_ver + ".svg"
plt.savefig(str(plots_dir /  filename), format='svg', bbox_inches='tight')
plt.show()








#%%
# Cosine function
ones_array = np.ones((154, 154))

# Constants
stepSize = 0.2
height = height_list[index]
maxRow, maxColumn = ones_array.shape
maxRow=maxRow 
maxColumn=maxColumn
NA = 0.39
n = 1

# Applying the cosine_correction function to each element
for row in range(ones_array.shape[0]):
    for column in range(ones_array.shape[1]):
        result = cosine_correction(row, column, stepSize, height, maxRow, maxColumn, NA, n)
        ones_array[row, column] = result['cosCorrection']  # Use only the cosCorrection

# Plotting the result
plt.imshow(ones_array, cmap='plasma', vmin=1.00, vmax=1.035)
plt.hlines(y=[27, 127], xmin=2, xmax=152, colors='limegreen', linestyles='dashed', linewidth=1.5, label='2x3 SS Insert')
plt.hlines(y=[52, 102], xmin=2, xmax=152, colors='yellow', linestyles='dashed', linewidth=1.5, label='1x3 SS Insert')

#plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), shadow=True, ncol=2)
plt.colorbar()

new_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]

#adjust the x and y ticks to add the numbers of new_labels
new_ticks = np.linspace(2, 152, len(new_labels))
plt.xticks(new_ticks,new_labels, rotation = 0)

#adjust the y ticks o add the numbers of new_labels
new_ticks = np.linspace(2, 152, len(new_labels))
plt.yticks(new_ticks,new_labels)

plt.xlabel("Front face (mm)")
plt.ylabel("Lateral Face (mm)")

plt.title('Cosine Correction Visualization')

filename= "CosineCorrection" + Diff_ver +".svg"
plt.savefig(str(plots_dir /  filename), format='svg', bbox_inches='tight')

plt.show()






#%%
# Apply cosine correction

# Calculate direct and indirect
direct_light = trimmed_black
indirect_light = trimmed_mirror - trimmed_black

# Trim direct array using cosine correction
trimemed_direct, trimmed_Cos=trim_arrays(direct_light, ones_array)

# Corrected direct light
DirxCos=(trimemed_direct * trimmed_Cos)

# Trim indirect using corrected direct
DirxCos, trimed_indirect_light=trim_arrays(DirxCos, indirect_light)

# Main correction: 
# corrected = (direct_light * cosine_correction) + indirect_light
corrected= DirxCos + trimed_indirect_light 









#%%
# Plotting the result
plt.imshow(corrected, cmap='plasma', vmin=0.0, vmax=0.4) #vmax=0.3 for difussor
#X ticks
newx_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
newx_ticks = np.linspace(2, corrected.shape[1]-2, len(newx_labels))
plt.xticks(newx_ticks,newx_labels, rotation = 0)

#Y ticks
if corrected.shape[0] >= 150:
    newy_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
    new_ticks = np.linspace(2, corrected.shape[0]-2, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
elif corrected.shape[0] < 150 and corrected.shape[0]>=100:
    newy_labels = [0.0, 5.0, 10.0, 15.0, 20.0]
    new_ticks = np.linspace(2, corrected.shape[0]-2, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)
else :
    newy_labels = [0.0, 2.5, 5.0, 7.5, 10.0]
    new_ticks = np.linspace(2, corrected.shape[0]-2, len(newy_labels))
    plt.yticks(new_ticks,newy_labels)

plt.xlabel("Front face (mm)")
plt.ylabel("Lateral Face (mm)")
plt.colorbar().set_label('Voltage (mV)',rotation=270, labelpad=10)
plt.title('Corrected')

filename="Corrected_" + f"{int(newy_labels[-1]/10)}x{int(newx_labels[-1]/10)}" + Diff_ver +".svg"
plt.savefig(str(plots_dir /  filename), format='svg', bbox_inches='tight')
plt.show()












#%%
#This is only for the figure using the insert of 3x3 with Difussor and with realtive Voltage 
#corrected=corrected[1:, 1:] #erase first row and column 

max_corrected_value = corrected.max()
relative_corrected= corrected / max_corrected_value
#obtain the max an min relative values to use in the heatmap
min_rel_value=relative_corrected.min()
max_rel_value=relative_corrected.max()



#plt.imshow(relative_corrected, cmap='plasma', vmin=min_rel_value, vmax=max_rel_value)
# Plotting
img = plt.imshow(relative_corrected, cmap='plasma', vmin=min_rel_value, vmax=max_rel_value)

# Adding colorbar
cbar = plt.colorbar(img)
cbar.ax.tick_params(labelsize=12)  # Adjust the fontsize as needed
cbar.set_label('Relative Voltage',rotation=270, labelpad=10, fontsize=12)

#Adjust x ans y ticks
new_labels = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
#X
newx_ticks = np.linspace(2, relative_corrected.shape[1]-2, len(new_labels))
plt.xticks(newx_ticks,new_labels, rotation = 0, fontsize=12)
#Y
newy_ticks = np.linspace(2, corrected.shape[0]-2, len(new_labels))
plt.yticks(newy_ticks,new_labels, fontsize=12)

plt.xlabel("Front face (mm)", fontsize=12)
plt.ylabel("Lateral Face (mm)", fontsize=12)
plt.title('Corrected Relative')

filename= "CorrectionRelative_" + f"{int(newy_labels[-1]/10)}x{int(newx_labels[-1]/10)}"+ Diff_ver + ".svg"
plt.savefig(str(plots_dir /  filename), format='svg', bbox_inches='tight')
plt.show()











#%%Obtain homogeneity cv and area for cv with another values for corrected array
homogeneity_cv = calculate_homogeneity_cv(corrected[2:-2, 2:-2], coverage=0.9)
area_for_cv = find_area_for_cv(corrected[2:-2, 2:-2], target_cv=10, initial_coverage=0.01, step_size=0.01, max_coverage=1)
mean, median, std, minimum, maximum= correction_summary(corrected[2:-2, 2:-2])









#%%Save the df with all data in a csv

# Be aware that the append() function was depreciated since pandas 2.0.0 release in 2023
df = df.append({'Sample': f"{int(newy_labels[-1]/10)}x{int(newx_labels[-1]/10)}" + Diff_ver, 'Homogeneity': homogeneity_cv, 'CV_area': area_for_cv, 'Mean': mean, 'Median':median, 'SD':std, 'Min':minimum,'Max':maximum}, ignore_index=True)

# Save DataFrame to a CSV file
filename = 'Corrections_sumary.csv'
df.to_csv(str(plots_dir /  filename), index=False)  # Set index=False to exclude the DataFrame index from the CSV file



