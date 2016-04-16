from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os, time
import datetime
import util
        
def getAvailableSlots(driver):
    #Set timezone
    global moreAvailableTimeSlots
    os.environ['TZ'] = 'America/Los_Angeles'
    time.tzset()

    startTime = datetime.datetime.now()
    #startTime = datetime.datetime(2016, 12, 31, 10, 31, 0)

    curEpoch = time.mktime(startTime.timetuple())
    timeDelta = 36 * 60 * 60
    searchTillTimeStamp = curEpoch + timeDelta
    searchTillTime = datetime.datetime.fromtimestamp(searchTillTimeStamp)

    #Get the calendar
    soup = getCalendarSoup(driver, startTime.year, startTime.month)
    availableTimeSlots, myReservedTimeSlots = getTimeSlotsForSoup(searchTillTimeStamp, soup)

    #Get the next month/year if the searchTill month is different
    if(startTime.month != searchTillTime.month):
        soup = getCalendarSoup(driver, searchTillTime.year, searchTillTime.month)
        moreAvailableTimeSlots, moreMyReservedTimeSlots = getTimeSlotsForSoup(searchTillTimeStamp, soup)
        availableTimeSlots += moreAvailableTimeSlots
        myReservedTimeSlots += moreMyReservedTimeSlots

    return [availableTimeSlots, myReservedTimeSlots]


def getTimeSlotsForSoup(searchTillTimeStamp, soup):
    availableSlots = soup.find_all('div', class_='available')
    availableTimeSlots = getAvailableTimeSlots(availableSlots, searchTillTimeStamp)
    myReservedSlots = soup.find_all('div', class_='unavailable-mine')
    myReservedTimeSlots = getAvailableTimeSlots(myReservedSlots, searchTillTimeStamp)
    return availableTimeSlots, myReservedTimeSlots


def getAvailableTimeSlots(availableSlots, searchTillTime):
    timestamps = []
    searchNextMonth = True
    for slot in availableSlots:
        timeStampNode = slot.find('div', class_='slot-timestamp')
        if timeStampNode:
            timeStamp = int(timeStampNode.text)
            if timeStamp < searchTillTime:
                timestamps.append(timeStamp)
            else:
                searchNextMonth = False
                break
    return timestamps


def getCalendarSoup(driver, year, month):
    calendarUrl = "https://my.us.sailtime.com/calendars/index/year:{}/month:{}/base:30/boat:272/mode:scheduler".format(year, month)
    driver.get(calendarUrl)
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.visibility_of_element_located((By.ID, 'scheduler')))
    try:
        driver.implicitly_wait(10)  # seconds
        myDynamicElement = driver.find_element_by_id("nonexistentelementghost")
    except:
        pass
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup


def login(driver):
    driver.get("https://my.us.sailtime.com/login")

    username = driver.find_element_by_id("UserUsername")
    password = driver.find_element_by_id("UserPassword")

    username.send_keys(os.environ['SAILTIME_USER_NAME'])
    password.send_keys(os.environ["SAILTIME_PASSWORD"])

    username.submit()

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.visibility_of_element_located((By.ID, 'facets')))

def getWebDriver():
    return webdriver.PhantomJS()

def startMechanizing():
    driver = getWebDriver()
    login(driver)
    return getAvailableSlots(driver)

def reserveTheSlotAt(timestamp):
    driver = getWebDriver()
    print timestamp
    print "get web driver"
    login(driver)
    print "logged in"
    curMonth = datetime.datetime.now().month
    print  curMonth
    timeRequired = util.getDateTime(timestamp)
    monthToLookFor = timeRequired.month
    yearToLookFor = timeRequired.year
    soup = getCalendarSoup(driver, yearToLookFor, monthToLookFor)
    print "have some soup"
    timestampNodes = driver.find_elements_by_xpath(
        '//div[contains(text(), "{0}") and @class="slot-timestamp"]'.format(timestamp))
    print timestampNodes
    if timestampNodes:
        slotNode = timestampNodes[0].find_element_by_xpath("..")
        print slotNode.get_attribute("outerHTML")
        slotNodeClasses = slotNode.get_attribute("class").split()
        if "available" in slotNodeClasses:
            try:
                slotNode.click()
                WebDriverWait(driver, 10).until(lambda s, timestampNodes = timestampNodes: \
                                                   "unavailable-mine" in timestampNodes[0].find_element_by_xpath(
                                                       "..").get_attribute("class").split())
                print "Reservation successful"
                return True
            except Exception, e:
                print "Exception: " + str(e)
                print "Reservation failed"
                return False
            else:
                return False
    return  False



