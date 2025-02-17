import logging
from types import *
import time
import threading
#Python CarMaker Library
from pycarmaker import CarMaker, Quantity
#Kuksa Library
from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint

print("\r++++++++++++++++++++++++++++++++++++\r")
print("Welcome to Demon 3 in Windows Server\r")
print("+++++++++++++++++++++++++++++++++++++\r")

# Global variable


digitalBattery_Soc = 0


def thread_ControlCarMaker():

	global digitalBattery_Soc


	carMaker_IP = "localhost"
	carMaker_Port = 16660

	cm = CarMaker(carMaker_IP, carMaker_Port)

	cm.connect()

	battery_soc = Quantity("Batterysoc", Quantity.FLOAT)


	cm.subscribe(battery_soc)


	print(cm.send("::Cockpit::Close\r"))
	print(cm.send("::Cockpit::Popup\r"))

	print(cm.send("StartSim\r"))
	print(cm.send("WaitForStatus running\r"))

	while True:
		cm.read()

		digitalBattery_Soc = vehspd.data

		print("Vehicle Battery soc: " + str(digitalBattery_Soc))

		# Update the last user input
		time.sleep(1)



def thread_ConnectToDigitalAuto():

	global digitalBattery_Soc

	carMaker_IP = "localhost"
	carMaker_Port = 16660

	cm = CarMaker(carMaker_IP, carMaker_Port)
	cm.connect()
	kuksaDataBroker_IP = '20.79.188.178'
	kuksaDataBroker_Port = 55555

	with VSSClient(kuksaDataBroker_IP, kuksaDataBroker_Port) as client:
		while True:

			client.set_current_values({'Vehicle.Powertrain.TractionBattery.StateOfCharge.Current':Datapoint(float(digitalBattery_Soc)),})
			print("Digital Battery Soc: " + str(digitalBattery_Soc))
			#time.sleep(2)
			#cm.DVA_write(switch, switchdata)  # Set the switch to '1'
			time.sleep(1)

			#if str(digitalAuto_UserRequest) == '1':

			#else:
				#client.set_current_values({'Vehicle.Body.Horn.IsActive':Datapoint(False),})
				#print("Digital Control Signal :False ")
				#time.sleep(1)



if __name__ == '__main__':
    try:
        # Declare threads
        CarMakerThread = threading.Thread(target=thread_ControlCarMaker, args=())
        DigitalAutoThread = threading.Thread(target=thread_ConnectToDigitalAuto, args=())

        # Start threads
        CarMakerThread.start()
        DigitalAutoThread.start()

        # Wait threads to finish
        CarMakerThread.join()
        DigitalAutoThread.join()

        print("+++++++++++++++++++++++++++\r")
        print(" Demonstration is finished\r")
        print("+++++++++++++++++++++++++++\r\n")

    except:
        print("Something wrong, Can not start the process")
