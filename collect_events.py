
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Configure Chrome options to run in headless mode (optional)
chrome_options = Options()
chrome_options.add_argument("--headless")  # runs Chrome in headless mode

# Path to your chromedriver (ensure chromedriver is installed and in your PATH)
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the page
driver.get("https://urlbuilder.calendar.duke.edu/")

# Wait for the page to load completely.
# You can adjust the sleep duration or use explicit waits for better control.
time.sleep(5)

# Get the full page HTML including dynamically loaded content
select_element = driver.find_element(By.ID, "groups")  # or whatever the real ID is
options = select_element.find_elements(By.TAG_NAME, "option")
group_names = [option.text for option in options]
with open("groups.txt", "w", encoding="utf-8") as f:
    for group_name in group_names:
        f.write(group_name + "\n")

# Get the full page HTML including dynamically loaded content
select_element = driver.find_element(By.ID, "categories")  # or whatever the real ID is
options = select_element.find_elements(By.TAG_NAME, "option")
category_names = [option.text for option in options]
with open("categories.txt", "w", encoding="utf-8") as f:
    for category_name in category_names:
        f.write(category_name + "\n")

# Always remember to quit the driver when done
driver.quit()