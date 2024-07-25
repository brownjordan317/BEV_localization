# Steps to go From Panoramic Image to BEV and Attempt Satellite Image Matching
This document is meant to work in tandom with the full README. For full explanations on how to run programs, please refer to the README. This Document is meant to serve as a low level outline for the workflow of going from panoramic image to potential satellite image match.

---

## 1: Obtain a Panoramic Image
Panoramic images can be generated using either a continuous panoramic imaging tool or by stitching together a series of images. Stitching of images can be done using main_programs/stitch_image.py

If you want to use a street view location to create your panorama their are a couple more steps to follow
- Select your street view location
- Set the tilt of the camera to 90 degrees and the direction to north
- screen record the street view imager spinning a ful 360 degrees
- run output video through GUIs/frame_extractor.py
- run extracted frames through main_programs/stitch_image.py

## 2: Generate BEV
Once a panoramic image is generated, you may then warp it into a BEV. Done simply by submitting the image into main_programs/pano_to_planar_frames.py and make sure the pitch is set to 180 for a BEV to result. The FOV setting will affect zoom of the top down image, should always be less than 180 degrees. 

## 3: Create Train Descriptors Data Base
To create a data base of descriptors you will need to submit the train image youd like to be tested against into main_programs/create_descriptor_data_base.py. You will also have two important numbers to submit:
- The segmentation size which is an int depicting the side length of each square segment to be extracted
- The step size which is an int depicting the number of pixels between each segment

## 4: Finding Best matches Query and Segments of Train
To find the best matches there are several necessary things to submit to the program main_programs/descriptor matcher:
- The path to your train image
- The path to your query image
- the path to your train image segmentation database
With those primary things submitted, you should be able to return an image depicting the best match between the query and train image