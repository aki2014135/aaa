# Plan: Scrape Yahoo Auction Data to Google Sheets

## 1. Scope and Assumptions
- Target a single Yahoo Auctions Japan listing URL (e.g., https://page.auctions.yahoo.co.jp/...).
- Extract core details: title, current price, buyout price (if available), number of bids, time remaining, seller name, and item description summary.
- Store extracted data as a row in a Google Sheet, appending new rows for each scrape.
- Use Python 3 with `requests`, `beautifulsoup4`, and `gspread` (Google Sheets API) libraries.
- Authentication to Google Sheets will leverage a service account credentials JSON.

## 2. Environment Setup
1. Create and activate a Python virtual environment.
2. Install required dependencies:
   ```bash
   pip install requests beautifulsoup4 lxml gspread google-auth
   ```
3. Store the Google service account JSON file securely (not committed to version control).
4. Share the target Google Sheet with the service account email.

## 3. Data Extraction Workflow
1. Accept the Yahoo Auction URL as an input parameter or command-line argument.
2. Perform an HTTP GET request to retrieve the listing page HTML.
3. Parse the HTML with BeautifulSoup using the `lxml` parser for robustness.
4. Extract fields using CSS selectors / element IDs:
   - Title: `h1` with class `ProductTitle__text`.
   - Current price: span with data-testid `current-price` (fallback to alternative selectors).
   - Buyout price: check for elements with text `即決` ("Buy It Now") and capture associated price.
   - Number of bids: element with `ProductDetail__bid` or similar label.
   - Time remaining: element near label `残り時間`.
   - Seller name: anchor tag within seller info section.
   - Description summary: text content from `ProductExplanation` section (truncate or clean whitespace).
5. Normalize and clean extracted text (strip whitespace, convert price to numeric by removing yen symbols and commas).
6. Handle missing data by substituting `None` or blank strings.

## 4. Google Sheets Integration
1. Use `gspread.service_account(filename="path/to/credentials.json")` to authenticate.
2. Open the target spreadsheet by name or key.
3. Determine target worksheet (default first sheet or specified).
4. Append a row with ordered data fields `[timestamp_utc, url, title, current_price, buyout_price, bid_count, time_remaining, seller, description]`.

## 5. Script Structure (`scrape_yahoo_auction.py`)
- `parse_args()`: CLI parsing for URL, sheet name, worksheet name, credentials path.
- `fetch_listing(url)`: returns HTML content (with error handling, retries, and user-agent header).
- `parse_listing(html)`: extracts data and returns a dict.
- `append_to_sheet(data, sheet_name, worksheet, creds_path)`: handles Google Sheets write.
- `main()`: orchestrates flow; logs progress and handles exceptions.

## 6. Testing Strategy
- Use `pytest` with `requests-mock` or recorded HTML fixtures to test `parse_listing` logic without live HTTP calls.
- Mock gspread interactions to validate `append_to_sheet` behavior.
- Add a dry-run mode that prints parsed data without writing to Sheets for manual verification.

## 7. Operational Considerations
- Implement rate limiting / sleep if scraping multiple URLs to respect Yahoo terms.
- Monitor for HTML structure changes; encapsulate selectors in constants for easier updates.
- Store sensitive credentials outside repo and reference via environment variable.
- Consider deploying as a scheduled job (e.g., GitHub Actions, cron, or cloud function) if recurring scrapes are needed.

## 8. Future Enhancements
- Support scraping multiple URLs from a list or CSV.
- Capture additional metadata (image URLs, category, shipping costs).
- Provide a Google Sheets-to-CSV export or integration with Google Data Studio.
- Integrate error notifications (Slack/email) for failed scrapes.

