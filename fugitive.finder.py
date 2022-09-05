# croo
#22jun22
# python+opencv -- facial recognition with tello drone
# 1.0 goal: proof of concept project, identify faces with the video stream from the tello drone
# 2.0 goal: have it follow (person) but at an angle to allow to view oncoming faces (ie you are
# --> walking down the street and the drone is following you while also detecting faces of the
# --> people walking past you going the opposite direction
# ## this is a proof of concept as a future/cyberpunk tool used by police/govt/amateur sleuths
# ### to detect the faces of famous people/politicians & govt officials/wanted criminals/ or 
# #### any other people that maybe of interest, perhaps a wanted felon or missing person has a reward
#

import cv2, sys, os, time, socket, threading, subprocess, pyttsx3
import numpy as np
from djitellopy import Tello

#converter is part of the text to speech library pyttsx3
# Initialize the converter
converter = pyttsx3.init()
#speed
converter.setProperty('rate', 150)
# Set volume 0-1
converter.setProperty('volume', 0.7)



# recv is used to read responses from drone should be 'ok' responses if everything is working correctly
def recv():
    while True: 
        try:
            data = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print ('\nExit . . .\n')
            break

### this block verifies that the wifi is connected to the tello drone wifi ssid
wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
data = wifi.decode('utf-8')
wifi_ssid = "TELLO-F12FFA" #change this to tello wifi ssid
#wifi_ssid = "LetsGoBrandon" #place holder for local wifi for compiling 
if wifi_ssid in data: #will match partial strings (ie if input is HomeWif it will match HomeWifi)
    print("connected to {}".format(wifi_ssid))
else:
    sys.exit("ERROR: not connected to correct wifi")

###drone needs a command every <15 secs or it will auto land

tello = Tello()


# PC/Mac/Mobile UDP Server: 0.0.0.0 UDP PORT: 11111
video_IP     = "0.0.0.0"
video_Port   = 11111

#udp socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#drone default ip & commands port
tello_address = ("192.168.10.1", 8889)


# Bind to address and ip
#server_sock.bind(('', video_Port)) # may need to change to 0.0.0.0 & 11111
#sock.connect(tello_address)
recvThread = threading.Thread(target=recv)
recvThread.start()

sock.sendto(bytes("command", "utf-8"), (tello_address)) #using the djitellopy 'tello.connect()' is the same command
time.sleep(2)
sock.sendto(bytes("takeoff", "utf-8"), (tello_address))
converter.say("Drone is airborne")#audio: voice text-to-speech
converter.runAndWait()
sock.sendto(bytes("streamon", "utf-8"), (tello_address)) # or tello.streamon()
time.sleep(3)
streamon_frame = tello.get_frame_read()

#####################
#####################
"""
 def _receive_thread(self):
        # Listen to responses from the Tello.
        # Runs as a thread, sets self.response to whatever the Tello last returned.
        # 
        while True:
            try:
                self.response, ip = self.socket.recvfrom(3000)
                #print(self.response)
            except socket.error as exc:
                print ("Caught exception socket.error : %s" % exc)

    def _receive_video_thread(self):
        #
        # Listens for video streaming (raw h264) from the Tello.
        # Runs as a thread, sets self.frame to the most recent frame Tello captured.
        # 
        packet_data = ""
        while True:
            try:
                res_string, ip = self.socket_video.recvfrom(2048)
                packet_data += res_string
                # end of frame
                if len(res_string) != 1460:
                    for frame in self._h264_decode(packet_data):
                        self.frame = frame
                    packet_data = ""

            except socket.error as exc:
                print ("Caught exception socket.error : %s" % exc)
    
    def _h264_decode(self, packet_data):
        # 
        # decode raw h264 format data from Tello
        
        # :param packet_data: raw h264 data array
       
        # :return: a list of decoded frame
        # 
        res_frame_list = []
        frames = self.decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                # print 'frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls)

                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, ls / 3, 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list
#####################
#####################
"""
       
# Create a VideoCapture object and read from input file
cap = cv2.VideoCapture(streamon_frame.frame)
   
# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video  file")
######delete this next line
#sys.exit()
# Read until video is completed
while(cap.isOpened()):
      
  # Capture frame-by-frame
  ret, vframe = cap.read()
  if ret == True:
   
    # Display the resulting frame
    cv2.imshow('Frame', vframe)
   
    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break
   
  # Break the loop
  else: 
    break
   
# When everything done, release 
# the video capture object
cap.release()
   
# Closes all the frames
cv2.destroyAllWindows()


#test