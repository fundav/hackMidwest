#Main source code
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from scrapFromUSDA import WebAutomator
from selenium.webdriver.common.by import By

uri = "mongodb+srv://ander:TopicalSet24#@cluster0.kbzhtfw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)
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