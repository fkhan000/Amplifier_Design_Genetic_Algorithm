import numpy as np

#model parts for components that program will use 
NPN_MODEL = "Q2N2222"
PNP_MODEL = "Q2N3906"
DIODE_MODEL = "D1N4148"


##########################################################Component Class##########################################################

#The component class represents a single element in the circuit.

####Class Attributes####

##kind: string indicating component type. Currently, program supports following types:
#Vsource, Resistor, Capacitor, Inductor, Diode, BJT, NMOS, and PMOS

##name: string indicating reference name of component

##nodes: list of names (strings) of nodes that component is connected to. For two
#terminal components, 1st element is node cathode of component is connected to.
#2nd element is node anode of component is connected to

##params: list of floats indicating the parameters of the component. Diodes contain
#no parameters in this program as well as BJTs. NMOS and PMOS transistors contain two
#parameters width (element 0) and length (element 1). Capacitors, Resistors, Inductors,
#and Voltage sources each contain one parameter which is the value of that component.


####Class Methods####


##mutate: This function performs gaussian mutation on each of the component's parameters.
#Takes in two arguments, factor and pm. Factor is the standard deviation of the
#gaussian distribution that the function samples from. pm is the probability that a single
#parameter would be mutated.


##pOut2Term: This is a helper function for the __str__ function and is used to print out
#two terminal components. It takes in spWd which is a list of strings that are substituted
#in the print out statement. For diodes, this list is empty but for the other two terminal devices
#the first element is the quantity of the component's value and the second argument is the unit of that value

##pOut3Term: This is a helper function for the __str__ function and is used to print out
#three terminal components. It takes in spWd which is a list of strings that are substituted
#in the print out statement. For BJTs this list is ["Collector", "Base", "Emitter"] and for
#NMOS and PMOS, this list is ["Drain", "Gate", "Source" "Width", "Length"]

##__str__(): This function overrides the default __str__ function

##netList(): This function returns the corresponding netlist line (a string) for this component.


class Component:

    def __init__(self, kind, name, nodes, params):
        
        self.kind = kind
        self.name = name
        self.nodes = nodes
        self.params = params

    def mutate(self, factor, pm):

        #sample len(self.params) values from a uniform distribution from 0 to 1
        uniSamp = np.random.uniform(0, 1, len(self.params))

        #for each parameter
        for index in range(len(self.params)):

            #with probability pm we will mutate this parameter
            if uniSamp[index] < pm:

                #sample from a normal distribution centered around the parameter value
                #and with standard deviation equal to the mutation factor
                normSamp = np.random.normal(self.params[index], factor)

                #After doing a bit of research I found that for gaussian mutation you
                #generally want the length of the interval that the parameter can take on
                #after mutating to be 10 times the mutation factor
                lb = self.params[index] - 5*factor
                ub = self.params[index] + 5*factor

                #we set the parameter to be the sample we took from the gaussian distribution
                #but clip to the lb and ub of the interval of values so that we don't get some
                #incredibly large (or small) value that could break our circuit. 

                #I also added 0 as an argument to the max function so that the mutation would never
                #make the parameter negative which would likely make the ltSpice simulation throw an
                #error
                self.params[index] = min(max(normSamp, lb, 0), ub)
            
    
    def pOut2Term(self, spWd):
        
        output = self.kind + " " + self.name + ":\n"

        output += "\tCathode: " + self.nodes[0] + "\n"

        output += "\tAnode: " + self.nodes[1]

        #if spWd has length > 0 then the component isn't a diode
        if len(spWd) > 0:
            output += "\n\t" + spWd[0] + ": " + str(self.params[0]) + spWd[1]

        return output

    def pOut3Term(self, spWd):
        output = self.kind + " " + self.name + ":\n"
        output += "\t" + spWd[0] + " : " + self.nodes[0] + "\n"
        output += "\t" + spWd[1] + " : " + self.nodes[1] + "\n"
        output += "\t" + spWd[2] + " : " + self.nodes[2]

        #if spWd has length > 3 then the component is a MOSFET
        if len(spWd) > 3:
            output += "\n\t" + spWd[3] + " : " + str(self.params[0]) + " m" + "\n"
            output += "\t" + spWd[4] + " : " + str(self.params[1]) + " m"

        return output

    
    def __str__(self):

        match self.kind:

            case "Vsource":
                return self.pOut2Term(["Voltage", "V"])
            case "Resistor":
                return self.pOut2Term(["Resistance", "\u03A9"])

            case "Capacitor":
                return self.pOut2Term(["Capacitance", "F"])

            case "Inductor":
                
                return self.pOut2Term(["Inductance", "H"])

            case "Diode":
                return self.pOut2Term([])
                
            case "PNP":
                return self.pOut3Term(["Collector", "Base", "Emitter"])

            case "NPN":
                return self.pOut3Term(["Collector", "Base", "Emitter"])
            
            case "PMOS":
                return self.pOut3Term(["Drain", "Gate", "Source", "W", "L"])

            case _:
                return self.pOut3Term(["Drain", "Gate", "Source", "W", "L"])

    
    def netList(self):

        output = self.name + " " + self.nodes[0] + " " + self.nodes[1]

        #for diodes, bjts, and mosfets we also have to specify the model that we're using
        if self.kind == "Diode":
            return output + DIODE_MODEL

        if self.kind == "Vsource":
            return output +  " DC " + str(self.params[0])

        if self.kind in ["Resistor", "Capacitor", "Inductor"]:
            return output +  " " + str(self.params[0])
        
        output += " " + self.nodes[2]

        if self.kind == "NPN":
            return  output + " " + NPN_MODEL
        if self.kind == "PNP":
            return  output + " " + PNP_MODEL

        #For the MOSFETs, they have an additonal pin called the substrate which for NMOS is connected to the emitter (or ground)
        #and for PMOS their substrate pin is tied to the collector node. 
        
        if self.kind == "NMOS":
            
            return output + " " +  self.nodes[2] + " NMOS W=" + str(self.params[0]) + " L=" + str(self.params[1])

        return output + " " + self.nodes[1] +" PMOS W=" + str(self.params[0]) + " L=" + str(self.params[1])
