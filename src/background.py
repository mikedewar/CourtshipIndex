#######################################
# iBehave Workflow Script
#######################################

import ctypes_opencv as ocv
import sys

#######################################

# For testing direct from the command line
#log = True
if len(sys.argv)==3:
  video = sys.argv[1]
  print video
  background = sys.argv[2]
  print background
#  log = False

#######################################

# Otherwise, will use known variables
invideofile = video 
outimagefile = background 
show = False # Could be arg

NUM_FRAMES = 1000 # number of frames to integrate FROM END

#######################################

# Log file
#if log:
#  logfile = open("/opt/ibehave/log/scripts.log",'w')  # TODO: better logging!
#  print >> logfile, "-----------------> Model Background"
#  print >> logfile, invideofile
#  print >> logfile, background 

#######################################

# open the video
cap = ocv.cvCreateFileCapture(invideofile)
# extract the number of frames
max_frames = ocv.cvGetCaptureProperty(cap,ocv.CV_CAP_PROP_FRAME_COUNT)
# interrogate the first frame to get the size
frame = ocv.cvQueryFrame(cap)
frame_size = ocv.cvGetSize(frame)

working =       ocv.cvCreateImage(frame_size,ocv.IPL_DEPTH_32F,3)
accumulator =   ocv.cvCreateImage(frame_size,ocv.IPL_DEPTH_32F,3)
background =    ocv.cvCreateImage(frame_size,ocv.IPL_DEPTH_32F,3)
ones =		ocv.cvCreateImage(frame_size,ocv.IPL_DEPTH_32F,3)
target =	ocv.cvCloneImage(frame) 

# Set divisor image all to one
ocv.cvSet(ones,ocv.cvScalar(1.0,1.0,1.0,0))

if show:
  ocv.cvNamedWindow ('Track', ocv.CV_WINDOW_AUTOSIZE)
  ocv.cvMoveWindow ('Track', 100, 100)

t = 1
n = 1

while True:
  # check to see if we should stop
  if max_frames:
    if t > max_frames:
      break
  # capture the next frame
  frame = ocv.cvQueryFrame(cap)
  # if we've reached the end of the video
  if frame is None:
    break

  if t>=(max_frames-NUM_FRAMES):
 
    # Convert to floating point
    ocv.cvConvert(frame,working)
 
    # Smooth it to remove artifacts
    ocv.cvSmooth(working,working,ocv.CV_GAUSSIAN,3,3,0.5)

    # Add to accumulator
    ocv.cvAcc(working,accumulator)

    # Divide accumulator my number of frames for mean background
    ocv.cvDiv(accumulator,ones,background,1.0/n)

    # Convert background to target (for viewing/saving)
    ocv.cvConvert(background,target)
 
    # Increment accumulator divisor
    n += 1

  # Increment frame
  t += 1

  if show: 
    ocv.cvShowImage ('Track', target)
    # Break if ESC
    if ocv.cvWaitKey (5) & 255 == 27:
      break
  
ocv.cvSaveImage(outimagefile,target)

