# AI-Powered Lead Generation and Outreach Agent

This tool automatically analyzes business websites, identifies potential leads, and generates personalized outreach emails.

## Features

- **Website Scraping**: Extracts key business information from any website
- **AI Analysis**: Identifies business type and potential lead categories
- **Lead Generation**: Creates synthetic leads based on business analysis
- **Email Generation**: Crafts personalized outreach emails for each lead
- **Email Sending**: Optional capability to send emails directly (requires Gmail configuration)

## Tools Included

This project contains several tools to help with your lead generation process:

1. **Standard Lead Generation** (`app.py`): Main application that scrapes a website, analyzes it, and generates leads
2. **Custom Lead Generation** (`custom_lead_gen.py`): Allows more customization when analyzing websites and generating leads
3. **Email Testing** (`test_email.py`): Test email generation and sending with your own lead data
4. **Lead Importing** (`import_leads.py`): Import leads from a CSV file and generate personalized emails
5. **Menu Interface** (`menu.py`): Easy-to-use menu that provides access to all the tools

## Setup

1. **Clone the repository**

2. **Create a virtual environment and activate it**

   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**

   ```
   playwright install
   ```

5. **Configure environment variables**
   Create a `.env` file in the project root with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GMAIL_USER=your_gmail_email
   GMAIL_PASSWORD=your_gmail_app_password
   ```
   Note: For Gmail, you need to use an App Password. See [Google Account Help](https://support.google.com/accounts/answer/185833) for instructions.

## Usage

Launch the menu interface for easy access to all tools:

```
python menu.py
```

Or run individual tools directly:

### Standard Lead Generation

```
python app.py
```

This will:

1. Prompt for a target website URL
2. Analyze the website to determine business type
3. Generate potential leads
4. Create personalized emails for each lead
5. Offer to send emails directly (optional)

### Custom Lead Generation

```
python custom_lead_gen.py
```

Enhanced version that:

1. Offers manual data entry or website analysis
2. Allows lead customization
3. Provides email preview and editing
4. Saves all leads and emails to the output directory

### Email Testing

```
python test_email.py
```

Test email generation with:

1. Your own business information
2. Custom or sample lead data
3. Email preview and editing
4. Optional sending to test recipients

### Import Leads from CSV

```
python import_leads.py
```

Import and process your own leads:

1. Create or use a CSV file with lead information
2. Generate personalized emails for each lead
3. Preview, edit, and optionally send emails
4. Batch process multiple leads at once

## Output

All tools save their output to the `output` directory:

- Lead information as JSON files
- Email content as text files
- Screenshots of websites (when available)
- Structured business data

## How It Works

1. **Website Scraping**: Uses BeautifulSoup for static sites and Playwright for JavaScript-heavy sites
2. **Data Extraction**: Parses website content to understand the business
3. **Business Analysis**: Uses AI to classify the business and identify potential lead types
4. **Lead Generation**: Creates synthetic leads that match the business needs
5. **Email Generation**: Crafts personalized emails highlighting specific benefits
6. **Output**: Saves all leads and emails to the `output` directory
7. **Email Sending**: Optionally sends emails via SMTP (Gmail)

## Customization

- Edit the prompts in `utils/lead_finder.py` to change email templates
- Modify `utils/scraper.py` to extract different website elements
- Update `utils/analyzer.py` to adjust business classification logic
- Customize the fallback leads in `utils/lead_finder.py` for different industries

## License

MIT

## Disclaimer

This tool is for educational purposes. Always comply with email regulations and respect recipients' privacy. Never use for spamming.
