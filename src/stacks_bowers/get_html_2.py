import base64
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://auctions.stacksbowers.com/auctions/3-1LCJJA/december-2025-showcase-auction-session-1-the-james-a-stack-sr-collection-part-i-silver-dollars-double-eagles-lots-20001-20054?limit=96&jump_to_lot=20001")

# Use Chrome DevTools directly
snapshot = driver.execute_cdp_cmd("Page.captureSnapshot", {})

with open("page.mhtml", "w", encoding="utf-8") as f:
    f.write(snapshot["data"])

driver.quit()
