import pandas as pd 
import numpy as np 

pd.set_option('display.max_columns', 8)
pd.set_option('display.width', 1000)

cadetScheduleDataRefined = pd.DataFrame()
classSLCDF = pd.DataFrame()
classInstrRoom = pd.DataFrame()

cadetScheduleDataRaw = pd.read_csv('cadetScheduleDataRaw.csv')
numCadets = cadetScheduleDataRaw.shape[0]

#Initizaling Data Storage container

#Primary Scheduling Datatable construct
cadetFirstNames = []
cadetMiddleNames = []
cadetLastNames = []
cadetSquadrons = []
cadetClassYrs = []
cadetScheduleData = []
cadetTotalCredits = []

#Credit Reference Datatable constructs
classPeriodArray = [('M' + str(period)) for period in range(1,8)] + [('T' + str(period)) for period in range(1,8)] + ['U1']
classSLCredit = []

#Instructor Room Pairing Datatable constructs
classInstrPeriods = []

for cadet in range(numCadets):
	
	#Demographic Information Processing 
	cadetDemoInfo = cadetScheduleDataRaw['Cadet Demographic Information'][cadet]
	cadetDemoInfoArray = str.split(cadetDemoInfo)

	cadetClassYr = int(cadetDemoInfoArray[-1])
	cadetSquadron = int(cadetDemoInfoArray[-2])
	cadetNameData = ""

	for i in cadetDemoInfoArray[:-2]:
		cadetNameData += i + ' '

	cadetLastName = cadetNameData.split(',')[0]
	cadetFirstName = cadetNameData.split(',')[1].split(' ')[1]
	cadetMiddleName = "".join(cadetNameData.split(',')[1].split(' ')[2:])

	#Appending Demographic Information
	cadetFirstNames.append(cadetFirstName)
	cadetMiddleNames.append(cadetMiddleName)
	cadetLastNames.append(cadetLastName)
	cadetSquadrons.append(cadetSquadron)
	cadetClassYrs.append(cadetClassYr)

	#Schedule Data Processing
	cadetSchedule = cadetScheduleDataRaw['Schedule Array'][cadet][1:-1].split(']')
	cadetTotalCredit = 0
	cadetScheduleDict = {}
	classSections = {}

	for classData in cadetSchedule:

		#Read in schedule data as an array
		aggregateClassData = classData.replace('[','').replace('\'','').split(',')

		#Removes null characters
		if aggregateClassData[0] == '':
			aggregateClassData = aggregateClassData[1:]

		#For class periods that the cadet has a class:
		if aggregateClassData != []:

			#Checks if class is a double period or not
			classPeriods = aggregateClassData[3].split('-')
			classSections[classPeriods[0][1:-1]] = classPeriods[0][-1]
			classPeriods[0] = classPeriods[0][1:-1]

			#Attaches a section marker to the second period if there is a second period
			try:
				classSections[classPeriods[1][:-1]] = classPeriods[1][-1]
				classPeriods[1] = classPeriods[1][:-1]
			except:
				pass

			#Removes leading whitespace characters
			classNameShort = aggregateClassData[0].lstrip()
			classNameLong = aggregateClassData[1].lstrip()

			#Interprets class credits as floats
			try:
				classCredits = float(aggregateClassData[2])
			except:
				pass

			#Further leading whitespace elimination
			classRoom = aggregateClassData[4].lstrip()
			classInstructor = aggregateClassData[5].lstrip()

			#Summation of credits hours
			cadetTotalCredit += classCredits
			#Collects classdata into a single array for easy processing later
			classData = [classNameShort, classNameLong, classCredits, classRoom, classInstructor]

			#Hashing periods and classData
			for period in classPeriods:

				#Handles multiple periods
				try:
					cadetScheduleDict[period]
					cadetScheduleDict[period].append(classData)
				except:
					cadetScheduleDict[period] = [classData]


	cadetTotalCredits.append(cadetTotalCredit)
	scheduleDataArray = []

	for classPeriod in classPeriodArray:
		try:
			if len(cadetScheduleDict[classPeriod]) == 1:
				cadetScheduleDataRefined.loc[cadet, classPeriod] = cadetScheduleDict[classPeriod][0][0] + classSections[classPeriod]

				classInstrPeriods.append([cadetScheduleDict[classPeriod][0][0] + classSections[classPeriod], cadetScheduleDict[classPeriod][0][4].replace("\"",""), cadetScheduleDict[classPeriod][0][3]])

				classSLCredit.append([cadetScheduleDict[classPeriod][0][0], cadetScheduleDict[classPeriod][0][1], cadetScheduleDict[classPeriod][0][2]])

			else:
				cadetScheduleDataRefined.loc[cadet, classPeriod] = ""

				for subClass in cadetScheduleDict[classPeriod]:
					cadetScheduleDataRefined.loc[cadet, classPeriod] = cadetScheduleDataRefined.loc[cadet, classPeriod] + subClass[0] + classSections[classPeriod]

				classInstrPeriods.append([subClass[0] + classSections[classPeriod], subClass[4].replace("\"",""), subClass[3]])

				cadetScheduleDataRefined.loc[cadet, classPeriod] = cadetScheduleDataRefined.loc[cadet, classPeriod].rstrip('/')

				classSLCredit.append([subClass[0], subClass[1], subClass[2]])


		except KeyError:
			cadetScheduleDataRefined.loc[cadet, classPeriod] = np.nan

cadetScheduleDataRefined['First Name'] = cadetFirstNames
cadetScheduleDataRefined['Middle Name'] = cadetMiddleNames
cadetScheduleDataRefined['Last Name'] = cadetLastNames
cadetScheduleDataRefined['Squadron'] = cadetSquadrons
cadetScheduleDataRefined['Class Year'] = cadetClassYrs
cadetScheduleDataRefined['Primary Major'] = cadetScheduleDataRaw['Major']
cadetScheduleDataRefined['Academic Advisor'] = cadetScheduleDataRaw['Academic Advisor']
cadetScheduleDataRefined['Total Credit Hours'] = cadetTotalCredits

cadetScheduleDataRefined = cadetScheduleDataRefined[cadetScheduleDataRefined.columns.tolist()[15:] + cadetScheduleDataRefined.columns.tolist()[:15]]

npClassSLC = np.array(classSLCredit)
uniqueClassSLC = np.unique(npClassSLC, axis = 0)

cadetScheduleDataRefined.to_csv('cadetScheduleData.csv', index = False)

classShortNames = []
classLongNames = []
classCreditCount = []

for classSLC in uniqueClassSLC:
	classShortNames.append(classSLC[0])
	classLongNames.append(classSLC[1])
	classCreditCount.append(classSLC[2])

classSLCDF['Class Name Short'] = classShortNames
classSLCDF['Class Name Long'] = classLongNames
classSLCDF['Credits'] = classCreditCount

classSLCDF.to_csv('classNameCreditData.csv', index = False)

classShortNameSections = []
classInstructors = []
classRooms = []


npClassInstrPeriod = np.array(classInstrPeriods)
uniqueClassInstrPeriods = np.unique(npClassInstrPeriod, axis = 0)

for classInstrPeriod in uniqueClassInstrPeriods:
	classShortNameSections.append(classInstrPeriod[0])
	classInstructors.append(classInstrPeriod[1])
	classRooms.append(classInstrPeriod[2])

classInstrRoom['Class Section Name'] = classShortNameSections
classInstrRoom['Class Section Instructor'] = classInstructors
classInstrRoom['Class Section Room'] = classRooms

classInstrRoom.to_csv('classInstrRoomData.csv', index = False)