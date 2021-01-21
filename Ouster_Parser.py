########################################################################
# Import Libs
########################################################################

# Todo: Downsampling code yet to be implemented
import sys, os, pcapy, glob, numpy as np
import pandas as pd
import time
import argparse



parser = argparse.ArgumentParser(description="Parse command line arguments.", 
                           formatter_class=argparse.RawTextHelpFormatter)


parser.add_argument("--file", type=str, help="File to be parsed")
parser.add_argument("--mode", type=str, help="Mode of the Lidar, 1024 and 2048")
parser.add_argument("--save_path", type=str, help="Path to save the files")
# parser.add_argument("--downsample_rate", type=int, default=1, help="Pass downsample rate for downsampling the data")
parser.add_argument("--save_as", type=str, default="npy", help="file format to store the data")


opt = parser.parse_args()

data = np.zeros((80000,5), dtype=np.float32)
iterator = 0
counter = 0

########################################################################
# Define pcap reader class
########################################################################
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



########################################################################
# vertical angles of each LiDAR channel
########################################################################
if opt.mode == "2048":
	print("2048 mode")
	

	azimuth_limit = 90068
	beam_altitude_angles = [
			44.450000000000003,
			41.509999999999998,
			38.579999999999998,
			35.659999999999997,
			32.75,
			29.859999999999999,
			26.989999999999998,
			24.109999999999999,
			21.25,
			18.420000000000002,
			15.58,
			12.77,
			9.9600000000000009,
			7.1500000000000004,
			4.3499999999999996,
			1.55,
			-1.25,
			-4.0499999999999998,
			-6.8700000000000001,
			-9.6899999999999995,
			-12.51,
			-15.34,
			-18.190000000000001,
			-21.050000000000001,
			-23.920000000000002,
			-26.809999999999999,
			-29.699999999999999,
			-32.619999999999997,
			-35.560000000000002,
			-38.520000000000003,
			-41.509999999999998,
			-44.530000000000001
	]

	beam_azimuth_angles = [
			-3.2000000000000002,
			-3.1099999999999999,
			-3.0299999999999998,
			-2.96,
			-2.8999999999999999,
			-2.8500000000000001,
			-2.8100000000000001,
			-2.7799999999999998,
			-2.7599999999999998,
			-2.73,
			-2.73,
			-2.71,
			-2.7200000000000002,
			-2.7400000000000002,
			-2.75,
			-2.77,
			-2.79,
			-2.8300000000000001,
			-2.8599999999999999,
			-2.8999999999999999,
			-2.9500000000000002,
			-2.9900000000000002,
			-3.0499999999999998,
			-3.1200000000000001,
			-3.2000000000000002,
			-3.2799999999999998,
			-3.3799999999999999,
			-3.48,
			-3.6099999999999999,
			-3.77,
			-3.9199999999999999,
			-4.1299999999999999
	]

	print(beam_altitude_angles[0])
	print(beam_azimuth_angles[0])

	time.sleep(3)

else:
	print("1024 mode")

	azimuth_limit = 90024
	beam_altitude_angles = [
			44.93,
			41.939999999999998,
			38.979999999999997,
			36.030000000000001,
			33.079999999999998,
			30.170000000000002,
			27.260000000000002,
			24.359999999999999,
			21.489999999999998,
			18.629999999999999,
			15.779999999999999,
			12.949999999999999,
			10.130000000000001,
			7.3099999999999996,
			4.4900000000000002,
			1.6799999999999999,
			-1.1200000000000001,
			-3.9399999999999999,
			-6.7599999999999998,
			-9.5800000000000001,
			-12.41,
			-15.25,
			-18.100000000000001,
			-20.960000000000001,
			-23.84,
			-26.73,
			-29.629999999999999,
			-32.549999999999997,
			-35.509999999999998,
			-38.469999999999999,
			-41.479999999999997,
			-44.520000000000003
		]

	beam_azimuth_angles = [
			-3.1200000000000001,
			-3.04,
			-2.9700000000000002,
			-2.9100000000000001,
			-2.8599999999999999,
			-2.8199999999999998,
			-2.79,
			-2.7599999999999998,
			-2.7400000000000002,
			-2.7400000000000002,
			-2.73,
			-2.73,
			-2.73,
			-2.73,
			-2.75,
			-2.77,
			-2.79,
			-2.8300000000000001,
			-2.8700000000000001,
			-2.8999999999999999,
			-2.9500000000000002,
			-3.0099999999999998,
			-3.0699999999999998,
			-3.1400000000000001,
			-3.2200000000000002,
			-3.3100000000000001,
			-3.4100000000000001,
			-3.52,
			-3.6499999999999999,
			-3.79,
			-3.9500000000000002,
			-4.1399999999999997
		]

	print(beam_altitude_angles[0])
	print(beam_azimuth_angles[0])
	
	time.sleep(3)

n = 27.670000000000002
########################################################################
# Construct path to pcap file
########################################################################

print(opt.file)
pcap_file = opt.file

####################################r####################################
# Read data payload from packets
########################################################################

# create pcap object 
pc = pcapIter(pcap_file)

##################### extract data from each packet ####################
for idx, packet in enumerate(pc):
	print("length", len(packet))

	# Obtain LiDAR sensor data, which has packet lengths of 1248
	if len(packet) == 6506:
		
		# print("inside if")

		# Each block contains all sensor info from one complete 
		# firing cycle of the 32 laser beam stack. 
		# There are 16 blocks per packet.
		for block_index in range(0, 16):

			# obtain azimuth angle of the LiDAR beam stack 
			# during a given firing cycle

			# 42 bytes for the header which is not mentioned in the manual, 12 bytes of Timestamp+MeasureID+FrameID
			# 44 ticks for 1024 mode and 88 for 2048 mode.
			firecycle_start = 42+12+block_index*404
			azimuth = packet[firecycle_start:firecycle_start +4]
			
			
			# convert binary azimuth angle value to float 
			# Note: azimuths are in deg not rads
			azimuth_value = int.from_bytes(azimuth, byteorder='little', signed=False)
			print("Encoder", azimuth_value)

			# print("Azimuth angle", azimuth_value)
			theta_encoder = 2*np.pi*(1-(azimuth_value/90112))

			# Obtain distance and intensity data from each laser 
			# channel in the block. There are 32 channels per block, 
			# one for each laser.
			# print("Azimuth angle \n", azimuth_value)
			for channel_index in range(32):
				
	# 			# obtain distance in mm
				channel_start = firecycle_start + 4 + 12*channel_index
				channel_distance = packet[channel_start:channel_start+4]
				distance = int.from_bytes(channel_distance, byteorder='little', signed=False)
				# print("Distance", distance)

	# 			# obtain intensity of returing laser pulse
				channel_intensity = packet[channel_start+4:channel_start+6]
				intensity = int.from_bytes(channel_intensity, byteorder='little', signed=False)

				

				theta_azimuth = -2*np.pi*beam_azimuth_angles[channel_index]/360
				phi = 2*np.pi*beam_altitude_angles[channel_index]/360

				X = (distance-n)*np.cos(theta_encoder+theta_azimuth)*np.cos(phi)+n*np.cos(theta_encoder)
				Y = (distance-n)*np.sin(theta_encoder+theta_azimuth)*np.cos(phi)+n*np.sin(theta_encoder)
				Z = (distance-n)*np.sin(phi)

				data[iterator,0]=X
				data[iterator,1]=Y
				data[iterator,2]=Z
				data[iterator,3]=distance
				data[iterator,4]=intensity

				iterator+=1

				# For 2048, there is this anamoly spherical points generated, not sure why! To discard those, below logic 
				# if(distance>1000000):
				# 	x = 0
				# 	y = 0
				# 	z = 0
				# 	print("Distance", distance)

				# print("X", x)
				# print("Y", y)
				# print("Z", z)
	# 			# obtain vertical angle from channel index
	# 			vertical_angle = V_angles[channel_index]

	# 			# print("Vertical angle \n", vertical_angle)
	# 			# print("channel intensity \n", intensity)
	# 			# print("distance \n", distance)

				# data = data.append({"X":x, "Y":y, "Z":z,"Laser_id":channel_index, "Distance":distance, "Intensity":intensity}, ignore_index=True)

		# 		break
		# break



			# Checking for the complete rotation. azimuth_limit for 1024 mode = 90024 and for 2048 mode = 90068
			if (azimuth_value>=azimuth_limit):

				# Removing extra rows 
				data = data[~np.all(data==0,axis=1)]

				# For 2048, there is this anamoly spherical points generated, not sure why! To discard those, below logic
				data = data[~np.any(data>=1000000, axis=1)]


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
				iterator = 0

				# Incrementing counter
				counter += 1

				# data.to_csv("./Data/data" + str(counter) + ".csv")
				# data.drop(data.index, inplace=True)
				# # print("Azimuth value",azimuth_value)
				# print("writing csv:",counter)
				time.sleep(3)
				# counter +=1


				# df = pd.DataFrame([azimuth_value,distance,])
				# pd.save_csv