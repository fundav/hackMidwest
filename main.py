# #Main source code
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
from scrapFromUSDA import WebAutomator
from selenium.webdriver.common.by import By

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