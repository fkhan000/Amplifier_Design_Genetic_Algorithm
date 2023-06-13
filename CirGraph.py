import CirComp
import Metrics
import os

##########################################################Circuit Class##########################################################

####Class Attributes####

##ID: (string) a unique identifier for the circuit used to locate its corresponding folder in the NetLists directory
##components: (list) a list of Component objects holding all of the components used in the circuit
##nodes: (set) a set of strings holding the names of all of the nodes in the circuit

####Class Methods####

##expNetList: This function exports the circuit into a netlist file (Circuit{ID}.cir) in
#the corresponding folder whose relative path is NetLists/Circuit{ID}.

##fitness: This function assigns a fitness score (FoM) to the circuit by calling on the Metrics submodule
#to produce the relevant measurements for the circuit. Takes in a fitFunc to calculate the fitness score
#More will be discussed once the function is complete

##mutate: This function mutates the circuit on a component level by adding gaussian noise to each of the component
#parameters with some probability. The factor argument is the variance of the gaussian noise and pm is the probability
#of mutating each component. The function will also mutate the circuit on a topological level by adding/removing components and
#nodes as well as changing the nodes that a component connects to but currently this functionality is unavailable.

##addComp: This function adds a component to the circuit. It takes in a Component object and adds it to the list
#and if there are any new nodes, it will add those to nodes

##delComp: This function deletes a component from the circuit given by the component's index in the component list.
#It's currently a work in progress. I'm pretty sure
#that what I have currently works for deleting two terminal devices but I'm not sure if it does for transistors.
#The idea is that a component is removed from a circuit either by just taking it out and creating an open circuit
#or by shorting it and replacing it with wire. If component connects to a node that isn't used by any other component
#then that component created a node. If we just took out the component, we would likely have a floating node. So instead
#we replace the component with a wire so that the nodes that the component joins become one node. If a component doesn't
#create a node then we don't have to worry about this problem and we can just make an open circuit. In fact, making a short
#here would be problematic since then if we had another component connecting these two nodes, it would also be effectively
#removed from the circuit since no current would flow through it. With three terminal devices it gets tricky since
#you can't really short a device like that. Maybe you can think of it as 2 two terminal devices?

##__str__(): This function overrides the default __str__() function


class Circuit:

    def __init__(self, ID, components, nodes):

        self.ID = ID
        self.components = components
        self.nodes = nodes


    def expNetList(self):
        file = "Circuit" + str(self.ID)

        if not os.path.exists("NetLists/" + file):
            os.makedirs("NetLists/" + file)
        f = open("NetLists/" + file + "/" + file + ".cir", "w")
        f.write("*Circuit # " + str(self.ID) + "\n\n")

        #add in model definitions
        f.write("*MODEL DEFINITIONS\n")
        f.write(".model 2N2222 NPN(IS = 1E-14 VAF = 100 BF = 200 IKF = 0.3 XTB = 1.5 BR = 3 CJC = 8E-12 CJE = 25E-12 TR=100E-9 TF=400E-12 ITF=1 VTF = 2 XTF=3 RB=10 RC=.3 RE=.2 Vceo=30 lcrating=800m mfg=N)\n")
        f.write(".model 1N4148 D(Is=2.52n Rs=.568 N=1.752 Cjo=4p M=.4 tt=20n lave=200m Vpk=75 mfg=OnSemi type=silicon\n")

        f.write(".model 2N3906 PNP(Is=1E-14 VAF=100 BF=200 IKF=0.4 XTB=1.5 BR=4 CJC=4.5E-12 CJE=10E-12 RB=20 RC=0.1 RE=0.1 TR=250E-9 TF=350E-12 ITF=1 VTF=2 XTF=3 Vceo=40 lcrating=200m mfg=NXP\n")

        
        f.write("*NETLIST DESCRIPTION\n")

        #iterate through list of components and call on netList function to get their corresponding line
        for component in self.components:
            f.write(component.netList() + "\n")
            
        f.close()

    def fitness(self, fitFunc):
        pass

    
    def mutuate(self, factor, pm):

        #to mutate component values, we just iterate through the list of components
        #and call on their mutate function
        for component in components:
            component.mutate(factor, pm)
    
    
    def addComp(self, comp):

        self.components.append(comp)
        for node in comp.nodes:
            self.nodes.add(node)
    
    def delComp(self, index):

        #to see if we need to short or open the component we make a dictionary keeping the count
        #of each of the nodes in the component
        numNodes = dict(zip(self.components[index].nodes, [0 for node in self.components[index].nodes]))
        

        #for each component
        for component in self.components:
            #iterate through the nodes it connects to
            for node in component.nodes:
                #if this component and the component to be deleted share a node
                #we add it to the corresponding count
                if node in numNodes:
                    numNodes[node] += 1
        #if the component to be deleted defined a node, we need to replace the component with a short
                    
        if sum([1 if val > 2 else 0 for val in numNodes.values()]) < 2*len(numNodes):

            #for each component in the circuit
            for idx in range(len(self.components)):
                #if this component is the same as the one to be deleted, we move on to the next component
                if idx == index:
                    continue

                #for each node
                for ndx in range(len(self.components[idx].nodes)):

                    #if the component and the component to be deleted share the node connected to the anode of the component to be deleted
                    if self.component[idx].nodes[ndx] == self.components[index].nodes[1]:
                        #set that node to be the node connected to the cathode of that anode. This is really similar
                        #to deleting a node in a linked list. We're removing all references to the node that's being deleted
                        self.component[idx].nodes[ndx] = self.components[index].nodes[0]

                #after we do that we remove that node from node list
                self.nodes.remove(self.components[index].nodes[1])

        #and if the component doesn't define a node, we can just remove it from the list. We also have to do this
        #if it does define a node.
        self.components.pop(index)

    
    def __str__(self):
        output = ""
        for component in self.components:
            output += component.__str__() + "\n"
        return output
