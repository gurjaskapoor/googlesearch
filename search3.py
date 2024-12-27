from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time
from rich.console import Console
from rich.table import Table

# Function to perform the Google News search
def google_news_search(query, max_results=10):
    # Automatically installs the correct version of chromedriver
    chromedriver_autoinstaller.install()

    # Setting up Chrome options for headless operation
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.100 Safari/537.36")

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")

    # Handle cookie consent
    try:
        consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'I agree') or contains(text(), 'Accept all') or contains(text(), 'Got it')]"))
        )
        consent_button.click()
        print("[INFO] Cookie consent accepted.")
    except Exception as e:
        print("[INFO] No cookie consent button found or timeout occurred.")
    
    # Search query with 'news' appended
    search_query = f"{query} news"
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    search_bar.send_keys(search_query)
    search_bar.send_keys(Keys.RETURN)

    # Wait until search results are loaded
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.g")))
    
    results = []
    result_elements = driver.find_elements(By.CSS_SELECTOR, "div.g")[:max_results]

    # Extract title, link, and description for each result
    for element in result_elements:
        try:
            title = element.find_element(By.CSS_SELECTOR, "h3").text if element.find_elements(By.CSS_SELECTOR, "h3") else "No Title"
            link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href") if element.find_elements(By.CSS_SELECTOR, "a") else "No Link"
            description = element.find_element(By.CSS_SELECTOR, "div.VwiC3b").text if element.find_elements(By.CSS_SELECTOR, "div.VwiC3b") else "No Description"
            results.append({
                "title": title,
                "link": link,
                "description": description
            })
        except Exception as e:
            print(f"[WARNING] Error extracting a result: {str(e)}")

    driver.quit()  # Always quit the driver at the end
    return results

# Function to display the results in a formatted table using 'rich'
def display_results(results):
    console = Console()
    table = Table(title="Google News Search Results")

    # Add table columns
    table.add_column("No.", justify="right", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Link", style="green")
    table.add_column("Description", style="white")

    # Add rows for each result
    for i, result in enumerate(results, start=1):
        table.add_row(
            str(i),
            result["title"],
            result["link"],
            result["description"]
        )

    # Print the table in the console
    console.print(table)

# Main entry point
if __name__ == "__main__":
    search_query = input("Enter your search query: ")
    max_results = int(input("Enter the maximum number of news results to extract: "))
    
    print("\n[INFO] Performing Google news search...\n")
    
    # Perform the search and get results
    search_results = google_news_search(search_query, max_results = max_results)
    
    # Display the results if any were found
    if search_results:
        display_results(search_results)
    else:
        print("[INFO] No results found.")