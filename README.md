![Tests](https://github.com/OzYossarian/Kandel/actions/workflows/tests.yml/badge.svg)


# Kandel

PJ's take:

The aim of this package is to make it convenient to simulate the performance of Fault-Tolerant Quantum Processing Units QPU's.
We aim to make simulations convenient by compiling logical circuits with a noise model down to a stim circuit with detectors and observables.
TODO: Examples folder.

Teague's take: 

This package aims to act as a bridge between a high-level description of a quantum code and a low-level 
quantum circuit implementing it - specifically, a Stim circuit. In other words, it's a compiler. We believe that Stim 
is currently the best tool around for quantum circuit simulation, and agree with its ethos of building circuits from 
the ground up, since this is most useful for exploration. That said, there are many cases where one just wants to be 
given a circuit for a code with the minimum of fuss. Kandel aims to do exactly this, at the cost of a small loss of 
flexibility in the circuit construction. The main use case we have in mind is for running memory experiments on 
quantum codes under circuit-level noise; if you can provide a high-level description of the code, Kandel can give you a 
Stim circuit, which can then be repeatedly sampled and decoded (we recommend Sinter!).

### Disclaimer 1
This is currently a prototype and susceptible to breaking changes (and bugs). Proper release will come soon. 

### Disclaimer 2 
Project aims are and always will be relatively humble. We are not software engineers, but rather 
researchers who wanted a tool like this and figured we may as well go the extra half a step of making it publically 
available. If you want a new feature, please contribute! We'd love to hear from you. On which note...

## Contact us
We're interested in hearing more about use cases for which you would use/are using Kandel (rather than using Stim directly, or indeed rather than using another package altogether). The main use case we had in mind was for profiling a code through a circuit-level noise simulation, but we want to know if you're using it for something else! Or if you thought about using Kandel but decided it wasn't right for you, we want to hear about this too! In short: we want to hear any and every opinion you have about this package. Just raise an issue and write your comments in it.

## Development Process
Thanks for contributing! Every change should have an associated issue on GitHub. Create a new branch, and include the issue number in the title - e.g. a branch called 'issue_24_change_printer_opacity'. Make changes to the code. Write/update tests! Then create a pull request from your branch into 'dev' (the tests should automatically run - check they pass!). Then wait for someone to review your request :)
