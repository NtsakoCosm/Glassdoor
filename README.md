# Glassdoor Job Scraper

This project is an asynchronous web scraper built with Python and Playwright. It is designed to scrape job listing details from Glassdoor by navigating to specified job search pages, scrolling through listings, and extracting relevant job details such as title, company name, location, salary estimate, and job description. The scraped data is saved in a JSON file (`job_listing.json`).

## Features

- **Asynchronous Operations:** Uses Python's `asyncio` for non-blocking I/O operations.
- **Browser Automation:** Leverages Playwright (via `async_playwright`) for interacting with web pages.
- **Dynamic Scrolling and Interaction:** Scrolls through pages, simulates mouse movements, and clicks on job listings dynamically.
- **Data Extraction:** Scrapes and extracts details including job title, company name, location, salary estimates, and job descriptions.
- **Concurrency:** Implements multi-threading with thread locks to ensure safe concurrent data writes.

## Prerequisites

- Python 3.7 or higher
- [Playwright for Python](https://playwright.dev/python/docs/intro)
- [patchright.async_api](#) (Ensure this module is installed or available in your environment)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/NtsakoCosm/glassdoor.git
   cd glassdoor
