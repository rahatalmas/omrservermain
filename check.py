#leatest work...

import cv2 as cv
import numpy as np

def process(block,Q):
    grey_block_image = cv.cvtColor(block, cv.COLOR_BGR2GRAY)
    img_blur_block = cv.GaussianBlur(grey_block_image, (5, 5), 1)
    img_canny_block = cv.Canny(img_blur_block, 10, 50)
    # Find contours
    contours_block, hierarchy_block = cv.findContours(img_canny_block, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    # Filter circular contours
    circleCons_block = circularContour(contours_block)
    #circleCons_block.reverse()
    #print(len(circleCons_block))


    # List to store the centroid coordinates and corresponding contours
    centroid_contour_pairs = []
    # Iterate over each contour to find centroids and store them with contours
    for contour in circleCons_block:
        # Calculate moments of the contour
        M = cv.moments(contour)
        
        # Calculate the centroid coordinates (cx, cy)
        if M["m00"] != 0:  # Check to avoid division by zero
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroid_contour_pairs.append(((cx, cy), contour))  # Store centroid with contour
        else:
            centroid_contour_pairs.append(((float('inf'), float('inf')), contour))  # Handle case where contour has no area

    # Sort the list based on the x-coordinate (cx) of the centroids (ascending order)
    centroid_contour_pairs.sort(key=lambda x: x[0][0])  # Sort by the first element of the tuple (cx)
    
    # Extract the sorted contours into a new list
    sorted_contours = [contour for (centroid, contour) in centroid_contour_pairs]
    # # Print the sorted contours and their centroids
    # print("Sorted contours based on centroid x (cx):")
    # for idx, contour in enumerate(sorted_contours):
    #     M = cv.moments(contour)
    #     cx = int(M["m10"] / M["m00"])
    #     cy = int(M["m01"] / M["m00"])
    #     print(f"Contour {idx + 1}: Centroid = ({cx}, {cy})")
    print(len(sorted_contours))
    if len(sorted_contours) > 4:
        sorted_contours = sorted_contours[1:]
    #answer checking ...
    if len(sorted_contours)==4:
        _, thresholded_block_img = cv.threshold(grey_block_image, 150, 255, cv.THRESH_BINARY_INV)
        filled_circles, filled_circle_indices = processColumnContours(sorted_contours, thresholded_block_img)
        print(f"Question: {Q} Answer: {filled_circle_indices} : filled circles {filled_circles}")
        if len(filled_circle_indices) > 0:
            return {Q: filled_circle_indices[0]}
        else:
            return{Q: -1}
        #for idx in filled_circle_indices:
            #cv.drawContours(block, [sorted_contours[idx - 1]], -1, (0, 255, 0), thickness=2)  # Green for filled circles
            #cv.imshow("block img", block)
            #cv.waitKey(0)


def processSerial(block,Q):
    grey_block_image = cv.cvtColor(block, cv.COLOR_BGR2GRAY)
    img_blur_block = cv.GaussianBlur(grey_block_image, (5, 5), 1)
    img_canny_block = cv.Canny(img_blur_block, 10, 50)
    # Find contours
    contours_block, hierarchy_block = cv.findContours(img_canny_block, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    # Filter circular contours
    circleCons_block = circularContour(contours_block)
    #circleCons_block.reverse()
    #print(len(circleCons_block))


    # List to store the centroid coordinates and corresponding contours
    centroid_contour_pairs = []
    # Iterate over each contour to find centroids and store them with contours
    for contour in circleCons_block:
        # Calculate moments of the contour
        M = cv.moments(contour)
        
        # Calculate the centroid coordinates (cx, cy)
        if M["m00"] != 0:  # Check to avoid division by zero
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroid_contour_pairs.append(((cx, cy), contour))  # Store centroid with contour
        else:
            centroid_contour_pairs.append(((float('inf'), float('inf')), contour))  # Handle case where contour has no area

    # Sort the list based on the x-coordinate (cx) of the centroids (ascending order)
    centroid_contour_pairs.sort(key=lambda x: x[0][0])  # Sort by the first element of the tuple (cx)
    
    # Extract the sorted contours into a new list
    sorted_contours = [contour for (centroid, contour) in centroid_contour_pairs]
    
    # # Print the sorted contours and their centroids
    # print("Sorted contours based on centroid x (cx):")
    # for idx, contour in enumerate(sorted_contours):
    #     M = cv.moments(contour)
    #     cx = int(M["m10"] / M["m00"])
    #     cy = int(M["m01"] / M["m00"])
    #     print(f"Contour {idx + 1}: Centroid = ({cx}, {cy})")
    # print(len(sorted_contours))
    
    if len(sorted_contours) > 4:
        sorted_contours = sorted_contours[1:]

    #answer checking ...
    if len(sorted_contours)==4:
        _, thresholded_block_img = cv.threshold(grey_block_image, 150, 255, cv.THRESH_BINARY_INV)
        filled_circles, filled_circle_indices = processColumnContours(sorted_contours, thresholded_block_img)
        print(f"row: {Q} filled row: {filled_circle_indices} : filled circles {filled_circles}")
        if len(filled_circle_indices) > 0:
            return filled_circle_indices
        else:
            return []
        #for idx in filled_circle_indices:
            #cv.drawContours(block, [sorted_contours[idx - 1]], -1, (0, 255, 0), thickness=2)  # Green for filled circles
            #cv.imshow("block img", block)
            #cv.waitKey(0)


# Function to filter circular contours
def circularContour(contours, min_area=150):
    circular_contours = []
    for contour in contours:
        # Calculate contour area
        area = cv.contourArea(contour)
        if area < min_area:
            continue  # Skip contours with area less than min_area
        
        perimeter = cv.arcLength(contour, True)
        if perimeter == 0:
            continue  # Avoid division by zero

        # Calculate circularity: 4π * (Area / Perimeter²)
        circularity = 4 * np.pi * (area / (perimeter * perimeter))

        # A perfect circle has circularity close to 1
        if 0.7 < circularity < 1.2:  # Adjust thresholds as needed
            circular_contours.append(contour)
    return circular_contours

# Function to check 

# Function to count white and black pixels inside the contour
def countBlackWhite(img, contour):
    # Create a mask for the current contour
    mask = np.zeros_like(img)
    cv.drawContours(mask, [contour], -1, 255, thickness=cv.FILLED)

    # Apply the mask to the image and count white pixels
    masked_img = cv.bitwise_and(img, img, mask=mask)
    white_pixels = np.sum(masked_img == 255)
    total_pixels = cv.contourArea(contour)  # Total pixels inside the contour (approximated by area)

    # Calculate percentage of white pixels
    white_percentage = (white_pixels / total_pixels) * 100
    return white_percentage

# Function to get a thresholded image for a column
def getThresholdedImage(img, column_idx, num_columns=5):
    # Get the width of the image to define the columns
    img_width = img.shape[1]
    column_width = img_width // num_columns
    
    # Define column region for thresholding
    start_x = column_idx * column_width
    end_x = (column_idx + 1) * column_width

    # Create the thresholded image for the specified column
    column_img = img[:, start_x:end_x]
    _, thresholded = cv.threshold(column_img, 150, 255, cv.THRESH_BINARY_INV)  # Invert the binary image
    
    return thresholded

# Function to process contours within each column
def processColumnContours(column_contours, thresholded_image):
    # Sort the contours within the column by (x + y)
    #sorted_column_contours = sortContoursByXYSum(column_contours)

    # Variables to store filled circle count and indices
    filled_circles = 0
    filled_circle_indices = []

    # Check each contour in the sorted column
    for i, contour in enumerate(column_contours):
        white_percentage = countBlackWhite(thresholded_image, contour)
        if white_percentage >= 90:
            filled_circles += 1  # Count filled circles
            filled_circle_indices.append(i + 1)  # Store 1-based index of the filled circle
            # Draw the filled contour outline on the image
            #cv.drawContours(img, [contour], -1, (0, 255, 0), thickness=2)  # Green outline

    return filled_circles, filled_circle_indices

def check(imagepath):
    answers = []
    # Load the image
    img = cv.imread(imagepath)

    # Check if the image is loaded properly
    if img is None:
        print("Error: Image not loaded.")
    else:
        # Get dimensions of the image
        height, width, _ = img.shape

        # Crop 90 pixels from each side
        top, bottom, left, right = 90, 90, 90, 90
        cropped_img = img[top:height-bottom, left:width-right]

        # Get the dimensions of the cropped image
        cropped_height, cropped_width, _ = cropped_img.shape

        # Calculate the split point for 1:2 ratio
        split_point = cropped_height // 3  # 1/3 for the top part
        top_part = cropped_img[:split_point, :]  # Top part
        bottom_part = cropped_img[split_point:, :]  # Bottom part

        # Remove 10 pixels from the top of the bottom part
        bottom_part = bottom_part[10:, :]
        

        # Get the width of the image to define the columns
        img_height, img_width = bottom_part.shape[:2]
        # Split the image into 5 equal columns
        num_columns = 4
        column_width = img_width // num_columns
        num_rows = 20
        row_height = img_height // num_rows  # Height of each row
        # Process each column one by one
        questionnumber = 0
        for column_idx in range(num_columns):
            print(f"\nProcessing Column {column_idx + 1}...\n")

            # Define the column's horizontal section
            start_x = column_idx * column_width
            end_x = (column_idx + 1) * column_width
            column_img = bottom_part[:, start_x:end_x]  # Extract column part of the image
            #Split column into 20 rows
            for row_idx in range(num_rows):
                questionnumber = questionnumber+1
                # Define the vertical section of the current row
                start_y = row_idx * row_height
                end_y = (row_idx + 1) * row_height if row_idx < num_rows - 1 else img_height  # Ensure the last row reaches the bottom
                row_img = column_img[start_y:end_y, :]
                #approach(50)(working...)(sorting based on x axis)
                answers.append(process(row_img,questionnumber))

        
            # processing for serial number
    height, width = top_part.shape[:2]  # Get the height and width of the image
    # Calculate the midpoint of the width
    midpoint = width // 2
    # Split the image into left and right parts
    left_half = top_part[:, :midpoint]  # Left 50% (columns from 0 to midpoint)
    right_half = top_part[:, midpoint:]  # Right 50% (columns from midpoint to the end)

    # Assuming left_half is a NumPy array representing the left portion of the image
    left_height, left_width = left_half.shape[:2]  # Get the height and width of the left half
    # Calculate the midpoint of the width for splitting left_half horizontally
    split_point = left_width // 2
    # Split the left_half into left and right parts
    left_of_left = left_half[:, :split_point]  # Left 50% of the left_half
    right_of_left = left_half[:, split_point:]  # Right 50% of the left_half
    # Crop the right_of_left image
    cropped_right_of_left = right_of_left[20:-34, :]
    # cv.imshow("img",cropped_right_of_left)
    # cv.waitKey(0)
    # Get the height and width of the cropped image
    cropped_height, cropped_width = cropped_right_of_left.shape[:2]
   
    # Calculate the height of each row
    row_height = cropped_height // 10
    j=1
    # Split the image into 10 rows and process each row
    
    serialNumber = [0] * 5
    #print(serialNumber)
    for i in range(10):
        # Extract each row
        row = cropped_right_of_left[i * row_height: (i + 1) * row_height, :]
        # Pass the row to the process function
        # cv.imshow("croope",row)
        # cv.waitKey(0)
        data = processSerial(row,j)
        # print(data)
        for k in range(len(data)):
            print("data k", data[k])
            serialNumber[data[k-1]] = j-1
        j = j+1
    
    serialNumber = serialNumber[1:]
    serialNumberInt = int("".join(map(str, serialNumber)))
    print("serial number",serialNumberInt) 
    

    omrData = {serialNumberInt:answers}

    return omrData












    # Save or display both parts
    # cv.imwrite("top_part.png", top_part)
    # cv.imwrite("bottom_part_adjusted.png", bottom_part)

    # # Display both parts
    # cv.imshow("Top Part", top_part)
    # cv.imshow("Bottom Part (10px Top Removed)", bottom_part)
    # cv.waitKey(0)
    # cv.destroyAllWindows()









