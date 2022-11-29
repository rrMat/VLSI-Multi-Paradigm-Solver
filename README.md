# VLSI design

#### Project Work - Combinatorial Decision Making and Optimization

**Alessandro Lombardini - Giacomo Melacini - Matteo Rossi Reich - Lorenzo Tribuiani**

[Overleaf link for editing repo](https://it.overleaf.com/9465416397qdwqknsgcnjh)

# Required Packages and installation
Clone repository  
Open a terminal and give: 

```pip install z3-solver```  
```pip install minizinc``` 

if not installed, the following packages are required too: 

**numpy**  
**pandas**  
**matplotlib**

finally give the command:  

 ```pip install -e .```

# Usage

Once the project is installed, to run an execution give, from the root directory:  


 ```python main.py [-h] [-i] [-p] [-r] {CP, SAT, SMT, LP} ...```  

 In the following table all the optional and positional argument (shared or selective from paradigm) are reported:  

![Table of commands](/table.png)

