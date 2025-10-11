"""
selenium_utils.py

A reusable class containing the essential Selenium methods extracted from the 
Sudoku solver program (setup, navigation, interaction, and cleanup). 
This can be imported into new projects for web automation tasks.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

class WebAutomator:
    """
    A utility class to handle common Selenium automation tasks.
    """
    
    def __init__(self, headless=False, browser='firefox'):
        """
        Initializes the WebDriver instance with specified options.

        Args:
            headless (bool): If True, runs the browser without a visible GUI.
            browser (str): Specifies the browser to use ('firefox' is default).
        """
        self.driver: RemoteWebDriver = None
        self.browser_type = browser.lower()
        self.headless = headless
        
        print(f"Setting up {self.browser_type} WebDriver (Headless: {self.headless})...")
        self._setup_driver()

    def _setup_driver(self):
        """Initializes the specified browser driver."""
        if self.browser_type == 'firefox':
            options = Options()
            if self.headless:
                options.add_argument('-headless')
            # Add other common options here if needed
            # options.add_argument("--width=1500")
            # options.add_argument("--height=800")
            self.driver = webdriver.Firefox(options=options)
        elif self.browser_type == 'chrome':
            # You would use ChromeOptions and webdriver.Chrome() here
            # Example: from selenium.webdriver.chrome.options import Options as ChromeOptions
            print("Chrome setup not implemented in this snippet.")
        else:
            raise ValueError("Unsupported browser type.")

    # --------------------------------------------------------------------------
    # 2. Navigation and Page State Management
    # --------------------------------------------------------------------------

    def navigate_to(self, url: str):
        """Navigates the browser to a specific URL."""
        if self.driver:
            print(f"Navigating to: {url}")
            self.driver.get(url)

    def add_browser_cookie(self, name: str, value: str):
        """Adds a cookie to the current browser session."""
        if self.driver:
            print(f"Adding cookie: {name}={value}")
            self.driver.add_cookie({"name": name, "value": value})

    # --------------------------------------------------------------------------
    # 3. Locating and Interacting with Elements
    # --------------------------------------------------------------------------

    def find_element_by_id(self, element_id: str):
        """Locates and returns a single element using its ID."""
        if self.driver:
            try:
                return self.driver.find_element(By.ID, element_id)
            except Exception as e:
                print(f"Error finding element with ID '{element_id}': {e}")
                return None
        return None

    def get_element_value(self, element) -> str:
        """Retrieves the 'value' attribute of a given element."""
        if element:
            return element.get_attribute("value")
        return ""

    def input_text_by_id(self, element_id: str, text: str):
        """Locates an element by ID and sends keys (inputs text) to it."""
        element = self.find_element_by_id(element_id)
        if element:
            print(f"Sending keys '{text}' to element ID: {element_id}")
            element.send_keys(text)

    # --------------------------------------------------------------------------
    # 4. Utility and Cleanup
    # --------------------------------------------------------------------------

    def take_screenshot(self, file_path: str):
        """Captures a screenshot of the current browser window."""
        if self.driver:
            try:
                self.driver.save_screenshot(file_path)
                print(f"Screenshot saved to: {file_path}")
            except Exception as e:
                print(f"Error taking screenshot: {e}")

    def close_driver(self):
        """Closes the current browser window/tab."""
        if self.driver:
            self.driver.close()
            print("Driver closed.")

# --------------------------------------------------------------------------
# Example Usage (Demonstrates how to use the class methods)
# --------------------------------------------------------------------------

if __name__ == '__main__':
    # 1. Setup
    automator = WebAutomator(headless=True) # Set to True to run silently

    # 2. Navigation and Page State Management
    url = "https://www.brainbashers.com/showsudoku.asp?date=1123&diff=1"
    automator.navigate_to(url)
    automator.add_browser_cookie("DarkMode", "DarkModeOn")
    automator.navigate_to(url) # Reload to apply cookie

    # 3. Locating and Interacting with Elements (Example on the Sudoku grid)
    
    # Try to scrape the value of the first cell (A10)
    first_cell_id = "BBsudokuinputA11" 
    first_cell = automator.find_element_by_id(first_cell_id)
    if first_cell:
        current_value = automator.get_element_value(first_cell)
        print(f"Value in cell {first_cell_id}: '{current_value}'")
        
        # Example of inputting a solved number (e.g., if we solved for '9')
        # Note: If the cell is already filled, this will append the text.
        # automator.input_text_by_id(first_cell_id, '9') 

    # 4. Utility and Cleanup
    # automator.take_screenshot("example_screenshot.png")
    automator.close_driver()