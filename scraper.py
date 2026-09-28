import asyncio
import random
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import urllib.parse

class LinkedInScraper:
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search"

    async def scrape_jobs(self, keywords: str, location: str = "Worldwide", max_jobs: int = 10, log_cb=None):
        def log(msg):
            print(msg)
            if log_cb:
                log_cb(msg)

        jobs_data = []
        
        async with async_playwright() as p:
            # We use non-headless or headless=False to avoid detection easily. 
            # For a UI experience we can run headless=True but it's riskier. Let's start with headless=True but with stealth.
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await Stealth().apply_stealth_async(page)
            
            # Construct URL
            params = {
                "keywords": keywords,
                "location": location,
                "f_TPR": "r2592000", # Past month
                "sortBy": "DD" # Most recent
            }
            url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
            log(f"Navigating to {url}")
            
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(3, 6))
            
            # Scroll to load jobs
            log("Scrolling to load more jobs...")
            for _ in range(5):
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await asyncio.sleep(random.uniform(1, 3))
                
            # Extract job cards
            job_cards = await page.query_selector_all("ul.jobs-search__results-list > li")
            log(f"Found {len(job_cards)} job cards on main page.")
            
            for card in job_cards[:max_jobs]:
                try:
                    title_elem = await card.query_selector("h3.base-search-card__title")
                    company_elem = await card.query_selector("h4.base-search-card__subtitle")
                    link_elem = await card.query_selector("a.base-card__full-link")
                    
                    if not title_elem or not link_elem:
                        continue
                        
                    title = (await title_elem.inner_text()).strip()
                    company = (await company_elem.inner_text()).strip() if company_elem else "Unknown"
                    job_url = await link_elem.get_attribute("href")
                    
                    # Clean URL
                    job_url = job_url.split("?")[0]
                    
                    jobs_data.append({
                        "title": title,
                        "company": company,
                        "url": job_url,
                        "description": ""
                    })
                except Exception as e:
                    log(f"Error extracting job card: {e}")
            
            # Now fetch descriptions for each job
            total_jobs = len(jobs_data)
            for idx, job in enumerate(jobs_data):
                log(f"Extracting description {idx+1}/{total_jobs}: {job['title']}")
                try:
                    await page.goto(job["url"], wait_until="domcontentloaded")
                    await asyncio.sleep(random.uniform(2, 5))
                    
                    # Click "Show more" button if it exists
                    try:
                        show_more = await page.wait_for_selector("button.show-more-less-html__button", timeout=3000)
                        if show_more:
                            await show_more.click()
                            await asyncio.sleep(random.uniform(1, 2))
                    except:
                        pass # Button might not be there
                        
                    desc_elem = await page.query_selector("div.show-more-less-html__markup")
                    if desc_elem:
                        job["description"] = (await desc_elem.inner_text()).strip()
                    else:
                        log(f"Description not found for {job['url']}")
                except Exception as e:
                    log(f"Error fetching description for {job['url']}: {e}")
                    
            await browser.close()
            
        return jobs_data
