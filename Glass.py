import asyncio
import datetime
import json
from threading import Lock
from  patchright.async_api import async_playwright,Page,Browser

PATTERNS = ["https://www.glassdoor.com/partner/jobListing.htm?"]
data = set()
dataListings = []
dataLock = Lock()
clicked_links = []


async def get_hovered_url(page, x, y):


    """
    Get the URL of the closest <a> element at the given mouse coordinates
    if it matches the specified patterns.
    """
    await page.wait_for_timeout(500)  # Wait for any hover effects to take place

    url = await page.evaluate("""
        ([x, y]) => {
            let elem = document.elementFromPoint(x, y);
            while (elem && elem.tagName !== 'A') {
                elem = elem.parentElement;  // Traverse up the DOM tree
            }
            return elem ? elem.href : null;  // Return the URL if an <a> element is found
        }
    """, [x, y])

    if url and any(url.startswith(pattern) for pattern in PATTERNS):
        return url
    return None

async def scroll(page,x,y,delay):

    await page.evaluate(f"window.scrollTo({x},{y})")

async def scroll_and_scrape(page: Page, x=170, y=121, step=250, delay=0.1, now=None):
   
    # Define a list of positions to query around the base coordinate.
    # You can adjust the offsets as needed.
    positions = [(x + dx, y + dy) for dx in range(-50, 50, 10) for dy in range(-50, 50, 10)]

    
    while True:
        # Get current scroll information.
        scrollY = await page.evaluate("() => window.scrollY")
        innerHeight = await page.evaluate("() => window.innerHeight")
        scrollHeight = await page.evaluate("() => document.body.scrollHeight")
        
        # Stop if near the bottom.
        if scrollY + innerHeight >= scrollHeight:
            print("Reached bottom of the page without finding a new valid link.")
            modal = await page.locator(".actionBarMt0").is_visible()
            if modal :
                await page.locator(".CloseButton").click()
            
            try:
                await page.locator(".ShowMoreCTA_spacing-md__bS21L").click(timeout=500)
            except:
                pass
            await page.locator("[data-test='load-more']").hover()
            await page.locator("[data-test='load-more']").click(force=True)
            break
        
        # Query multiple positions for hovered links.
        hovered_links = await page.evaluate('''(positions) => {
            return positions.map(([x, y]) => {
                const el = document.elementFromPoint(x, y);
                const url = el ? el.closest('a')?.href : null;
                return {url: url, x: x, y: y};
            });
        }''', positions)
        
        # Iterate over each returned link and process if it meets the criteria.
        
        for link_info in hovered_links:
            url = link_info.get('url')
            if url and any(url.startswith(pattern) for pattern in PATTERNS):
                if url in clicked_links:
                    continue
                
                await page.mouse.click(link_info['x'], link_info['y'])
                #Close New tab
                newPage=None
                try:
                    newPage = await page.wait_for_event("popup",timeout=500)
                except:
                    pass
                if newPage:
                    await newPage.close()
                    
                        
                clicked_links.append(url)
                await asyncio.sleep(0.5)
                
            
                await scrape(page=page, now=now)
                break  # Process only one new link per scroll step
        
        # Scroll down by the specified step and reposition the mouse to the base position.
        await page.evaluate(f"() => window.scrollBy(0, {step})")
        await page.mouse.move(x, y)
        await asyncio.sleep(delay)
    
    return None

async def scrape(page:Page,now):
    modal = await page.locator(".actionBarMt0").is_visible()
    if modal :
        await page.locator(".CloseButton").click()
    
    try:
        await page.locator(".ShowMoreCTA_spacing-md__bS21L").click(timeout=500)
    except:
        pass
    
    employerDetails= await page.locator('[class *="JobDetails_jobDetailsHeader__"]').inner_text()
    employerDetails = employerDetails.split("\n")
    title = await page.locator(".heading_Level1__soLZs").inner_text()
    location = await page.locator('.JobDetails_location__mSg5h').inner_text()
    description = await page.locator("div+ .Section_bottomMargin__Fka0J").inner_text()
    try :
        salaryEst = await page.locator(".SalaryEstimate_salaryRange__brHFy").inner_text(timeout=500)
    except:
        salaryEst = "None"
    #print(details)
    companyName = employerDetails[0]
    
    print(description)
    print(title)
    print(location)
    print(salaryEst)
    print(f"Company name - {companyName}")

    
    listing = {
        "title":title,
        "Company_name": companyName,
        "location":location,
        "salaryEst":salaryEst,
        "description":description,
        

    }
    
    
    
    with dataLock:
        if frozenset(listing.items()) not in data:
            data.add(frozenset(listing.items()))
            dataListings.append(listing)

            print(data.__len__())
            scrapetime = datetime.datetime.now()
            elapsed = scrapetime-now
            print(elapsed)
            print("-"*200)
            
     
        

async def glassScraper(url,now,browser:Browser):
    context = await browser.new_context()
    page = await context.new_page()
    page.set_default_timeout(31536000)
    
    await page.goto(url)
    await asyncio.sleep(1)
    
    for ii in range(1,60):
            await scroll_and_scrape(page=page,now=now)
            
    await asyncio.sleep(5)
    await browser.close()

async def main():
    now = datetime.datetime.now()
    async with async_playwright() as p:
       
        browser =  await p.chromium.launch(
            channel="chrome",                   
            headless=False,
   
        )
        #Multi Scraping Setup, The urls are split into multiple salary ranges to scrape more job listings eg New York jobs 
        urls = [ 
            

            ("https://www.glassdoor.com/Job/new-york-jobs-SRCH_IL.0,8_IC1132348.htm?maxSalary=35000&minSalary=15000",now,browser),
            #("https://www.glassdoor.com/Job/new-york-jobs-SRCH_IL.0,8_IC1132348.htm?maxSalary=55000&minSalary=35000",now,browser)
            #("https://www.glassdoor.com/Job/new-york-jobs-SRCH_IL.0,8_IC1132348.htm?maxSalary=95000&minSalary=75000",now,browser),
            
            
            
            
            
            ]
        
        tasks = [asyncio.create_task(glassScraper(*arg)) for arg in urls]
        await asyncio.gather(*tasks)
        
        with open("job_listing.json", "w") as file:
            json.dump(dataListings, file, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
                        
