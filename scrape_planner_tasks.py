"""
Scrape Microsoft Planner Tasks using browser automation
No API or admin permissions needed - just your login credentials
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_planner_tasks():
    """Scrape tasks from Microsoft Planner web interface"""

    print("="*70)
    print("MICROSOFT PLANNER TASKS SCRAPER")
    print("="*70)
    print("\nStarting browser...")

    # Set up Chrome driver
    options = webdriver.ChromeOptions()
    # Remove headless mode so you can see and interact with login
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # Navigate to Planner
        print("Opening Microsoft Planner...")
        driver.get('https://planner.microsoft.com')

        # Wait for login or main page to load
        print("\n" + "="*70)
        print("PLEASE LOG IN TO MICROSOFT 365 IN THE BROWSER")
        print("="*70)
        print("\nWaiting for you to log in...")
        print("(Script will continue automatically after login)")

        # Wait for the main Planner page to load (after login)
        # Looking for the plans container or hub title
        try:
            WebDriverWait(driver, 300).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test-id="planner-hub"]'))
            )
            print("\n✓ Login successful!")
        except:
            print("\n✓ Proceeding to scrape tasks...")

        time.sleep(3)

        # Get all tasks from the current view
        print("\nScraping tasks...")

        # Try to find task cards
        tasks = []

        # Method 1: Try to find task cards
        try:
            task_elements = driver.find_elements(By.CSS_SELECTOR, '[data-test-id*="task-card"]')

            if task_elements:
                print(f"\nFound {len(task_elements)} task card(s)\n")

                for idx, task_elem in enumerate(task_elements, 1):
                    try:
                        title = task_elem.find_element(By.CSS_SELECTOR, '[data-test-id="task-card-title"]').text

                        # Try to get other details
                        try:
                            bucket = task_elem.find_element(By.CSS_SELECTOR, '[data-test-id="task-card-bucket"]').text
                        except:
                            bucket = "Unknown Bucket"

                        tasks.append({
                            'title': title,
                            'bucket': bucket
                        })

                        print(f"{idx}. {title}")
                        print(f"   Bucket: {bucket}\n")
                    except Exception as e:
                        print(f"Could not parse task {idx}: {e}")
        except Exception as e:
            print(f"Method 1 failed: {e}")

        # Method 2: Try generic approach
        if not tasks:
            print("\nTrying alternative scraping method...")
            time.sleep(2)

            # Get page source and look for task data
            page_source = driver.page_source

            # Print some debug info
            print("\nPage title:", driver.title)

            # Try to find any divs that might contain tasks
            all_divs = driver.find_elements(By.TAG_NAME, 'div')
            print(f"Found {len(all_divs)} div elements")

            # Look for buttons or links that might be tasks
            buttons = driver.find_elements(By.TAG_NAME, 'button')
            links = driver.find_elements(By.TAG_NAME, 'a')

            print(f"Found {len(buttons)} buttons and {len(links)} links")

            # Print first few button texts to see what we're working with
            print("\nSample button texts:")
            for btn in buttons[:10]:
                text = btn.text.strip()
                if text:
                    print(f"  - {text}")

        if not tasks:
            print("\n⚠ Could not automatically extract tasks")
            print("This might be due to Planner's dynamic UI structure")
            print("\nThe browser window is still open - you can manually view your tasks there")
            print("Press ENTER when you're done viewing...")
            input()
        else:
            print(f"\n{'='*70}")
            print(f"✓ TOTAL: {len(tasks)} task(s) found")
            print(f"{'='*70}")

            print("\nPress ENTER to close browser...")
            input()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\nClosing browser...")
        driver.quit()
        print("✓ Done")

if __name__ == "__main__":
    scrape_planner_tasks()
