import numpy as np
import mlrose
import warnings

def baseline(fridge_temp):
    if round(fridge_temp)==33:
        return np.zeros(12,dtype='int')
    elif round(fridge_temp)==38:
        return np.zeros(12, dtype='int')
    elif round(fridge_temp)==43:
            return np.ones(12, dtype='int')
    else:
        return np.ones(12, dtype='int')
        warnings.critical(f'frige temp is wrong {fridge_temp}')

    
    

def moer_min(state, moer_vector, fridge_temp, heat_rate, cool_rate):
    """Custom fitness function for minimizing MOER to be used in minimization algorithm. This fitness function
        minimzes MOER while keeping the internal temp <43 and >33. 

    Args:
        state (array): discrete vector generated by optimizing algo representing possible series of binary on/off states. 
        moer_data (array): array of moer data for each time step with same length of state.
        fridge_temp (int/float ): initial fridge temp at start of hour.

    Returns:
        float: total MOER emissions at current state
    """

    #sum up total MOER from proposed state vector
    moer_sum = sum(moer_vector*state)

    #calculate forecasted fridge temp for each time step in hour's proposed state vector
    for i in state:
        if i ==0:
            #fridge is off, so warm
            fridge_temp += heat_rate
            fridge_temp = round(fridge_temp,3)

        elif i ==1: 
            #fridge is on so cool
            fridge_temp -= cool_rate
            fridge_temp = round(fridge_temp,3)

        #enforce temperature parameters:
        if fridge_temp > 43 or fridge_temp < 33:
            return 99999999999
    #if temp parameters not exceded, return total MOER 
    return moer_sum

def initial_state(fridge_temp,state_length):
    """Sets state_vector inital condition for use in optimization algorithm using heuristics to potentially accelerate finding minimum. 

    Args:
        fridge_temp (int): Current refridgerator temperature.

    Returns:
        (np.arry): initial state vector with length of available forecast
    """
    # Define initial state vector based on fridge temp
    if fridge_temp < 36:
        #if fridge is coldish, then lean towards not running much
        # init_state = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        init_state = np.zeros((state_length), dtype=int)
    elif fridge_temp >40:
        #if fridge is warm then lean towards running/cooling
        # init_state = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        init_state = np.ones((state_length), dtype=int)
    else: 
        #if fridge is middle ground then randomized initial state
        init_state=None
    return init_state

def optimize(state_length, fitness_fn, algorithm, algorithm_kwargs, **cust_fitness_fn_kwargs):
    """Uses optimization techniques to identify binary state vector that minimizes fitness (MOER) over forecast period. 

    Args:
        state_length (int): length of state_vector to be optimized (minimized). (represents length of forecast in periods)
                                ex: 1 hr forecast series given in 5 minute periods would have a length of 12. 
        fitness_fn: callable Function for calculating fitness of a state with the signature fitness_fn(state, **kwargs)
        algorithm (mlrose optimization object): One of: mlrose.simulated_anneling, mlrose.random_hill_climb
                                    mlrose.hill_climb, mlrose.genetic_alg, or mlrose.mimic. See mlrose documentation for details. 
        algorithm_kwargs (dict): kwargs for mlrose optimization algorithims. 
        


    Returns:
        best_state: (array) Numpy array containing state that optimizes the fitness function.
        best_fitness: (float) Value of fitness (MOER) at best state. 
        curve: (array) Numpy array containing the fitness at every iteration. Must include in kwargs curve=True.
    """
    #create custom fitness class using mlrose constructor
    cust_fitness_fn = mlrose.CustomFitness(fitness_fn, **cust_fitness_fn_kwargs)

    #define problem using mlrose constructor
    prob = mlrose.DiscreteOpt(length=state_length, 
                                fitness_fn=cust_fitness_fn, 
                                maximize=False, 
                                max_val=2)

    #set initial state using heuristic to accelerate optimization 
    init_state = initial_state(cust_fitness_fn_kwargs.get('fridge_temp'),state_length=state_length)

    #use mlrose optimization algo to find state vector with minimum MOER
    best_state, best_fitness, curve = algorithm(prob,init_state=init_state, **algorithm_kwargs)
    
    return best_state, best_fitness, curve





