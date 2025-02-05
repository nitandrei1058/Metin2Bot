import cv2 as cv
import numpy as np
import os
from time import time, sleep
from windowcapture import WindowCapture
from vision import Vision
from pynput.mouse import Button, Controller
import random
mouse = Controller()

import ctypes

import pytest
from PySide6.QtWidgets import QApplication

with pytest.MonkeyPatch.context() as mp:
    mp.setattr(ctypes.windll.user32, "SetProcessDPIAware", lambda: None)
    import pyautogui  # noqa # pylint:disable=unused-import
    import pydirectinput

QApplication()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# initialize the WindowCapture class
wincap = WindowCapture('METIN2')
# initialize the Vision class
vision_pumnal = Vision('pumnal.jpg')
vision_loc_gol = Vision('loc_gol.jpg')

def get_pumnal_position(screenshot):
    # look for pumnal
    height, width, _ = screenshot.shape  # Get the image dimensions

    # Define cropping boundaries
    crop_x_start = (width // 2) + (width // 4)  # Start of the rightmost quarter
    crop_x_end = width  # End of the rightmost quarter
    crop_y_start = 0
    crop_y_end = height // 2  # Top half

    # Crop the image
    cropped_img = screenshot[crop_y_start:crop_y_end, crop_x_start:crop_x_end]

    # Find objects in the cropped image
    rectangles_translated = vision_pumnal.find(cropped_img, 0.6, offset_x=crop_x_start, offset_y=crop_y_start)
    return rectangles_translated

def get_loc_gol_positions(screenshot):
     # look for loc gol
    height, width, _ = screenshot.shape  # Get the image dimensions

    # Define cropping boundaries for the left-bottom corner
    crop_x_start = width // 2
    crop_x_end = width # Right half
    crop_y_start = height // 2  # Bottom half
    crop_y_end = height

    # Crop the image
    cropped_img = screenshot[crop_y_start:crop_y_end, crop_x_start:crop_x_end]        

    # look for loc gol
    rectangles_loc_gol = vision_loc_gol.find(cropped_img, 0.6, offset_x=crop_x_start, offset_y=crop_y_start)
    return rectangles_loc_gol

def main():

    # get an updated image of the game
    screenshot = wincap.get_screenshot()
    # get the pumnal position
    rectangle_pumnal = get_pumnal_position(screenshot)

    loop_time = time()
    while(True):

        # get an updated image of the game
        screenshot = wincap.get_screenshot()
        rectangles_loc_gol = get_loc_gol_positions(screenshot)

        # Draw the translated rectangles on the original screenshot
        output_image = vision_pumnal.draw_rectangles(screenshot, rectangle_pumnal)
        output_image = vision_loc_gol.draw_rectangles(output_image, rectangles_loc_gol)

        cv.imshow('Matches', output_image)

        if len(rectangles_loc_gol) == 0:
            break

        rand = random.randint(150, 2000)
        if len(rectangle_pumnal) > 0:
            targets = vision_pumnal.get_click_points(rectangle_pumnal)
            target = wincap.get_screen_position(targets[0])
            pyautogui.moveTo(target[0], target[1])
            pyautogui.rightClick()
            sleep(rand / 1000)

        # debug the loop rate
        print('FPS {}'.format(1 / (time() - loop_time)))
        loop_time = time()

        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break

    print('Done.')

if __name__ == '__main__':
    main()