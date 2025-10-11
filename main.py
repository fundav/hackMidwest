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
USDA.navigate_to("https://www.rd.usda.gov/programs-services/all-programs")
state_links = USDA.find_elements(By.CSS_SELECTOR, "html.js body.path--programs-services.path-programs-services.context-programs-services-all-programs.with-sidebar div.dialog-off-canvas-main-canvas main#main-content.usa-section.uswds-main-content-wrapper div.grid-container div.grid-row div.tablet---grid-col-9.usa-layout__content div div.region.region-content div#block-usda-rd-uswds-2-content--2.block.block-system.block-system-main-block div.views-element-container div.programs-list.view.view-programs.view-id-programs.view-display-id-page_1.js-view-dom-id-8efb7b7d0ab9bd2ee0aec6b8bb654191253b1ff04b0fdd8c12ae5b60d64d8aa4 div.view-header div.view.view-state-group-jumper.view-id-state_group_jumper.view-display-id-state_group_jump_menu_block.js-view-dom-id-0518d1884fc2a9bbf46524e45d87742ec326f7b6b7a8c6da8c24a9c262f203fe div.view-content div select#state-group-jumper-state-group-jump-menu-block-jump-menu.form-select.usa-select.ViewsJumpMenu.js-viewsJumpMenu option")
for i in state_links:
    i = i.text
print(state_links)