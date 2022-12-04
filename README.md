# VLSI design

#### Project Work - Combinatorial Decision Making and Optimization

**Alessandro Lombardini - alessandr.lombardin3@studio.unibo.it**

**Giacomo Melacini - giacomo.melacini@studio.unibo.it**

**Matteo Rossi Reich - matteo.rossireich@studio.unibo.it**

**Lorenzo Tribuiani - lorenzo.tribuiani@studio.unibo.it**

## Prerequisites

### CP

### MIP

Install AMPL from [AMPL website](https://portal.ampl.com/account/ampl/login)

## Required Packages and installation
1. Clone repository

2.  Open a terminal

3. Create and activate a virtual environment with:

   ```python -m venv [name-of-venv]```

   ```./[name-of-venv]/Scripts/activate ```

   ```pip install -e . ```

4. Install the requirements with:

   ```pip install -r requirements.txt```  
   
5. Install mathsat and z3 for SMT executions via pysmt with:

   ```pysmt-install --msat```  

   ```pysmt-install --z3```  

## Usage

Once the project is installed, to run an execution give, from the root directory:  


 ```python main.py [-h] [-i] [-p] [-r] {CP, SAT, SMT, LP} ...```  

 In the following table all the optional and positional argument (shared or selective from paradigm) are reported:  

| TABLE OF COMMANDS ||                             |                |
| :-----------: | :------------: | :---------: | :------------: |
| long argument | short argument | Description | Allowed params |
| **OPTIONAL SHARED PARAMETERS** |                |             |                |
| *--ins* | *-i* | Select instance to solve | 1-40<br />omit to execute all |
| *--print_img* | *-p* | Toggle image saving | None |
| *--rotation* | *-r* | Toggle solving with allowed rotation | None |
| **POSITIONAL ARGUMENTS** |                |             |                |
| paradigm |                | Select the solving paradigm | CP \| SAT \| SMT \| LP |
| **CP REQUIRED ARGUMENTS** |                |             |                |
| *--model* | *-m* | Select CP model | max \|sbs (one or both) |
| --solver | -s | Select CP solver | chuffed \| gecode (one or both) |
| **SAT REQUIRED ARGUMENTS** |  |  |  |
| *--model* | -m | Select SAT model | SATModel \| SATModelBorders |
| --encoding | -e | Select SAT encoding | seq \| np \| bw \| he |
| *--symmetry_breaking* | *-sb* | Choose if the symmetry breaking constraint has to be used | None |
| **SMT REQUIRED ARGUMENTS** |  |  |  |
| *-m* | --model | Select SMT model | z3Py \| z3Py_rotation \| z3Py_parallel_rotation \| z3Py_parallel \| pySMT_z3 \| pySMT_msat |
| **MIP REQUIRED ARGUMENTS** |  |  |  |
| *-m* | *--model* | Select MIP model | std \| strong (one or both) |
| *-s* | *--solver* | Select MIP solver | gurobi \| cplex \| copt \| highs \| xpress (one or more) |
| **MIP OPTIONAL ARGUMENTS** |  |  |  |
| *-a* | *--ampl_dir* | If the AMPL installation directory is not in the system search path, specify the full path to the AMPL installation directory | String with full path to AMPL installation dir |

