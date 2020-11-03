import pandas as pd 

def prep_df(moer_df, start_dt, end_dt):
    """Basic data operations to preprocess dataframe of MOER data 

    Args:
        moer_df (pd.DataFrame): df with timestamps and MOER forecast data
        start_dt (string/obj): starting datetime for period of simulatation
        end_dt (string/obj): ending datetime for period of simulatation

    Returns:
        pd.DataFrame: MOER data clipped to period of simulation and with new columns ['status','recorded_temp']
    """
    moer_df.timestamp=pd.to_datetime(moer_df.timestamp)
    moer_df['status']=0
    moer_df['recorded_temp']=0
    end_dt = pd.Timestamp(end_dt)+pd.Timedelta(55,'minutes')
    moer_df = moer_df.set_index('timestamp')[start_dt:end_dt]
    moer_df.reset_index(inplace=True)
    return moer_df

def get_forecast_idxs(moer_df, current_time_stamp, forecast_length):
    """helper function to get indexes of timestamps of available forecast period.

    Args:
        moer_df (pd.DataFrame): df with timestamps and MOER forecast data
        current_time_stamp (pd.DateTime obj): current time stamp to the start the forecast from 
        forecast_length (int): length of available forecast in # of periods

    Returns:
        (list): list of indexes
    """
    #find index of current time stamp
    ts_idx = moer_df.loc[moer_df.timestamp==current_time_stamp].index[0]
    
    #get index of current and future entries
    idxs = [i+ts_idx for i in range(forecast_length)]
    return idxs

def get_hr_forecast(moer_df, indexes):
    """Get vector of future MOER emissions data 

    Args:
        moer_df (pd.DataFrame): indexed df with MOER data in col 'MOER' and timestamp in col 'timestamp'
        indexes (list): df indexes of time steps  

    Returns:
        (np.array): array of the MOER data for each period available in the forecast
    """
    #get forecast MOER data into vector
    moer_vect_hr = moer_df.loc[indexes]['MOER'].values
    return moer_vect_hr


