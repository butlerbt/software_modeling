import matplotlib.pyplot as plt
import seaborn as sns

class Refrigerator():
    """A smart refrigerator.

    Attributes:
        starting_temp (int): temperature the refrigerator starts at
        data (pd.DataFrame()): If provided, a df with time stamps, emissions data. 
                                Used to record and report simulation data. 
        running_time (int): default=0, time the refrigerator has been running
        watts(float/int): default=200, energy refrigerator consumes while on
    """
    def __init__(self, starting_temp, data=None, running_time=0, watts=200):
        self.starting_temp = starting_temp
        self.current_temp = starting_temp
        self.running_time = running_time
        self.data = data
        self.watts = watts 
    
    def set_lapse_rates(self, heat_rate=5, cool_rate=10, minutes=5):
        """Define and calculate rate at which heat is lost and gained

        Args:
            heat_rate (int, optional): Deg per hour the refrigerator increases when not being cooled. Defaults to 5.
            cool_rate (int, optional): Deg per hour the regrigerator decreases when being cooled. Defaults to 10.
            minutes (int, optional): Number of minutes to calculate the heating/cooling rate. ex: 5 results in deg/5min. Defaults to 5.
        """
        #calculates heat/cool rates per length of minutes
        self.time_step_minutes=minutes
        self.heat_rate = round((heat_rate/60)*self.time_step_minutes,4) #temp increse per 5 minutes off
        self.cool_rate = round((cool_rate/60)*self.time_step_minutes,4) #temp decrease per 5 minutes on 
        
    
    def cool(self, minutes=5):
        """Runs the Refrigerator for 5 minute step, decreases the temperature at the given rate, 
            and keeps a running time count.
        """
        self.current_temp -= self.cool_rate
        self.current_temp = round(self.current_temp,4)
        self.status = 1
        self.running_time += self.time_step_minutes

    def heat(self):
        """Shuts off the Refrigerator and increases temperature. 
        """
        self.current_temp += self.heat_rate
        self.current_temp = round(self.current_temp,4)
        self.status = 0
    
    def calculate_fridge_temp_vector(self, state_vector):
        """Using a proposed seres of refergerator states (ons and offs) calculate the temperature at each step of the series

        Args:
            state_vector (list or np.array): series of states. Ex: [0,1,0,1] represents the refridgerator 
                                                turning off, turning on, turing off, turning on... in that sequence. 

        Returns:
            (list): series of temps at each step for the state vector. Ex: [34,36,39,36]
        """
        fridge_temp_vector = []
        for i in state_vector:
            if i==0:
                #fridge is off, so it warms
                self.heat()
                fridge_temp_vector.append(self.current_temp)
            else:
                #fridge is on so cool
                self.cool()
                fridge_temp_vector.append(self.current_temp)
        return fridge_temp_vector

    def record_data(self, indexes, state_vector, temp_vector):
        """Records the status (on/off), and the temperature of the refridgerator at each time step in the state_vector.
           Data can be accessed at self.data
        Args:
            indexes (list, np.array): dataframe indexes for the row/entries associated with each step in the state/series
            state_vector (list, np.array): series of states. Ex: [0,1,0,1] represents the refridgerator 
                                                turning off, turning on, turing off, turning on... in that sequence.
            temp_vect (list, np.array): series of temps at each step for the state/series. Ex: [34,36,39,36] 
        """
        self.data.loc[indexes, 'status']=state_vector
        self.data.loc[indexes, 'recorded_temp']=temp_vector

    def _calc_carbon_footprint(self):
        #status to minutes running
        self.data['total_time_running_min']=self.data.status*self.time_step_minutes

        #calculate energy used in MWH from Watts (refrige consumes 200W)
        mega_watts = self.watts/1000000 
        self.data['MWH']=mega_watts*(self.data.total_time_running_min/60)

        #calculate marginal carbon footprint per timestep
        self.data['marginal_carbon_footprint_hr']=self.data.MWH*self.data.MOER

        #calculate running total of carbon produced from energy consumed
        self.data['marginal_carbon_cumu_sum']=self.data.marginal_carbon_footprint_hr.cumsum()

    def _report_prep(self):
        """helper function to prepare data for plotting/report
        """
        #define aggregation methods for resampling
        agg_map = {
            'MOER':'sum', 
            'status':'sum', 
            'recorded_temp':'last',
            'total_time_running_min':'sum',
            'marginal_carbon_footprint_hr':'sum',
        }

        #create copy and set time index
        self.data_to_plot = self.data.copy()
        self.data_to_plot.set_index('timestamp', inplace=True)

        #resample to hourly data for chart clarity
        self.data_to_plot = self.data_to_plot.resample('H').agg(agg_map)
        self.data_to_plot.reset_index(inplace=True)

    def report(self, file_path='reports/Refrigerator_Simulation.jpg'):
        """Creates report of simulation with figures and print outs. Saves to /reports/Refrigerator_Simulation.jpg
        """
        self._calc_carbon_footprint()
        self._report_prep()
        
        #matplotlib graphing
        fig, ax = plt.subplots(nrows=2, ncols=1,figsize=(40,16))
        ax2 = ax[0].twinx()
        ax1_2 = ax[1].twinx()

        ax[0].plot("timestamp", "recorded_temp", data=self.data_to_plot, color='teal', label='Temperature')
        ax2.plot("timestamp", "MOER", data=self.data_to_plot, color='purple', label='MOER')
        ax[1].bar(self.data_to_plot.timestamp, self.data_to_plot.total_time_running_min, .03, color='teal', label='Minutes')
        ax1_2.plot("timestamp", "marginal_carbon_cumu_sum",data=self.data, color='purple', label='CO2')

        ax[0].set_xlim(xmin='2019-03-01', xmax='2019-04-01')
        ax[1].set_xlim(xmin='2019-03-01', xmax='2019-04-01')
        ax[1].set_ylim(ymax=60)
        ax1_2.set_ylim(ymin=0)

        ax[0].set_ylabel('Refrigerator Temperature (F)')
        ax[1].set_ylabel('Minutes running, per hour period')
        ax2.set_ylabel('Hourly total MOER (lbs/mwh)')
        ax1_2.set_ylabel('CO2 simulation cumulative sum (lbs)')

        ax2.legend(loc='upper left')
        ax[0].legend()
        ax1_2.legend()
        ax[1].legend()

        ax[0].set_title('Refrigerator Simulation')
        plt.savefig(file_path)

        print(f'Total amount of CO2 produced (lbs): {self.data.marginal_carbon_footprint_hr.sum()}')
        print(f'Total run time minutes: {self.running_time}')
        print(f'Average time running per hour: {self.data_to_plot.total_time_running_min.mean()}')
        print(f'Average internal temperature: {self.data.recorded_temp.mean()}')

    


        
        
        

