# LidarPraser
Consists of python script to parse pcap files produced by Velodyne 32 bit lidar. Data can be parsed as it is or it can be downsampled.

### Arguments to pass
* --file - Pcap file path to be parsed.
* --save_as - Output format of the parsed data (csv, npy), default=npy
* --save_path - Path for the output files
* --downsampling_rate - Specify the downsampling size of the data, default=1

## Requirements
* Linux System >= 16
* Numpy
* Pcapy
