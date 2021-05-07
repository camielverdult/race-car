import numpy as np
import cv2, math

class LineFinder:

    def __init__(self, capture):
        self.capture = capture

    def apply_hough_transform(self, image):
        
        #Convert to Grey Image
        grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Define a kernel size and apply Gaussian smoothing
        kernel_size = 5
        blur_gray = cv2.GaussianBlur(grey_image,(kernel_size, kernel_size), 0)
        
        # Define our parameters for Canny and apply
        low_threshold = 50
        high_threshold = 150
        edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
        
        # Next we'll create a masked edges image using cv2.fillPoly()
        mask = np.zeros_like(edges)

        ignore_mask_color = 255
        
        # Defining Region of Interest
        imshape = image.shape

        # Draw a square in centre of the image, this will be masked and ran through the hough transform
        vertices = np.array([[(imshape[1]/4, 0), (3*imshape[1]/4, 0), (3*imshape[1]/4, imshape[0]), (imshape[1]/4, imshape[0])]], dtype=np.int32)
        cv2.fillPoly(mask, vertices, ignore_mask_color)
        masked_edges = cv2.bitwise_and(edges, mask)
        
        # Hough transform parameters
        rho = 2 # distance resolution in pixels of the Hough grid
        theta = np.pi/180 # angular resolution in radians of the Hough grid
        threshold = 15     # minimum number of votes (intersections in Hough grid cell)
        min_line_length = 40 #minimum number of pixels making up a line
        max_line_gap = 30    # maximum gap in pixels between connectable line segments

        # Run Hough on edge detected image
        # Output "lines" is an array containing endpoints of detected line segments
        lines = cv2.HoughLinesP(masked_edges, rho, theta, threshold, np.array([]),
                                    min_line_length, max_line_gap)
                                    
        theta=0

        # Iterate over the output "lines" and draw lines on a blank image
        if lines is not None:
            for line in lines:
                for x1,y1,x2,y2 in line:
                    theta=theta+math.atan2((y2-y1),(x2-x1))

        return (theta, lines)

    def process_frame(self):
        _, frame = self.capture.read()
        theta, lines = self.apply_hough_transform(frame)

        return (theta, lines)

    
    # cap = cv2.VideoCapture(0)
    # while True:
    #     ret, frame = cap.read()

    #     hough = processImage(frame)
    #     cv2.imshow('frame', hough)
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    # cap.release()
    # cv2.destroyAllWindows()
