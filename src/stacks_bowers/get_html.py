from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

url = "https://auctions.stacksbowers.com/auctions/3-1LCJJA/december-2025-showcase-auction-session-1-the-james-a-stack-sr-collection-part-i-silver-dollars-double-eagles-lots-20001-20054?limit=96"

options = Options()
# IMPORTANT: no headless for this test
options.add_argument(
    "--user-data-dir=/home/jared/.config/google-chrome"
)  # or chromium path
options.add_argument("--profile-directory=Profile 7")  # or "Profile 1" etc

driver = webdriver.Chrome(options=options)

try:
    driver.get(url)

    # Give it time to fully render; and explicitly wait for lot containers
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.lot-repeater"))
    )

    html = driver.page_source
    with open("stacks_bowers_profile.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Saved HTML to stacks_bowers_profile.html")

    # Pause so you can visually confirm in the real browser
    input("Check the browser window. Press Enter here when you see the lots...")

finally:
    driver.quit()
