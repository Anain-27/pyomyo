# Simplistic data recording
import time
import multiprocessing
import numpy as np
import pandas as pd

from pyomyo import Myo, emg_mode

#Para guardar los csv más facilmente
def save(myo_data,myo_cols,filepath):
	# Add columns and save to df
	myo_df = pd.DataFrame(myo_data, columns=myo_cols)
	myo_df.to_csv(filepath, index=False)
	print("CSV Saved at: ", filepath)
def data_worker(mode, seconds, filepathemg,filepathimu):
	collect = True
	tiempo = 0
	# ------------ Myo Setup ---------------
	m = Myo(mode=mode)
	m.connect()

	#Ana: Guardo los datos EMG
	myo_emg_data = []
	# Ana: Guardo los datos IMU
	myo_imu_data = []
	# Ana: Guardo los demás datos
	myo_data = []

	def save_emg(emg, movement):
		datos= (tiempo,)+ emg
		#print("EMG:", datos)

		myo_emg_data.append(datos)

	m.add_emg_handler(save_emg)

	#Ana: Pintamos y guardamos
	def print_save_battery(bat):
		print("Battery level:", bat)
		#Ana: Además de pintarlo lo guardamos
		myo_data.append(bat)
	def print_save_arm(arm,xdir):
		print("Arm data:", arm, xdir)
		#Ana: Además de pintarlo lo guardamos
		myo_data.append(arm)
		myo_data.append(xdir)
	def print_save_imu(quat, acc, gyro):
		#print("IMU data:", quat, acc, gyro)
		imu=quat+acc+gyro

		#Ana: Además de pintarlo lo guardamos
		myo_imu_data.append(imu)
	def print_save_pose(pose):
		print("Pose data:", pose)
		#Ana: Además de pintarlo lo guardamos
		myo_data.append(pose)

	# Ana: Añadimos los demás handlers para captar todos los datos
	m.add_battery_handler(print_save_battery)
	m.add_arm_handler(print_save_arm)
	m.add_imu_handler(print_save_imu)
	m.add_pose_handler(print_save_pose)

	 # Its go time
	m.set_leds([0, 128, 0], [0, 128, 0])
	# Vibrate to know we connected okay
	m.vibrate(1)

	print("Data Worker started to collect")
	# Start collecing data.
	start_time = time.time()

	while collect:
		if (time.time() - start_time < seconds):
			m.run()
			#Ana: Añadimos el tiempo
			tiempo= time.time() - start_time
		else:
			collect = False
			collection_time = time.time() - start_time
			print("Finished collecting.")
			print(f"Collection time: {collection_time}")
			print(len(myo_emg_data), "frames collected")

			# Add columns and save to df
			myo_emg_cols = ["Tiempo","Channel_1", "Channel_2", "Channel_3", "Channel_4", "Channel_5", "Channel_6", "Channel_7", "Channel_8"]

			myo_imu_cols = ["quat1","quat2","quat3","quat4", "acc1","acc2","acc3", "gyro1","gyro2","gyro3"]
			save( myo_emg_data,myo_emg_cols,filepathemg)
			save( myo_imu_data, myo_imu_cols, filepathimu)


# -------- Main Program Loop -----------
if __name__ == '__main__':
	#Ana: tiempo de captación
	seconds=5
	name = "datos/prueba"
	file_emg_name = str(name)+"_emg.csv"
	file_imu_name = str(name) + "_imu.csv"
	#Cambiado para ver el raw
	mode = emg_mode.FILTERED
	p = multiprocessing.Process(target=data_worker, args=(mode, seconds, file_emg_name,file_imu_name))
	p.start()
