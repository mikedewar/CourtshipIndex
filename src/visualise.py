#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
# For Mac
##!/usr/bin/python
# For Linux

from ctypes_opencv import *
import string

#################

if __name__ == "__main__":

  infile = sys.argv[1]
  outfile = sys.argv[2]
  trackfile = sys.argv[3]
  
  print infile, outfile, trackfile


  capture = cvCreateFileCapture (infile)
  frame = cvQueryFrame (capture)
  frame_num = 1

  #video = cvCreateVideoWriter(outfile,CV_FOURCC('P','I','M','1'),10,cvSize(frame.width,frame.height),frame.nChannels)
  video = cvCreateVideoWriter(outfile,CV_FOURCC_DEFAULT,10,cvSize(frame.width,frame.height),frame.nChannels)
  font = cvInitFont(None,CV_FONT_HERSHEY_PLAIN, 1.0, 1.0, 0, 1, 8)

  tracks = open(trackfile)

  for line in tracks.readlines():

    fields = string.split(line, ',')

    frame = cvQueryFrame (capture)

    if frame is None:
      break

    if int(fields[0])!=frame_num:
      break

    for target in range((len(fields)-1)/3):
      atx = int(fields[target*3+1])
      aty = int(fields[target*3+2])
      txt = str.strip(fields[target*3+3])
      cvPutText(frame, txt, cvPoint(atx+4,aty+12), font, CV_RGB(255,0,0));
      cvCircle(frame, cvPoint(atx,aty), 1, CV_RGB(0,0,0), 1,8,0);
      cvCircle(frame, cvPoint(atx,aty), 2, CV_RGB(0,0,0), 1,8,0);
      cvCircle(frame, cvPoint(atx,aty), 1, CV_RGB(255,255,255), 1,8,0)

    #print frame_num

    cvWriteFrame(video,frame)

    frame_num += 1
