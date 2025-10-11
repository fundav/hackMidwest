# # Main source code
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
from scrapFromUSDA import WebAutomator

from selenium.webdriver.common.by import By
#from selenium import webdriver
# uri = "mongodb+srv://ander:TopicalSet24#@cluster0.kbzhtfw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)
USDA = WebAutomator()
USDA.navigate_to("https://www.rd.usda.gov/programs-services/business-programs/rural-cooperative-development-grant-program/al")


title = USDA.find_element(By.CSS_SELECTOR, "#main-content > div > div > div > h1")
print (title.text)

program_status = USDA.find_element(By.CSS_SELECTOR, "#block-usda-rd-uswds-2-content--2 > article > div.grid-row.bg-base-lighter.margin-top-2.padding-105.program-heading > div.desktop---grid-col-3.tablet---grid-col-4.grid-col-12.padding-05 > div")
print (program_status.text)

program_deadline = USDA.find_element(By.CSS_SELECTOR, "#block-usda-rd-uswds-2-content--2 > article > div.grid-row.bg-base-lighter.margin-top-2.padding-105.program-heading > div.desktop---grid-col-9.tablet---grid-col-8.grid-col-12.padding-05 > div")
print (program_deadline.text)

program_overview = USDA.find_element(By.CSS_SELECTOR, "#overview > div > div")
print (program_overview.text)

program_overview_link = USDA.find_element(By.CSS_SELECTOR, "#overview > div > div > div > div > span > span > div > div > p > a")
print (program_overview_link.text)

program_apply = USDA.find_element(By.CSS_SELECTOR, "#to-apply")
print (program_apply.text)

program_requirements = USDA.find_element(By.CSS_SELECTOR, "#other-requirements > div > div > div > div > div > div > p")
print (program_requirements.text)

program_contact = USDA.find_element(By.CSS_SELECTOR, "#contact > div > div > div > div > div > div > p:nth-child(5)")
print (program_contact.text)

program_contact_link = USDA.find_element(By.CSS_SELECTOR, "#contact > div > div > div > div > div > div > p:nth-child(5)")
print (program_contact_link.text)

program_events = USDA.find_element(By.CSS_SELECTOR, "#events")
print (program_events.text)


#contact info (county - phone number) (not working)
# requirements (not working)... links to other pages (not working)
# program events (not working)
# program apply (not working)
#program overview link (not working)


#elibility

#next steps

