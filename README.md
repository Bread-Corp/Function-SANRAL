# 🛣️ SANRAL Tender Processing Lambda Service

[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)
[![Amazon SQS](https://img.shields.io/badge/AWS-SQS-yellow.svg)](https://aws.amazon.com/sqs/)
[![SANRAL API](https://img.shields.io/badge/API-SANRAL-green.svg)](https://www.nra.co.za/)
[![BeautifulSoup](https://img.shields.io/badge/Scraping-BeautifulSoup-orange.svg)](https://www.crummy.com/software/BeautifulSoup/)

**Building the highways to prosperity, one tender at a time!** 🛤️ This AWS Lambda service is the road engineering powerhouse of our tender scraping fleet - one of five specialized crawlers that captures opportunities from South Africa's premier road infrastructure agency. From massive freeway construction to bridge maintenance, we pave the way to every opportunity! 🌉

## 📚 Table of Contents

- [🎯 Overview](#-overview)
- [🛣️ Lambda Function (lambda_function.py)](#️-lambda-function-lambda_functionpy)
- [📊 Data Model (models.py)](#-data-model-modelspy)
- [🏷️ AI Tagging Initialization](#️-ai-tagging-initialization)
- [📋 Example Tender Data](#-example-tender-data)
- [🚀 Getting Started](#-getting-started)
- [📦 Deployment](#-deployment)
- [🧰 Troubleshooting](#-troubleshooting)

## 🎯 Overview

Welcome to the highway to opportunity! 🚗 This service is your express lane into SANRAL's vast road infrastructure ecosystem, capturing multi-billion rand highway projects, bridge constructions, geotechnical investigations, and critical maintenance contracts that keep South Africa's road network world-class! 🌍

**What makes it build better roads?** 🏗️
- 🛣️ **Road Infrastructure Expertise**: Specialized in highways, bridges, interchanges, and road maintenance
- 🔍 **Dual-Mode Intelligence**: Unique two-step process combining API calls with intelligent web scraping
- 🌍 **National Coverage**: From Cape Town's coastal routes to Johannesburg's highway networks
- 🎯 **Engineering Precision**: Captures complex geotechnical, consulting, and construction opportunities

## 🛣️ Lambda Function (`lambda_function.py`)

The highway engineering brain of our operation! 🧠 The `lambda_handler` orchestrates our sophisticated dual-phase extraction process:

### 🔄 The Road Construction Journey:

1. **🌐 Initial Reconnaissance**: Connects to the SANRAL JSON API to get the construction site survey - a comprehensive list of all open tenders across South Africa's road network.

2. **🛡️ Highway-Grade Error Handling**: Built like a reinforced bridge! Handles network construction zones, API maintenance periods, and response detours with civil engineering precision. Always finds an alternate route! 🚧

3. **🔍 Deep Excavation Phase**: Here's where we get serious! For each tender opportunity, we don't just scrape the surface - we conduct a full geotechnical investigation:
   - **Phase 1**: Extract the tender URL from the API response
   - **Phase 2**: Deploy our web scraping bulldozers (BeautifulSoup) to excavate detailed information from each tender page
   - **Phase 3**: Consolidate surface data with deep-drill information for complete tender profiles

4. **⚙️ Civil Engineering Validation**: Each tender goes through our rigorous `SanralTender` model with specialized logic for HTML parsing, regex pattern matching for emails and URLs, and robust date parsing that handles SANRAL's construction timelines.

5. **✅ Quality Assurance Inspector**: Our validation process ensures only structurally sound tenders make it through. Failed excavations get logged and marked for review - no unstable foundations in our pipeline! 🔨

6. **📦 Highway Batching**: Valid tenders are efficiently organized into construction batches of 10 messages - optimized for maximum SQS throughput like a well-planned highway interchange.

7. **🚀 Express Lane Delivery**: Each batch travels the fast lane to the central `AIQueue.fifo` SQS queue with the unique `MessageGroupId` of `SanralTenderScrape`. This keeps our road infrastructure tenders organized and maintains perfect traffic flow.

## 📊 Data Model (`models.py`)

Our data architecture is engineered for highway-grade performance! 🏗️

### `TenderBase` **(The Road Foundation)** 🛤️
The solid foundation that supports all our tender infrastructure! This abstract class defines the core roadway that connects all construction opportunities:

**🔧 Core Attributes:**
- `title`: The project blueprint - what road infrastructure is being built?
- `description`: Detailed engineering specifications and construction requirements
- `source`: Always "SANRAL" for this highway construction specialist
- `published_date`: When this construction project broke ground
- `closing_date`: Bid submission deadline - when the construction gate closes! ⏰
- `supporting_docs`: Critical engineering drawings and specifications
- `tags`: Keywords for AI intelligence (starts empty, gets surveyed by our AI service)

### `SanralTender` **(The Highway Engineer)** 🛣️
This engineering powerhouse inherits all the foundational strength from `TenderBase` and adds SANRAL's unique highway construction features:

**🏗️ SANRAL-Specific Attributes:**
- `tender_number`: Official SANRAL project code (e.g., "SUB-CONTRACT SANRAL N.001-250-2024/1D-SS")
- `category`: Type of construction project (e.g., "Other Projects", "Consulting Engineering")
- `region`: Which regional office manages this highway (e.g., "Northern Region", "Western Cape")
- `email`: Direct line to the project engineer (extracted via intelligent web scraping)
- `full_notice_text`: Complete construction notice with all technical specifications and requirements

**🔍 Advanced Engineering Process:**
The `from_api_response` method is our master civil engineer! It performs:
- **HTML Excavation**: BeautifulSoup-powered deep drilling into tender pages
- **Regex Survey**: Pattern matching for emails, URLs, and technical specifications
- **Date Engineering**: Robust parsing of construction timelines and deadlines

## 🏷️ AI Tagging Initialization

We're all about intelligent highway planning! 🤖 Every tender that travels through our system is perfectly prepared for downstream AI enhancement:

```python
# From models.py - Preparing for AI highway classification! 🛣️
return cls(
    # ... other fields
    tags=[],  # Initialize tags as an empty list, ready for the AI service.
    # ... other fields
)
```

This ensures **seamless highway integration** with our AI pipeline - every tender object arrives with a clean, empty `tags` field just waiting to be surveyed with intelligent categorizations! 🧠🛤️

## 📋 Example Tender Data

Here's what a real SANRAL highway project looks like after our scraper works its construction magic! 🎩✨

```json
{
  "title": "Sub-Contract Sanral N.001-250-2024/1D-Ss",
  "description": "For Geotechnical Investigation Including Test Pitting, Laboratory Testing And Rotary Core Drilling For The Upgrading Of National Route 1 Section 25 From Modimolle Interchange (Km 0.0) To Tobias Zyn Loop (Km 30.0)  Sub-Contract Sanral N.001-250-2024/1D-Ss",
  "source": "SANRAL",
  "publishedDate": "2025-09-26T00:00:00",
  "closingDate": "2025-10-17T11:00:00",
  "supporting_docs": [
    {
      "name": "Tender Details",
      "url": "https://www.nra.co.za/open-tenders/sub-contract-sanral-n-001-250-2024-1d-ss"
    }
  ],
  "tags": [],
  "tenderNumber": "SUB-CONTRACT SANRAL N.001-250-2024/1D-SS",
  "category": "Other Projects",
  "region": "Northern Region",
  "email": "",
  "fullNoticeText": "Tender Notice And Invitation To Tender (Incorporating Sbd1) The South African National Roads Agency Soc Limited (Sanral) On Behalf Of Zutari (Pty) Ltd Invites Suitably Qualified Tenderers For Sanral N.001-250-2024/1D-Ss Geotechnical Investigation Including Test Pitting, Laboratory Testing And Rotary Core Drilling For The Upgrading Of National Route 1 Section 25 From Modimolle Interchange (Km 0.0) To Tobias Zyn Loop (Km 30.0 ). This Project Is In The Province Of Limpopo And In The District Municipality Of Waterberg And Local Municipality Of Modimolle–Mookgophong. The Approximate Duration Is 4.5 Months..."
}
```

**🛣️ What this highway project delivers:**
- 🏗️ **Major Highway Upgrade**: National Route 1 enhancement project in Limpopo
- 🔍 **Geotechnical Engineering**: Comprehensive soil investigation with core drilling
- 📏 **Strategic Corridor**: 30km stretch from Modimolle Interchange to Tobias Zyn Loop
- ⏰ **Fast-Track Timeline**: 4.5-month engineering investigation period
- 🌍 **Regional Impact**: Critical infrastructure for Waterberg District transportation
- 🎯 **Professional Opportunity**: Sub-contract through established engineering firm Zutari

## 🚀 Getting Started

Ready to build the highway to success? Let's lay the foundation! 🏗️

### 📋 Prerequisites
- AWS CLI configured with appropriate credentials 🔑
- Python 3.9+ with pip 🐍
- BeautifulSoup4 for web scraping capabilities 🔍
- Access to AWS Lambda and SQS services ☁️
- Understanding of civil engineering and road construction terminology 🛣️

### 🔧 Local Development
1. **📁 Clone the repository**
2. **📦 Install dependencies**: `pip install -r requirements.txt`
3. **🧪 Run tests**: `python -m pytest`
4. **🔍 Test locally**: Use AWS SAM for local Lambda simulation

## 📦 Deployment

### 🚀 Highway Express Deploy
1. **📁 Package**: Bundle your code and dependencies like construction materials
2. **⬆️ Upload**: Deploy to AWS Lambda with highway-grade settings
3. **⚙️ Configure**: Set up CloudWatch Events for scheduled construction runs
4. **🎯 Test**: Trigger manually to verify highway connection

### 🔧 Environment Variables
- `SQS_QUEUE_URL`: Target queue for processed highway tenders
- `API_TIMEOUT`: Request timeout for SANRAL API calls
- `SCRAPING_TIMEOUT`: Timeout for web scraping operations
- `BATCH_SIZE`: Number of tenders per SQS construction batch (default: 10)

## 🧰 Troubleshooting

### 🚨 Highway Construction Challenges

<details>
<summary><strong>Web Scraping Timeouts</strong></summary>

**Issue**: BeautifulSoup operations timing out on complex SANRAL tender pages.

**Solution**: SANRAL tender pages can be engineering document-heavy! Increase scraping timeouts and implement intelligent content parsing that focuses on key data sections. Sometimes you need to excavate carefully! 🔍

</details>

<details>
<summary><strong>HTML Structure Changes</strong></summary>

**Issue**: SANRAL website updates breaking the scraping logic.

**Solution**: Highway maintenance never stops! Monitor for HTML structure changes and update your scraping selectors accordingly. Keep your web scraping tools as current as road maintenance! 🛠️

</details>

<details>
<summary><strong>Dual-Phase Processing Failures</strong></summary>

**Issue**: API call succeeds but web scraping phase fails.

**Solution**: Implement robust fallback logic. If detailed scraping fails, ensure you can still process basic tender information from the API. A partial highway is better than no highway! 🚧

</details>

<details>
<summary><strong>Engineering Document Processing</strong></summary>

**Issue**: Complex technical documents causing parsing failures.

**Solution**: SANRAL deals in serious civil engineering! Update your parsing logic to handle technical specifications, engineering drawings references, and construction terminology. Build your parser like you'd build a bridge - to last! 🌉

</details>

<details>
<summary><strong>Regional Data Variations</strong></summary>

**Issue**: Different regional offices formatting data differently.

**Solution**: SANRAL operates across diverse regions with varying formatting standards. Implement flexible parsing that can handle Northern Region, Western Cape, and other regional variations! 🌍

</details>

---

> Built with love, bread, and code by **Bread Corporation** 🦆❤️💻
