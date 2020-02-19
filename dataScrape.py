from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from time import sleep

import pandas as pd
import numpy as np
import requests

cadetScheduleDF = pd.DataFrame(columns = ['Cadet Demographic Information', 'Major', 'Class Year', 'Schedule Array'])

driver = webdriver.Chrome()
url = 'https://camis.usafa.edu/ords/apex/f?p=220:1::::::'

driver.get(url)

try:
	agreeButton = driver.find_element_by_xpath("//form/input[@value = 'I AGREE']")
	agreeButton.click()

except:
	print('CAMIS agreement already accepted')

# squadronSelect = Select(driver.find_element_by_xpath("//select[@id = 'P1_SQUADRON']"))

# for squadNum in range(1,41):
# 	squadronSelect.select_by_value(str(squadNum))
# 	sleep(1)

dataRowIndex = 2
pageNum = 110
firstPage = True
cellIndicies = [2,3,4,5,7,8]
nextPageCount = 1

sleep(3)

while True:
	cadetScheduleDataArray = []
	#nextPage = driver.find_element_by_xpath("//div[@id = 'R120439445068567761_data_panel']/div[1]/ul[1]/li[3]/button")

	# while nextPageCount <= 0:
	# 	try:
	# 		nextPage = driver.find_element_by_xpath("//div[@id = 'R120439445068567761_data_panel']/div[1]/ul[1]/li[3]/button")
	# 		#nextPage = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id = 'R120439445068567761_data_panel']/div[1]/ul[1]/li[3]/button")))
	# 		nextPage.click()
	# 		sleep(3.5)
	# 	except:
	# 		print('Next page error')

	# 	nextPageCount += 1

	try:
		generalCadetDataXPath = "//table[@id = '120439541300567762']/tbody/tr["+str(dataRowIndex)+"]"
		cadetScheduleDataXPath = generalCadetDataXPath + "/td[1]/a"

		cadetDemoData = driver.find_element_by_xpath(generalCadetDataXPath).text

		cadetScheduleDataArray.append(cadetDemoData)

		cadetScheduleDataWindow = driver.find_element_by_xpath(cadetScheduleDataXPath)
		cadetScheduleDataWindow.click()

		#scheduleIFrame = driver.find_element_by_tag_name('iframe')
		try:
			scheduleIFrame = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
		except:
			print('Network Error')

		driver.switch_to.frame(scheduleIFrame)
		major = driver.find_element_by_xpath("//input[@id='P2_PRIMARY_MAJOR']").get_attribute('value')
		advisor = driver.find_element_by_xpath("//input[@id='P2_ADVISOR']").get_attribute('value')
		
		cadetScheduleDataArray.extend([major, advisor])

		scheduleRowIndex = 1
		scheduleArray = []
		while True:
			try:
				scheduleRow = driver.find_element_by_xpath("//table[@class = 't-Report-report']/tbody/tr[" + str(scheduleRowIndex) + "]")
				scheduleRowArray = []

				for cellIndex in cellIndicies:
					scheduleRowCell = driver.find_element_by_xpath("//table[@class = 't-Report-report']/tbody/tr[" + str(scheduleRowIndex) + "]/td[" + str(cellIndex) + "]").text
					scheduleRowArray.append(scheduleRowCell)

				scheduleArray.append(scheduleRowArray)
				scheduleRowIndex += 1
			except:
				break

		cadetScheduleDataArray.append(scheduleArray)

		driver.switch_to.default_content()

		webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
		dataRowIndex += 1

		cadetScheduleDF = cadetScheduleDF.append(pd.Series(cadetScheduleDataArray, index = cadetScheduleDF.columns), ignore_index = True)

		
	except:
		try:
			cadetScheduleDF.to_csv('cadetScheduleData/cadetSchedules' + str(pageNum) + '.csv',index = False)
			print(str(pageNum) + ' CSV successfully created')
			dataRowIndex = 2
			pageNum += 1
		except:
			print('SCRAPE COMPLETE')
			break

		sleep(4)
		nextPage = driver.find_element_by_xpath("//div[@id = 'R120439445068567761_data_panel']/div[3]/ul[1]/li[3]/button")
		nextPage.click()
		sleep(4)

driver.quit()
