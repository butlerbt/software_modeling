import pandas as pd
import numpy as np
from src.refrigerator import *
import pytest

def mock_data():
    time_series = pd.date_range(start=('1990-01-01 00:00:00+00:00'), end='1990-01-01 23:00:00+00:00', freq='H')
    moer_mock_data = np.array([0,0,0,0,100,100,100,100,0,0,0,0,100,100,100,100,0,0,0,0,100,100,100,100])
    mock_df = pd.DataFrame({'timestamp':time_series,'MOER':moer_mock_data})
    fridge = Refrigerator(starting_temp=43,data=mock_df, running_time=0)
    fridge.set_lapse_rates(5,10,60)
    test_idx = np.linspace(0,23,num=24, dtype='int')
    test_state_vector=np.ones(24, dtype='int')
    test_temp_vect = fridge.calculate_fridge_temp_vector(test_state_vector)
    fridge.record_data(test_idx, test_state_vector, test_temp_vect)
    return fridge


def test_set_lapse_rates():
    fridge=mock_data()
    assert fridge.heat_rate == 5
    assert fridge.cool_rate == 10

def test_calculate_fridge_temp_vector():
    fridge=mock_data()
    starting_temp = fridge.current_temp

    test_temp_vector = fridge.calculate_fridge_temp_vector([0,0])
    assert test_temp_vector == [starting_temp+5, starting_temp+10] 

    test_temp_vector = fridge.calculate_fridge_temp_vector([1,1])
    assert test_temp_vector == [starting_temp, starting_temp-10] 


def test_record_data():
    fridge=mock_data()
    assert fridge.data.iloc[23]['recorded_temp']==43-(fridge.cool_rate*24)

def test_calc_carbon_footprint():
    fridge=mock_data()
    fridge._calc_carbon_footprint()
    assert fridge.data['total_time_running_min'].sum()==(len(fridge.data)*fridge.time_step_minutes)
    assert fridge.data['MWH'].sum()==(fridge.watts/1000000*len(fridge.data))
    assert np.round(fridge.data.iloc[-1]['marginal_carbon_cumu_sum'],3)==fridge.data['marginal_carbon_footprint_hr'].sum()

