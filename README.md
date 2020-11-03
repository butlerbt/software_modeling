# Refrigerator Simulation
Optimzation of a smart refrigerator 

## Running the simulation

### • `wattime_env` conda environment

This project relies on a few specific python libraries/versions. I've included the [`environment.yml`](environment.yml) file to recreate the `wattime_env` conda environment. To do so, please run the following commands:

```bash
# create the zipcode conda environment
conda env create -f environment.yml

# activate the zipcode conda environment
conda activate wattime_env
```
### • running the simluation
Once in the wattime_env environment with the necessary libaries, running the simluation from the main directory is as simple as `python refrigerator_sim.py` 

### Methods/Results

I spent a fair amount of time deciding how I wanted to approach this problem. Its clear that there are many different ways that would be reasonable: heuritics, machine learning, time series forecasting, and optimization. Or some combo of the above. I chose to try optimization (with a small boost from a heuristic or two). To put the optimzation into context I incorporated a simple baseline simulation. 

The simple baseline simulation is as simple as it gets. The refrigerator cools for an hour, warms for two hours, and then repeats with no regards for changing MOER or for reducing amount of time running.

On the other hand, the optimzed simulation uses an optimization algorithim called simulated anneling. This approach resulted in a small reduction of total CO2 produced (~1.6 lbs across the 1 month period), while maintaing the (surpringly) exact same amount of time running. The optimzed solution has a slightly higher average temperature than the baseline results. What is most intesting is plot of the temperature profile against the MOER data. There are times in the simulation where the temperature profile follows the MOER data very closely (dropping when MOER is low, rising when MOER emissions are high). 

Given the availbility of the perfect forecast, I decided that if I could find the optimum on/off series for each hour, that it would probably be close to the optimum solution for the entire time period (or at least a step in the right direction!) So, with this in mind, the simulated anneling optimzation tries to find the optimum 12 step, binary (on/off) vector representig the refrigerator's behavior across each 1 hour time period during the simulation. On/off series that result in low MOER are chosen. On/off series that result in temperatures leaving the allowed range are heavily penalized (so heavily penalized they are never chosen).

My approach has a significant limitation in that the optimzation never sees beyond the 1 hour time period it is currently working in. If it could be implemneted at each 5 minute step, instead of at each hour, it could do better. Also, some additional heuristics could help, and certainly using machine learning or time series forecasting to increase the forecasting window availble to the optimzation, would substantially improve it. Regardless, I enjoyed working on this problem, and it gave me a chance to learn about a new optimzation technique.  










