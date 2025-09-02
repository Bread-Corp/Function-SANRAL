# SANRAL Tender Processing Lambda Service

## 1. Overview
This service contains an AWS Lambda function responsible for scraping tender information from the South African National Roads Agency (SANRAL) portal. This service is unique within the project because it employs a two-step data retrieval process:
1. **API Call**: It first fetches a list of open tenders from a JSON API endpoint.
2. **Web Scraping**: For each tender in the list, it extracts a URL and then scrapes that URL to gather more detailed and accurate information.

The function processes this combined data, validates it against a defined data model, and then dispatches it to the central Amazon SQS queue for downstream processing.

## 2. Lambda Function (`lambda_function.py`)
The `lambda_handler` orchestrates the process:
1. **Fetch Initial Data**: It sends an HTTP GET request to the SANRAL JSON API to get a summary list of all open tenders.
2. **Error Handling**: It includes robust error handling for network issues and invalid API responses.
3. **Data Parsing (Delegation)**: It iterates through the list of tenders returned by the API. Each item (which is a list of data points) is passed to the `SanralTender` model's `from_api_response` method. This method contains all the complex logic for the secondary web scraping and data consolidation.
4. **Validation & Logging**: If a tender fails the complex validation and scraping process, it is skipped, and a warning is logged in CloudWatch.
5. **Batching**: Successfully processed tenders are grouped into batches of 10.
6. **Queueing**: Each batch is sent to the `AIQueue.fifo` SQS queue with a `MessageGroupId` of `SanralTenderScrape`.

## 3. Data Model (`models.py`)
The service uses a set of Python classes to define the structure of the tender data.

### `TenderBase` (Abstract Class)
This is the standard foundational class that defines the common attributes for any tender, ensuring consistency across all data sources.
-   **Core Attributes**: `title`, `description`, `source`, `published_date`, `closing_date`, `supporting_docs`, `tags`.

### `SanralTender` (Concrete Class)
This class inherits from `TenderBase` and adds fields specific to the data available from SANRAL. Its `from_api_response` method is the core of this service's logic. It performs HTML parsing (with BeautifulSoup), regex matching (for URLs and emails), and robust date parsing to build a complete tender object.
- **Inherited Attributes**: All attributes from `TenderBase`.
- **SANRAL-Specific Attributes**:
    - `tender_number`: The unique tender number.
    - `category`: The tender's category (e.g., "Consulting Engineering").
    - `region`: The geographical region for the tender.
    - `email`: A contact email address, extracted from the scraped text.
    - `full_notice_text`: The complete, cleaned text scraped from the tender notice.

### AI Tagging Initialization
As with the other services, the `tags` attribute is intentionally initialized as an empty list (`[]`) within the `from_api_response` method.

```
# From models.py
return cls(
    # ... other fields
    tags=[], # Initialize with an empty list for the AI service.
    # ... other fields
)

```

The SANRAL portal does not provide predefined tags. By setting this field to an empty list, we create a consistent data structure that the downstream AI service can use to generate and populate relevant tags.