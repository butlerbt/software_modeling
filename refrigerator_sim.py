
import pandas as pd
import numpy as np
from src.refrigerator import *
from src.utils import *
from src.optimization import *
import logging
import datetime

if __name__ == '__main__':
    #define simulation parameters, import and process MOER data
    df = pd.read_csv('data/MOERS.csv')
    starting_temp=33
    start_dt = '2019-03-01 00:00:00+00:00'
    end_dt='2019-03-31 23:00:00+00:00'
    forecast_length=12 #number of time steps available in 1 hr perfect forecast
    df=prep_df(df, start_dt=start_dt, end_dt=end_dt)

    ###BASELINE SIMULATION
    #create log file for baseline simulation
    logging.basicConfig(filename=f'log/baseline/baseline_fridge_simulation{datetime.datetime.now()}.log', level=logging.INFO)
    #instantiate the Refrigerator and set lapse rates for baseline simulation
    BaseLineFridge=Refrigerator(starting_temp=starting_temp, data=df.copy())
    BaseLineFridge.set_lapse_rates()

    logging.info(f'Started Refrigerator simulation at {datetime.datetime.now()}')
    #begin baseline (simple) simulation
    for i in pd.date_range(start=start_dt, end=end_dt, freq='h', tz='UTC'):
        #for each period in 12 step forecast get MOER data and define the 'state' of the fridge across the periods
        indexes = get_forecast_idxs(df, i, forecast_length=forecast_length)
        moer_vect_hr = get_hr_forecast(df, indexes=indexes)
        base_line_state = baseline(fridge_temp=BaseLineFridge.current_temp)

        #caculate temperature change based on state across time periods, sum hourly MOER for logging, record state and temp data
        fridge_temp_vector = BaseLineFridge.calculate_fridge_temp_vector(base_line_state)
        MOER_hr = sum(moer_vect_hr*base_line_state)
        BaseLineFridge.record_data(indexes, base_line_state, fridge_temp_vector)
        logging.info(f"Current time stamp: {i} Best state: {base_line_state} Minimum MOER achieved: {MOER_hr} Max hour MOER: {moer_vect_hr.sum()} Fridge Temp: {BaseLineFridge.current_temp}")

    #create plots of simulation
    print('Baseline simulation results:')
    BaseLineFridge.report(file_path='reports/Refrigerator_Simulation_baseline.jpg')
    logging.info(f'Finished Simulation at {datetime.datetime.now()}')

    ### OPTIMZED SIMULATION
    logging.basicConfig(filename=f'log/fridge_simulation{datetime.datetime.now()}.log', level=logging.INFO)
    #instantiate the Refrigerator and set lapse rates for optimzed simulation
    Fridge=Refrigerator(starting_temp=starting_temp, data=df.copy())
    Fridge.set_lapse_rates()

    logging.info(f'Started Refrigerator simulation at {datetime.datetime.now()}')
    #begin optimzed simulation
    for i in pd.date_range(start=start_dt, end=end_dt, freq='h', tz='UTC'):
        #for each period in 12 step forecast get MOER forecast for each time step
        indexes = get_forecast_idxs(df, i, forecast_length=forecast_length)
        moer_vect_hr = get_hr_forecast(df, indexes=indexes)

        #define parameters for fitness/objective function to be used in optimization
        fitness_func_kwargs = {
            'moer_vector':moer_vect_hr, 
            'fridge_temp':Fridge.current_temp, 
            'heat_rate':Fridge.heat_rate, 
            'cool_rate':Fridge.cool_rate
                }
        #define parameters for simulated_annealing optimzation    
        algorithm_kwargs = {
            'max_attempts':10,
            'max_iters':10,
            'random_state': 1,
            'schedule':mlrose.ExpDecay(),
            'curve':True
                }
        #use simulation_anneling to optimze the fridge's state given the next 12 periods MOER forecast (minimizing MOER)        
        best_state, best_fitness, curve = optimize(forecast_length, moer_min, mlrose.simulated_annealing, algorithm_kwargs=algorithm_kwargs, **fitness_func_kwargs)
        fridge_temp_vector = Fridge.calculate_fridge_temp_vector(best_state)

        #record simuation data
        Fridge.record_data(indexes, best_state, fridge_temp_vector)
        logging.info(f"Current time stamp: {i} Best state: {best_state} Minimum MOER achieved: {best_fitness} Max hour MOER: {moer_vect_hr.sum()} Optimzation iterations: {len(curve)} Fridge Temp: {Fridge.current_temp}")

    #create plots of simulation
    print('Optimized simulation results:')
    Fridge.report()
    logging.info(f'Finished Simulation at {datetime.datetime.now()}')




