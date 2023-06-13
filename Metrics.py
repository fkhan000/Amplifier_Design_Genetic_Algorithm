import os

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
    fcir.write("\nC1 N2 N5 10u\n")
    fcir.write("Vin N5 0 sin(0, 10m, " + str(freq) + " )\n")
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
    fcir.writelines(lines[:-6])

    fcir.close()

def tranalysis(freq, ID, node):
    pass

def ac(ID, node):
    pass

def acAnalysis(ID, node):
    pass

def monteCarlo(ID, node):
    pass

def robustness(ID, node):
    pass
