#Bluetooth Reciever(runs on rpi startup)

# Checks for bluetooth connection

# Manages state of the software(RUNNING, IDLE) and sends a staus back (ERR_BUSY, SUCCESS, FAIL)
# Have a way to stop the current training
# Recieves data files packages as a tranining ID, GUI can recieve a send command to run a training ID

#On Recieve(Data files)
#Create a temp folder where the program is stored with the root files and store them there
#Modify global parameter file to update file path of training file to a local path
#Start program, run training and set status to running
#When program is done, if bluetooth is still connected, send produced data file


#On Recieve(Data file request)
# Allow bluetooth users to request files ONLY in DATA FILE OUTPUTS




#Bluetooth Sender
# For the most part keep same as OG GUI
# Have a connected Status
# Make it so that when you click the start button, it sends the files over to the reciever
    