import os
import numpy as np
import time

#Metrics submodule uses ltSpice simulator to simulate the circuit
#and calculate metrics relevant to FoM score

#This function performs a transient analysis on the circuit
#described in the file Netlists/Circuit{ID}/Circuit{ID}.cir
#where ID is the unique identifier for the circuit
#takes in the expected frequency of the output voltage signal
#as well as the name of the node to measure the waveform from

#creates a csv file called Circuit{ID}.csv in the same folder as the cir
#file which contains the output waveform sampled at 100 equally spaced points

def tran(freq, ID, node):
    
    prefix = "NetLists/Circuit" + str(ID) + "/" + "Circuit" + str(ID)

    #add commands for performing transient analysis
    fcir = open(prefix + ".cir", "a")

    fcir.write("Vin N5 0 sin(0, 1m, " + str(freq) + " )\n")
    fcir.write(".tran 0 " + str(1/freq) + " " + str(1/(100*freq)) + "\n")
    fcir.write(".param T = 0\n")
    fcir.write(".meas tran result find V(" + node + ") at = T\n")
    fcir.write(".step param T 0 " + str(1/freq) + " " + str(1/(100*freq)) + "\n")

    fcir.close()

    #simulate the circuit using ltSpice

    os.system("cd NetLists/Circuit" + str(ID) + ";/Applications/LTspice.app/Contents/MacOS/LTspice -b Circuit" + str(ID) + ".cir")

    #remove the raw files generated as we only need the error log file
    os.remove(prefix + ".raw")
    os.remove(prefix + ".op.raw")

    #open up the log file and create a csv file where we will store the results from the transient analysis
    flog = open(prefix +  ".log", "r", encoding = "utf-16-le")

    fcsv = open(prefix + "trans.csv", "w")

    
    logList = flog.readlines()

    #we iterate through the log file
    for index in range(len(logList)):

        #and find where the measurements made are located
        if ('Measurement: result\n' == logList[index]):
            idx = index + 2

            #then we write the value of the output at each time step
            #and write it into the csv file
            while(len(logList[idx].strip()) > 1):
                
                fcsv.write(",".join(logList[idx].split("\t")))
                idx += 2
            break
    
    fcsv.close()
    flog.close()
    

    #once we have transferred the relevant information to the csv file,
    #we can get rid of the log file
    
    os.remove(prefix + ".log")

    #after that we remove the command lines we added from the cir file
    fcir = open(prefix + ".cir", "r+")
    lines = fcir.readlines()
    fcir.seek(0)
    fcir.truncate()
    fcir.writelines(lines[:-5])

    fcir.close()

    #after that we calculate the amount of distortion in the output.
    #This measurement is more relevant for oscillators where you can get harmonic distortion
    #and not so much for amplifiers. To measure distortion, I took the sum of the distance
    #between the expected output, which should be sinusoidal and the actual output and then divided
    #it by the peak to peak swing of the output so that larger signals don't get penalized more

    #we load in the data collected from the log file on the output waveform
    
    arr = np.loadtxt(prefix + "trans.csv", delimiter = ",", dtype = float)

    #we then take off the last element because in ltSpice, transient simulations always end
    #with the value of the outing being 0 which could cause a huge jump in our measurement
    #and make the distortion seem higher than it actually is
    
    arr = arr[0:-2]

    #we subtract off the mean from the output waveform to make it 0 mean
    arr[:, 1] = arr[:, 1] - np.mean(arr[:, 1])

    #then we measure the peak to peak
    p2p = np.ptp(arr[:,1])

    phase = 0

    #we iterate through the array of output values
    #and look for when the output cross the x axis
    for index in range(len(arr[:, 2]) - 1):
        if arr[index][1]*arr[index + 1][1] < 0:

            #the phase would then just be the distance from this point
            #to the origin multiplied by the angular frequency
            
            phase = arr[index + 1][2]*freq*2*np.pi
            break
    

    #after we get the phase we can measure the distance between the expected and actual output
    
    distortion = np.sum(np.absolute(arr[:,1] - 0.5*p2p*np.sin(arr[:,2]*freq*2*np.pi + phase)))/p2p

    #and then remove the csv file since we got all of the relevant measurements from it
    os.remove(prefix + "trans.csv")
    return {"p2p": p2p, "distortion": distortion}


#This function performs ac analysis on the circuit and measures the 
#gain and phase at the operating frequency, the 3db cutoff frequencies
#the unity gain frequency, and the phase margin of the amplifier.
#It takes in the unique ID for the circuit, the node to measure the output from,
#the starting frequency, the number of frequencies to sample in the analysis, and
#the stopping frequency. Returns a dictionary with the measurements

def ac(ID, node, start, numStep, stop):

    #get the step size from the number of steps given
    step = (stop -  start)/numStep

    prefix = "NetLists/Circuit" + str(ID) + "/" + "Circuit" + str(ID)
    
    fcir = open(prefix + ".cir", "a")

    #go into the circuit file and add in certain commands for getting the measurements
    fcir.write("Vin N5 0 ac 1 sin\n")

    fcir.write(".ac dec " + str(start) + " " + str(step) + " " + str(stop)+"\n")
    fcir.write(".MEASURE AC op_point max mag(V(" + node + "))\n")
    fcir.write(".MEASURE AC 3dB_cutoff1 when mag(V(" + node + ")) = (op_point/sqrt(2)) cross=1\n")
    fcir.write(".MEASURE AC 3dB_cutoff2 when mag(V(" + node + ")) = (op_point/sqrt(2)) cross=2\n")
    fcir.write(".MEASURE AC unity_freq when mag(V(" + node + ")) = 1\n")
    fcir.write(".MEASURE AC unity_phase FIND V(N3) at unity_freq\n")
        
    fcir.close()

    #we run the AC analysis
    os.system("cd NetLists/Circuit" + str(ID) + ";/Applications/LTspice.app/Contents/MacOS/LTspice -b Circuit" + str(ID) + ".cir")

    #and remove the raw files
    os.remove(prefix + ".op.raw")
    os.remove(prefix + ".raw")

    #then we open up the cir file again and remove all of the commands
    #we added in
    fcir = open(prefix + ".cir", "r+")
    lines = fcir.readlines()
    fcir.seek(0)
    fcir.truncate()
    fcir.writelines(lines[:-7])

    fcir.close()

    #open up the log file and read in the lines
    flog = open(prefix +  ".log", "r", encoding = "utf-16-le")
    
    logList = flog.readlines()

    #initialize the measurements dictionary
    measurements = {"op_freq_gain": None, "op_freq_phase": None, "3db_cutoff1": None, "3db_cutoff2": None, "unity_freq": None, "phase_margin": 0}
    

    #iterate through each line in the log file and get the measurements
    
    for line in logList:

        #we check if a line has a key word
        if "op_point:" in line:
            #if it does then we check if ltSpice was successful in getting the measurement
            if "FAIL'ed" in line:
                #if not we skip the measurement
                continue

            #else we process that line and extract the measurement
            readIn = line.split("=")[1].split(",")

            measurements["op_freq_gain"] = float(readIn[0][1:-2])
            measurements["op_freq_phase"] = float(readIn[1][0:readIn[1].index(u'\N{DEGREE SIGN}')])

        elif "unity_phase" in line:
            if "FAIL'ed" in line or measurements["op_freq_phase"]  == None:
                continue
            
            readIn = line.split(",")[1]
            measurements["phase_margin"] = 180 - abs(float(readIn[0: readIn.index(u'\N{DEGREE SIGN}')]) - measurements["op_freq_phase"])
            continue
        
        else:
            for measurement in list(measurements.keys())[2:-1]:
                if measurement in line:
                    if "FAIL'ed" in line:
                        break
                    measurements[measurement] = float(line.split(" ")[-1])
                    break

    #and once we get all of the measurements we can remove the log file
    flog.close()
    os.remove(prefix + ".log")
    
    return measurements

#this function calculates the DC power for the circuit.Takes in the ID
#for the circuit

def DCpow(ID):

    
    #In ltSpice it doesn't look there's a command for calculating the total power of a circuit so
    #I instead found the current going through each of the voltage sources in the circuit to get the
    #power consumption.

    
    prefix = "NetLists/Circuit" + str(ID) + "/" + "Circuit" + str(ID)
    fcir = open(prefix + ".cir", "r+")

    lines = fcir.readlines()
    #we keep track of the names of the voltage sources in a dictionary
    voltages = dict()

    #we go through each of the lines in the cir file
    for index in range(len(lines[6:])):
        
        #if line starts with V then it's describing a voltage source
        if lines[index][0] == "V":
            li = lines[index].split(" ")

            #so we add a mapping from the voltage source name to its DC value
            #to the dictionary
            voltages[li[0].lower()] = float(li[4])

    #we add in the .op command to get the DC operating points
    fcir.write("\n.op")
    fcir.close()

    #run the simulation and remove the .raw file .op command only produces one of these files which
    #is pretty interesting

    os.system("cd NetLists/Circuit" + str(ID) + ";/Applications/LTspice.app/Contents/MacOS/LTspice -b Circuit" + str(ID) + ".cir")

    os.remove(prefix + ".raw")
    
    power = 0

    #go through each line of the log file
    flog = open(prefix + ".log", "r", encoding = "utf-16-le")

    lines = flog.readlines()
    for index in range(len(lines)):

        #if the line is describing the current going through one of the voltage sources
        if lines[index][0:3] == "I(V":

            readIn = lines[index].split()
            #we get the current going through that voltage source and multiply it by
            #the voltage of the voltage source to get the power consumed by the source
            power += float(voltages[readIn[0][2:-1].lower()])*float(readIn[1])

    flog.close()
    
    os.remove(prefix + ".log")

    #after that we remove the .op file
    fcir = open(prefix + ".cir", "r+")
    lines = fcir.readlines()
    fcir.seek(0)
    fcir.truncate()
    fcir.writelines(lines[:-2])

    fcir.close()

    #and return the total power consumed
    return {"DC Power": abs(power)}
