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

This section covers three deployment methods for the SANRAL Tender Processing Lambda Service. Choose the method that best fits your workflow and infrastructure preferences.

### 🛠️ Prerequisites

Before deploying, ensure you have:
- AWS CLI configured with appropriate credentials 🔑
- AWS SAM CLI installed (`pip install aws-sam-cli`)
- Python 3.13 runtime support in your target region
- Access to AWS Lambda, SQS, and CloudWatch Logs services ☁️
- Required Python dependencies: `beautifulsoup4` and `requests`

### 🎯 Method 1: AWS Toolkit Deployment

Deploy directly through your IDE using the AWS Toolkit extension.

#### Setup Steps:
1. **Install AWS Toolkit** in your IDE (VS Code, IntelliJ, etc.)
2. **Configure AWS Profile** with your credentials
3. **Open Project** containing `lambda_function.py` and `models.py`

#### Deploy Process:
1. **Right-click** on `lambda_function.py` in your IDE
2. **Select** "Deploy Lambda Function" from AWS Toolkit menu
3. **Configure Deployment**:
   - Function Name: `SanralFunction`
   - Runtime: `python3.13`
   - Handler: `lambda_function.lambda_handler`
   - Memory: `128 MB`
   - Timeout: `120 seconds`
4. **Add Layers** manually after deployment:
   - beautifulsoup4-library layer
   - requests-library layer
5. **Set Environment Variables** as needed
6. **Configure IAM Permissions** for SQS, Logs, and EC2 (for VPC if needed)

#### Post-Deployment:
- Test the function using the AWS Toolkit test feature
- Monitor logs through CloudWatch integration
- Update function code directly from IDE for quick iterations

### 🚀 Method 2: SAM Deployment

Use AWS SAM for infrastructure-as-code deployment with the provided template.

#### Initial Setup:
```bash
# Install AWS SAM CLI
pip install aws-sam-cli

# Verify installation
sam --version
```

#### Create Required Layer Directories:
Since the template references layers not included in the repository, create them:

```bash
# Create layer directories
mkdir -p beautifulsoup4-library/python
mkdir -p requests-library/python

# Install beautifulsoup4 layer
pip install beautifulsoup4 -t beautifulsoup4-library/python/

# Install requests layer  
pip install requests -t requests-library/python/
```

#### Build and Deploy:
```bash
# Build the SAM application
sam build

# Deploy with guided configuration (first time)
sam deploy --guided

# Follow the prompts:
# Stack Name: sanral-lambda-stack
# AWS Region: us-east-1 (or your preferred region)
# Confirm changes before deploy: Y
# Allow SAM to create IAM roles: Y
# Save parameters to samconfig.toml: Y
```

#### Subsequent Deployments:
```bash
# Quick deployment after initial setup
sam build && sam deploy
```

#### Local Testing with SAM:
```bash
# Test function locally
sam local invoke SanralFunction

# Start local API Gateway (if needed)
sam local start-api
```

#### SAM Deployment Advantages:
- ✅ Complete infrastructure management
- ✅ Automatic layer creation and management
- ✅ IAM permissions defined in template
- ✅ Easy rollback capabilities
- ✅ CloudFormation integration

### 🔄 Method 3: Workflow Deployment (CI/CD)

Automated deployment using GitHub Actions workflow for production environments.

#### Setup Requirements:
1. **GitHub Repository Secrets**:
   ```
   AWS_ACCESS_KEY_ID: Your AWS access key
   AWS_SECRET_ACCESS_KEY: Your AWS secret key
   AWS_REGION: us-east-1 (or your target region)
   ```

2. **Pre-existing Lambda Function**: The workflow updates an existing function, so deploy initially using Method 1 or 2.

#### Deployment Process:
1. **Create Release Branch**:
   ```bash
   # Create and switch to release branch
   git checkout -b release
   
   # Make your changes to lambda_function.py or models.py
   # Commit changes
   git add .
   git commit -m "feat: update SANRAL tender processing logic"
   
   # Push to trigger deployment
   git push origin release
   ```

2. **Automatic Deployment**: The workflow will:
   - Checkout the code
   - Configure AWS credentials
   - Create deployment zip with `lambda_function.py` and `models.py`
   - Update the existing Lambda function code
   - Maintain existing configuration (layers, environment variables, etc.)

#### Manual Trigger:
You can also trigger deployment manually:
1. Go to **Actions** tab in your GitHub repository
2. Select **"Deploy Python Scraper to AWS"** workflow
3. Click **"Run workflow"**
4. Choose the `release` branch
5. Click **"Run workflow"** button

#### Workflow Deployment Advantages:
- ✅ Automated CI/CD pipeline
- ✅ Consistent deployment process
- ✅ Audit trail of deployments
- ✅ Easy rollback to previous commits
- ✅ No local environment dependencies

### 🔧 Post-Deployment Configuration

Regardless of deployment method, configure the following:

#### Environment Variables:
```bash
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/211635102441/AIQueue.fifo
API_TIMEOUT=30
SCRAPING_TIMEOUT=30
BATCH_SIZE=10
USER_AGENT=Mozilla/5.0 (compatible; SANRAL-Tender-Bot/1.0)
```

#### CloudWatch Events (Optional):
Set up scheduled execution:
```bash
# Create CloudWatch Events rule for daily execution
aws events put-rule \
    --name "SanralLambdaSchedule" \
    --schedule-expression "cron(0 9 * * ? *)" \
    --description "Daily SANRAL tender scraping"

# Add Lambda as target
aws events put-targets \
    --rule "SanralLambdaSchedule" \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:211635102441:function:SanralFunction"
```

### 🧪 Testing Your Deployment

After deployment, test the function:

```bash
# Test via AWS CLI
aws lambda invoke \
    --function-name SanralFunction \
    --payload '{}' \
    response.json

# Check the response
cat response.json
```

#### Expected Success Indicators:
- ✅ Function executes without errors
- ✅ CloudWatch logs show successful API calls and scraping activity
- ✅ SQS queue receives tender messages
- ✅ No timeout or memory errors
- ✅ Valid JSON tender data in queue messages

### 🔍 Monitoring and Maintenance

#### CloudWatch Metrics to Monitor:
- **Duration**: Function execution time
- **Error Rate**: Failed invocations
- **Memory Utilization**: RAM usage patterns
- **Throttles**: Concurrent execution limits

#### Log Analysis:
```bash
# View recent logs
aws logs tail /aws/lambda/SanralFunction --follow

# Search for errors
aws logs filter-log-events \
    --log-group-name /aws/lambda/SanralFunction \
    --filter-pattern "ERROR"
```

### 🚨 Troubleshooting Deployments

<details>
<summary><strong>Layer Dependencies Missing</strong></summary>

**Issue**: `beautifulsoup4` or `requests` import errors

**Solution**: Ensure layers are properly created and attached:
```bash
# For SAM: Verify layer directories exist and contain packages
ls -la beautifulsoup4-library/python/
ls -la requests-library/python/

# For manual deployment: Create and upload layers separately
```
</details>

<details>
<summary><strong>IAM Permission Errors</strong></summary>

**Issue**: Access denied for SQS or CloudWatch operations

**Solution**: Verify the Lambda execution role has required permissions:
- `sqs:SendMessage`
- `sqs:GetQueueUrl` 
- `sqs:GetQueueAttributes`
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`
- `ec2:CreateNetworkInterface`
- `ec2:DeleteNetworkInterface`
- `ec2:DescribeNetworkInterfaces`
</details>

<details>
<summary><strong>Workflow Deployment Fails</strong></summary>

**Issue**: GitHub Actions workflow errors

**Solution**: Check repository secrets are correctly configured and the target Lambda function exists in AWS.
</details>

<details>
<summary><strong>API Connection Issues</strong></summary>

**Issue**: Cannot connect to SANRAL API endpoints

**Solution**: Verify network connectivity and consider VPC configuration if the Lambda needs specific network access.
</details>

Choose the deployment method that best fits your development workflow and infrastructure requirements. SAM deployment is recommended for development environments, while workflow deployment excels for production CI/CD pipelines.

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
