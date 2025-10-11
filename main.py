#Main source code
from scrapFromUSDA import WebAutomator
from selenium.webdriver.common.by import By

USDA = WebAutomator(True)
programLinks = []
USDA.navigate_to("https://www.rd.usda.gov/programs-services/all-programs?page=0")
index = USDA.find_element(By.CSS_SELECTOR, "li.usa-pagination__item:nth-child(5) > a:nth-child(1)").text
for i in range (0, int(index)):
    USDA.navigate_to(("https://www.rd.usda.gov/programs-services/all-programs?page=" + str(i)))
    programsList = USDA.find_element(By.CSS_SELECTOR, "div.view-content:nth-child(3)")
    programs = programsList.find_elements(By.CLASS_NAME, "views-row")
    for i in programs:
        prog = i.find_element(By.TAG_NAME, "a").get_attribute("href")
        programLinks.append(prog)
title = []
program_status = []
program_deadline = []
program_overview = []
program_overview_link = []
program_apply = []
program_requirements = []
program_contact = []
program_contact_link = []
program_events = []
for i in programLinks:
    USDA.navigate_to(i)
    title.append(USDA.find_element(By.CSS_SELECTOR, "#main-content > div > div > div > h1").text)
    program_status.append(USDA.find_element(By.CSS_SELECTOR, "#block-usda-rd-uswds-2-content--2 > article > div.grid-row.bg-base-lighter.margin-top-2.padding-105.program-heading > div.desktop---grid-col-3.tablet---grid-col-4.grid-col-12.padding-05 > div").text)
    program_deadline.append(USDA.find_element(By.CSS_SELECTOR, "#block-usda-rd-uswds-2-content--2 > article > div.grid-row.bg-base-lighter.margin-top-2.padding-105.program-heading > div.desktop---grid-col-9.tablet---grid-col-8.grid-col-12.padding-05 > div").text)
    program_overview.append(USDA.find_element(By.CSS_SELECTOR, "#overview > div > div").text)
    program_overview_link.append(USDA.find_element(By.CSS_SELECTOR, "#overview > div > div > div > div > span > span > div > div > p > a").get_attribute('href'))
    program_apply.append(USDA.find_element(By.CSS_SELECTOR, "#to-apply").text)
    program_requirements.append(USDA.find_element(By.CSS_SELECTOR, "#other-requirements > div > div > div > div > div > div > p").text)
    program_contact.append(USDA.find_element(By.CSS_SELECTOR, "#contact > div > div > div > div > div > div > p:nth-child(5)").text)
    program_contact_link.append(USDA.find_element(By.CSS_SELECTOR, "#contact > div > div > div > div > div > div > p:nth-child(5) a").get_attribute('href'))
    program_events.append(USDA.find_element(By.CSS_SELECTOR, "#events").text)
print(title)
