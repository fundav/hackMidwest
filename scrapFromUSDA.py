from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from typing import Optional, List
import time

class WebAutomator:
    """
    A utility class to handle common Selenium automation tasks.
    """
    
    def __init__(self, headless: bool = False, browser: str = 'firefox'):
        """
        Initializes the WebDriver instance.
        
        Args:
            headless (bool): If True, runs the browser without a visible GUI.
            browser (str): The browser to use ('firefox' or 'chrome').
        """
        self.driver: Optional[RemoteWebDriver] = None
        self.browser_type = browser.lower()
        self.headless = headless
        
        print(f"Setting up {self.browser_type} WebDriver (Headless: {self.headless})...")
        self._setup_driver()

    def _setup_driver(self):
        """Initializes the specified browser driver."""
        if self.browser_type == 'firefox':
            options = FirefoxOptions()
            if self.headless:
                options.add_argument('-headless')
            self.driver = webdriver.Firefox(options=options)
        elif self.browser_type == 'chrome':
            options = ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')  # Recommended for Linux environments
                options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=options)
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}. Use 'firefox' or 'chrome'.")

    # --------------------------------------------------------------------------
    # 1. Navigation and Page State Management
    # --------------------------------------------------------------------------

    def navigate_to(self, url: str):
        """Navigates the browser to a specific URL."""
        if self.driver:
            print(f"Navigating to: {url}")
            self.driver.get(url)

    def add_browser_cookie(self, name: str, value: str, **kwargs):
        """Adds a cookie to the current browser session."""
        if self.driver:
            cookie = {"name": name, "value": value}
            cookie.update(kwargs)
            print(f"Adding cookie: {name}...")
            self.driver.add_cookie(cookie)
            
    def reload_page(self):
        """Reloads the current page."""
        if self.driver:
            self.driver.refresh()
            print("Page reloaded.")

    # --------------------------------------------------------------------------
    # 2. Locating and Interacting with Elements
    # --------------------------------------------------------------------------
    
    def find_element(self, by: By, value: str):
        """Locates and returns a single element using a specified locator strategy."""
        if self.driver:
            try:
                return self.driver.find_element(by, value)
            except Exception as e:
                # Optionally log the error, but return None to continue script execution
                # print(f"Error finding element (By={by}, Value='{value}'): {e}")
                return None
        return None
    
    def find_elements(self, by: By, value: str) -> List:
        """Locates and returns a list of elements using a specified locator strategy."""
        if self.driver:
            try:
                return self.driver.find_elements(by, value)
            except Exception as e:
                print(f"Error finding elements (By={by}, Value='{value}'): {e}")
                return []
        return []

    def get_attribute(self, element, attribute_name: str) -> str:
        """Retrieves the value of a specified attribute from an element."""
        if element:
            return element.get_attribute(attribute_name)
        return ""

    def send_keys(self, element, text: str):
        """Sends keys (inputs text) to a target element."""
        if element:
            element.send_keys(text)
            
    def click_element(self, element):
        """Clicks a target element."""
        if element:
            element.click()
            
    # --------------------------------------------------------------------------
    # 3. Utility and Cleanup
    # --------------------------------------------------------------------------

    def take_screenshot(self, file_path: str):
        """Captures a screenshot of the current browser window."""
        if self.driver:
            try:
                self.driver.save_screenshot(file_path)
                print(f"Screenshot saved to: {file_path}")
            except Exception as e:
                print(f"Error taking screenshot: {e}")

    def wait(self, seconds: float):
        """Pauses the script execution for a specified number of seconds."""
        time.sleep(seconds)

    def close_driver(self):
        """Closes the current browser window/tab."""
        if self.driver:
            self.driver.quit()  # Use quit() to close all associated windows and gracefully end the session
            print("Driver session quit.")

# --------------------------------------------------------------------------
# Example Usage (Demonstrates how to use the general-purpose class)
# --------------------------------------------------------------------------

if __name__ == '__main__':
    # Usage Example: Scraping a public Google page (e.g., Google's main page)
    # NOTE: You must have the appropriate WebDriver (e.g., geckodriver for Firefox) 
    # installed and configured in your system PATH or use WebDriverManager.
    
    try:
        # 1. Setup: Initialize for Chrome, running in headless mode
        # Change 'chrome' to 'firefox' if preferred
        automator = WebAutomator(headless=True, browser='chrome') 

        # 2. Navigation
        automator.navigate_to("https://www.google.com")
        automator.wait(2) # Wait for page load

        # 3. Locating and Interacting (Search for 'Selenium WebDriver')
        # Google search box usually has name="q" or is locatable by tag/class
        search_box = automator.find_element(By.NAME, "q") 
        
        if search_box:
            search_query = "Selenium WebDriver"
            automator.send_keys(search_box, search_query)
            automator.send_keys(search_box, u'\ue007') # Send the ENTER key
            automator.wait(3)

            # 4. Utility (Take a screenshot of the search results)
            automator.take_screenshot("google_search_results.png")

        else:
            print("Could not find the search box element.")

    except Exception as e:
        print(f"An error occurred during the automation process: {e}")

    finally:
        # 5. Cleanup
        automator.close_driver()