#######################################

import ctypes_opencv as ocv
import sys
import operator
from itertools import *
from math import *

#######################################

def dotproduct(vec1, vec2):
  return sum(imap(operator.mul, vec1, vec2))

def anglebetween(x1,y1,x2,y2):
  x = x2-x1
  y = y2-y1
  angle = atan2(y,x)
  angle = angle * -1
  return (angle+pi) % (2*pi)

def anglediff(a1,a2):
  r = abs(a1-a2)
  t = abs((2*pi)-r)
  return min(r,t)

def selectangle(ang1,ang2,ang3):
  diff = anglediff(ang1,ang3)
  oiff = anglediff(ang2,ang3)
  if diff<oiff:
    return ang1
  else:
    return flipped

#######################################

# For testing direct from the command line
#log = True
#show = False 
if len(sys.argv)==5:
  video = sys.argv[1]
  mask = sys.argv[2]
  background = sys.argv[3]
  tracks = sys.argv[4]
  log = False
  show = True

#######################################

filename = video 
maskname = mask 
backname = background 
trackname = tracks 

#######################################

# Actual number of targets FIXED FOR THE MOMENT
ntargets = 2
# set some thresholds for the ellipses
min_width = 10 
min_height = 10 
min_area = min_width*min_height
# max thresholds
max_width = 30 
max_height = 45 
max_area = max_width * max_height
# values for dynamics 
smallmove = 0.2 # fraction of length
anglefrom = pi*0.33 # angles of turning
angleto = pi*0.66

#######################################

# open the video
cap = ocv.cvCreateFileCapture(filename)
# extract the number of frames
max_frames = ocv.cvGetCaptureProperty(cap,ocv.CV_CAP_PROP_FRAME_COUNT)
# interrogate the first frame to get the size
t = 1
frame = ocv.cvQueryFrame(cap)
frame_size = ocv.cvGetSize(frame)

# create some temporary frames
gray =		ocv.cvCreateImage(frame_size,8,1) 
#backgray =		ocv.cvCreateImage(frame_size,8,1) 
grayfloat =		ocv.cvCreateImage(frame_size,ocv.IPL_DEPTH_32F,1)
background =		ocv.cvCreateImage(frame_size,ocv.IPL_DEPTH_32F,1)
ones =		ocv.cvCreateImage(frame_size,ocv.IPL_DEPTH_32F,1)
thresh = 	ocv.cvCreateImage(frame_size,8,1) 
output =	ocv.cvCloneImage(frame) 
masked = 	ocv.cvCreateImage(frame_size,8,1) 
  
#mask = ocv.cvLoadImage(maskname,0)
backgray = ocv.cvLoadImage(backname,0) 
#print back
#print frame_size.width, frame_size.height 
#ocv.cvConvertImage(back,backgray)
ocv.cvConvert(backgray,background)

if show:
  ocv.cvNamedWindow ('Track', ocv.CV_WINDOW_AUTOSIZE)
  ocv.cvMoveWindow ('Track', 100, 100)
  font = ocv.cvInitFont(None,ocv.CV_FONT_HERSHEY_PLAIN, 1.0, 1.0, 0, 1, 8)

#######################################

tracks = open(trackname,'w')

targets = []
for i in range(ntargets):
  targets.append([0.0,0.0,0.0,0.0,0.0,0.0,0.0])

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
  # update outputs to the new frame
  ocv.cvCopy(frame,output)

  # Mask - if you do this here you get edge artifacts
  #ocv.cvCopy(frame,m_frame,mask)

  # Convert frame to grayscale
  ocv.cvConvertImage(frame,gray)

  # Convert grayscale to float
  ocv.cvConvert(gray,grayfloat)

  # Smooth - CRITICAL to remove codec artifacts
  ocv.cvSmooth(grayfloat,grayfloat,ocv.CV_GAUSSIAN,3,3,0.5)
  #ocv.cvSmooth(gray,gray,ocv.CV_MEDIAN)

  # Subtract current frame from background model
  ocv.cvAbsDiff(grayfloat, background, grayfloat);

  # Normalise image
  ocv.cvSet(ones,ocv.cvScalar(1.0,0,0,0),0) 
  minval = ocv.cvMinMaxLoc(grayfloat,True,False)
  maxval = ocv.cvMinMaxLoc(grayfloat,False,True)
  #print min,max
  ocv.cvSubS(grayfloat,ocv.cvScalar(minval,0,0,0),grayfloat,0)
  if ((maxval-minval)!=0): #Stop divide by zero
    ocv.cvDiv(grayfloat,ones,grayfloat,1.0/(maxval-minval))
  else:
    cvZero(grayfloat)
  ocv.cvScale(grayfloat,grayfloat,255.0) # Scale back to 0-255

  # Convert back to int 
  ocv.cvConvert(grayfloat,gray)
  #ocv.cvMerge(gray,gray,gray,0,output) # Show on output

  #Find the "lightest" things in the image 
  #TODO: find "dip" inbetween
  #ocv.cvEqualizeHist(gray,gray)
  thresholdat = 70 #30

  # Threshold frame
  #ocv.cvAdaptiveThreshold(
  #  gray,
  #  thresh,
  #  255, 
  #  ocv.CV_ADAPTIVE_THRESH_GAUSSIAN_C,
  #  ocv.CV_THRESH_BINARY_INV,
  #  5,
  #  2)
  ocv.cvThreshold(
    gray,
    thresh,
    thresholdat,#128, #bang in the middle - 'cause we normalised 
    255, 
    ocv.CV_THRESH_BINARY)

  # Mask 
  ocv.cvCopy(thresh,masked) #without mask for testing!
  #ocv.cvCopy(thresh,masked,mask)
  #ocv.cvMerge(masked,masked,masked,0,output)# if show on output
  
  # Apply some morphological operators - to remove any small dots 
  kernel = ocv.cvCreateStructuringElementEx(3,3,1,1,ocv.CV_SHAPE_ELLIPSE)
  ocv.cvErode(masked,masked,kernel,1)
  ocv.cvDilate(masked,masked,kernel,1)

  # Get contours
  stor = ocv.cvCreateMemStorage(0)
  nb_contours, cont = ocv.cvFindContours(
    masked,
    stor,
    method=ocv.CV_CHAIN_APPROX_NONE)

  ocv.cvDrawContours(output,cont,ocv.CV_RGB(255,0,0),ocv.CV_RGB(0,255,0),1, 1, 8 )

  flies = [] 
  #Fit ellipses
  if cont is not None:
    # The components of each contour
    for c in cont.hrange():
      # Number of points in component 
      count = c.total
      # Need at least 6 points for ellipse fitting
      if (count < 6):
        continue
      # Allocate matrices to convert points for fitting
      PointArray = ocv.cvCreateMat(1,count,ocv.CV_32SC2)
      PointArray2D32f = ocv.cvCreateMat(1,count,ocv.CV_32FC2)
      # Convert sequenece into floating point matrix
      ocv.cvCvtSeqToArray(c,PointArray.data.ptr, ocv.cvSlice(0, ocv.CV_WHOLE_SEQ_END_INDEX))
      ocv.cvConvert(PointArray,PointArray2D32f)
      # Actually perform ellipse fitting
      box = ocv.cvFitEllipse2(PointArray2D32f)
      # box sizes
      size = (box.size.height,box.size.width)
      area = size[0] * size[1]
      width = min(size)
      height = max(size)
      # tests - the results are stored in a list. 
      # they should return TRUE if the box fails the test
      tests = []
      tests.append(box.size.height*box.size.width < max_area)
      tests.append(box.size.height*box.size.width > min_area)
      tests.append(width > min_width)
      tests.append(height > min_height)
      tests.append(width < max_width)
      tests.append(height < max_height)
      # return false if any of the tests fail
      if(sum(tests)==6):
        # Convert ellipse data from float to integer representation.
        center = ocv.CvPoint()
        nsize = ocv.CvSize()
        center.x = ocv.cvRound(box.center.x)
        center.y = ocv.cvRound(box.center.y)
        nsize.width = ocv.cvRound(width*0.5)
        nsize.height = ocv.cvRound(height*0.5)
        box.angle = -box.angle # correct
        # Draw ellipse on overlay
        if show:
          ocv.cvEllipse(output, center, nsize, box.angle, 0, 360, ocv.CV_RGB(0,255,0), 1, ocv.CV_AA, 0)
        angle = (box.angle/360.0)*2*pi
        angle = angle + (pi/2) # correct from x-axis
        angle = (angle) % (2*pi)
        flies.append([center.x,center.y,angle,height])

  # Right, sort out which flies are which based on distance
  # If just zero or one estimate - keep the same as last time

  if len(flies)==2:
    targ = 0
    found = [False] * len(flies)
    for [xpos,ypos,ango,axislen,lastx,lasty,lasta] in targets:
      bestdist = 99999.9
      bestind = 0
      at = 0
      for [x,y,orient,alen] in flies:
        dist = sqrt((x-xpos)**2 + (y-ypos)**2)  
        if dist<bestdist:
          if found[at]==False:
            bestdist = dist
            bestind = at
        at += 1
      # Update from last time
      targets[targ][4] = targets[targ][0] 
      targets[targ][5] = targets[targ][1]
      targets[targ][6] = targets[targ][2]
      # Set to new best target
      targets[targ][0] = flies[bestind][0] #xpos
      targets[targ][1] = flies[bestind][1] #ypos
      targets[targ][2] = flies[bestind][2] #ango
      targets[targ][3] = flies[bestind][3] #axis
      found[bestind]=True
      targ += 1
 
    # Now sort out their orientation

    orient = 0.0
    targ = 0
    for [xpos,ypos,ango,axislen,lastx,lasty,lasta] in targets:
      flipped = (ango-pi) % (2*pi)
      movedby = sqrt((xpos-lastx)**2 + (ypos-lasty)**2)
      fractionmoved = movedby/axislen
      # Check for small movement
      if fractionmoved<smallmove:
        orient = selectangle(ango,flipped,lasta) 
      # Otherwise, moving quite a bit 
      else:
        movemento = anglebetween(lastx,lasty,xpos,ypos)
        prevmove = anglediff(lasta,movemento)
        # moving along axis (i.e. previous and last in line)
        if prevmove>anglefrom and prevmove<angleto:
          orient = selectangle(ango,flipped,lasta) 
        # moving roughly in direction pointing
        else:
          orient = selectangle(ango,flipped,movemento) 
      if orient>0:
        orient -= 2*pi
      targets[targ][2] = orient
      targ += 1

  #### Output

  # framenumber, male_x, male_y, male_angle, female_x, female_y, female_angle

  at = 0
  pastx = 0
  pasty = 0
  if t==1:
    print >> tracks, "framenumber, male_x, male_y, male_angle, female_x, female_y, female_angle"
  print >> tracks, str(t),
  for [xpos,ypos,ang,axislen,lastx,lasty,lasta] in targets:
    print >> tracks, "," + str(xpos) + "," + str(ypos) + "," + str(-ang),
    if show:
      axis = axislen*0.5
      if at==0:
        colour = ocv.CV_RGB(255,0,255)
        pastx = xpos
        pasty = ypos
      if at==1:
        colour = ocv.CV_RGB(255,255,0)
        ocv.cvLine(output, ocv.cvPoint(xpos,ypos), ocv.cvPoint(pastx,pasty),ocv.CV_RGB(0,0,0),1)
        dbetween = sqrt((xpos-pastx)**2 + (ypos-pasty)**2) 
        ocv.cvPutText(output, str(round(dbetween,2)), ocv.cvPoint(int((xpos+pastx)/2),int((ypos+pasty)/2)), font, ocv.CV_RGB(0,0,0));
      #if ang<-2*pi or ang>0.0:
      #  print "Watch out! Angle outside of bounds: " + str(ang)
      x = -axis # NOTE: negative x axis for drawing!   
      y = 0  
      tox = x*cos(ang)+y*sin(ang)
      toy = x*-sin(ang)+y*cos(ang)
      tox += xpos # translate
      toy += ypos
      ocv.cvLine(output, ocv.cvPoint(xpos,ypos), ocv.cvPoint(tox,toy), colour,2)
      ocv.cvCircle(output, ocv.cvPoint(tox,toy),4,colour,ocv.CV_FILLED)
      ocv.cvPutText(output, str(round(-ang,2)), ocv.cvPoint(xpos+10,ypos), font, ocv.CV_RGB(0,0,0));
    at += 1
  print >> tracks

  # Increment frame
  t += 1
 
  if show:
    ocv.cvShowImage ('Track', output)
    # Break if ESC
    if ocv.cvWaitKey (5) & 255 == 27:
      break

