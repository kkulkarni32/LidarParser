########################################################################
# This parser parses X,Y,Z,Distance,Intensity from Pcap file produced by Velodyne 32 Lidar and stores in either npy or csv.
# Other variables like Laser_ID, Vertical angle, Azimuth angle can also be included.
########################################################################
import sys, os, pcapy, glob, numpy as np
import pandas as pd
import time
import argparse

# Initializing empty matrix and other necessary variables 
data = np.zeros((80000,5), dtype=np.float32)
iterator = 0
azimuth_value_prev = 0
counter = 0

# Vertical angles for each laser
V_angles = np.array([-30.67,-9.33,-29.33,-8.00,-28.00,-6.67,-26.67,
	-5.33,-25.33,-4.00,-24.00,-2.67,-22.67,-1.33,-21.33,0.00,-20.00,
	1.33,-18.67,2.67,-17.33,4.00,-16.00,5.33,-14.67,6.67,-13.33,8.00,
	-12.00,9.33,-10.67,10.67])



parser = argparse.ArgumentParser()

parser.add_argument("--file", type=str, help="Pcap file path")
parser.add_argument("--save_path", type=str, help="Path to save the files")
parser.add_argument("--downsample_rate", type=int, default=1, help="Pass downsample rate for downsampling the data")
parser.add_argument("--save_as", type=str, default="npy", help="file format to store the data")

opt = parser.parse_args()


######### Define pcap reader class #########

class pcapIter:
	def __init__(self, fname):
		self.pcapy_obj = pcapy.open_offline(fname)

	def __iter__(self):
		return self

	def __next__(self):
		header, packet = self.pcapy_obj.next()
		if len(packet) == 0:
			raise StopIteration
		else:
			return packet



# create pcap object 
pc = pcapIter(opt.file)


##################### extract data from each packet ####################
for idx, packet in enumerate(pc):

	# Obtain LiDAR sensor data, which has packet lengths of 1248
	if len(packet) == 1248:		

		# Each block contains all sensor info from one complete 
		# firing cycle of the 32 laser beam stack. 
		# There are 12 blocks per packet.

		# downsample_rate determines downsampling of the lidar points. e.g - downsample_rate = 2 skips every alternating azimuth angle.
		# This way we have lesser points radially but retains vertical points 
		for block_index in range(0,12,opt.downsample_rate):

			# obtain azimuth angle of the LiDAR beam stack 
			# during a given firing cycle
			firecycle_start = 42+block_index*100
			azimuth = packet[firecycle_start + 2:firecycle_start +4]
			
			# convert binary azimuth angle value to float 
			# Note: azimuths are in deg not rads
			azimuth_value = int.from_bytes(azimuth, byteorder='little', signed=False)/100
			azimuth_value = azimuth_value*np.pi/180


			# Obtain distance and intensity data from each laser 
			# channel in the block. There are 32 channels per block, 
			# one for each laser.
			
			for channel_index in range(32):
				
				# obtain distance in mm
				channel_start = firecycle_start + 4 + 3*channel_index
				channel_distance = packet[channel_start:channel_start+2]
				distance = int.from_bytes(channel_distance, byteorder='little', signed=False)/1000

				# obtain intensity of returing laser pulse
				channel_intensity = packet[channel_start+2:channel_start+3]
				intensity = int.from_bytes(channel_intensity, byteorder='little', signed=False)

				# obtain vertical angle from channel index and convert it into radians
				vertical_angle = V_angles[channel_index]*np.pi/180


				X = distance*np.cos(vertical_angle)*np.sin(azimuth_value)
				Y = distance*np.cos(vertical_angle)*np.cos(azimuth_value)
				Z = distance*np.sin(vertical_angle)

				data[iterator,0]=X
				data[iterator,1]=Y
				data[iterator,2]=Z
				data[iterator,3]=distance
				data[iterator,4]=intensity

				iterator+=1


			# Checking if one rotaion is completed, azimuth_value reaches its maximum and then starts decreasing  
			if (azimuth_value<=azimuth_value_prev):


				# Removing extra rows
				data = data[~np.all(data==0,axis=1)]

				if (opt.save_as == "csv"):

					#Converting data to df before saving as csv. For some reason np.save_txt saves csv with larger file size
					df = pd.DataFrame(data, columns=["X", "Y", "Z", "Distance", "Intensity"])
					df.to_csv(opt.save_path + "data" + str(counter) + ".csv")
					print("writing csv:",counter)

				else:
					np.save(opt.save_path + "data" + str(counter), data)
					print("writing npy:",counter)


				# Reinitializing variables 
				data = np.zeros((80000,5))
				azimuth_value_prev = 0
				iterator = 0

				# Incrementing counter
				counter += 1


			else:
				# If the new azimuth value is larger than previous, assign it to the azimuth_value_prev variable 
				azimuth_value_prev=azimuth_value
			