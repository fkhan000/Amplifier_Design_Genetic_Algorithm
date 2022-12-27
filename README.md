# Amplifier_Design_Genetic_Algorithm
Designing an Amplifier Using a Genetic Algorithm


In this project, I want to see if I can use genetic algorithms to design a high speed common emitter amplifier. I plan on using ltSpice to simulate and evaluate the performance of the designs produced by the algorithm. The amplifier produced by the algorithm should have things like high midband gain, high bandwidth, high input impedance, low output impedance, and low power consumption. One of the challenging things about this is representing all of the features that make for a good amplifier in a single fitness score. Luckily there are already metrics like FOM scores that are used to describe the quality of an amplifier. Additionally, the design should be robust so that when the circuit is physically built, the small deviations from the values of the simulated circuit components don't cause the amplifier to behave completely differently. To add this into the fitness score, we could see how much the FOM scores differ before and after adding random noise to the circuit components. 


Hopefully if I get good results from this, the next step would be to have the algorithm create the amplifier from scratch instead of having it just modify resistor and capacitor values.
