![Tests](https://github.com/OzYossarian/Kandel/actions/workflows/tests.yml/badge.svg)


# FaultTolerantQPU

PJ's take:

The aim of this package is to make it convenient to simulate the performance of Fault-Tolerant Quantum Processing Units QPU's.
We aim to make simulations convenient by compiling logical circuits with a noise model down to a stim circuit with detectors and observables.
TODO: Examples folder.

Teague's take: this package aims to act as a bridge between a high-level description of a quantum code and a low-level 
quantum circuit implementing it - specifically, a Stim circuit. In other words, it's a compiler. We believe that Stim 
is currently the best tool around for quantum circuit simulation, and agree with its ethos of building circuits from 
the ground up, since this is most useful for exploration. That said, there are many cases where one just wants to be 
given a circuit for a code with the minimum of fuss. Kandel aims to do exactly this, at the cost of a small loss of 
flexibility in the circuit construction. The main use case we have in mind is for running memory experiments on 
quantum codes under circuit-level noise; if you can provide a high-level description of the code, Kandel can give you a 
Stim circuit, which can then be repeatedly sampled and decoded (we recommend Sinter!).

Disclaimer 1: Is currently a prototype and open to breaking changes. Proper release will come soon. 

Disclaimer 2: Project aims are and always will be relatively humble. We are not software engineers, but rather 
researchers who wanted a tool like this and figured we may as well go the extra half a step of making it publically 
available.

To run tests in the repository...
