import pandas as pd 
import numpy as np 

def loadScheduleData():
	cadetScheduleData = pd.read_csv('cadetScheduleDataRefined.csv')
	print(cadetScheduleData.iloc[0, 9])

loadScheduleData()