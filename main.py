#Main source code
from scrapFromUSDA import WebAutomator
from selenium.webdriver.common.by import By

USDA = WebAutomator()
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