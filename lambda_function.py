# ==================================================================================================
#
# File: SANRALLambda/lambda_function.py
#
# Description:
# This script contains an AWS Lambda function designed to fetch tender data from the SANRAL
# (South African National Roads Agency) API. Unlike other scrapers, this one has a more
# complex data retrieval process which is handled by the model class.
#
# The function performs the following steps:
# 1. Fetches an initial list of tenders from the SANRAL API.
# 2. Handles potential network errors or invalid API responses.
# 3. Extracts the list of tenders (where each tender is itself a list of data points).
# 4. Iterates through each tender item and passes it to the SanralTender model, which
#    then performs a secondary web scraping operation to get more details.
# 5. Skips and logs any items that fail the complex validation and scraping process.
# 6. Converts the successfully processed tender objects into dictionaries.
# 7. Batches the tender data and sends it to a specified SQS FIFO queue.
#
# ==================================================================================================

# --- Import necessary libraries ---
import json
import requests
import logging
import boto3
from models import SanralTender # Import the data model for SANRAL tenders.

# --- Global Constants and Configuration ---
# The URL of the SANRAL open tenders API.
SANRAL_API_URL = "https://www.nra.co.za/sanral-tenders/list/open-tenders?pageSize=100&pageIndex=1&order_by=0&order=asc&init=0"

# Standard HTTP headers to mimic a web browser.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
}

# --- Logger Setup ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- AWS Service Client Initialization ---
sqs_client = boto3.client('sqs')
# The URL of the target SQS FIFO queue.
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/211635102441/AIQueue.fifo'

# ==================================================================================================
# Lambda Function Handler
# ==================================================================================================
def lambda_handler(event, context):
    """
    The main handler function for the AWS Lambda.
    """
    logger.info("Starting SANRAL tenders processing job.")

    # --- Step 1: Fetch Initial Data from the SANRAL API ---
    try:
        logger.info(f"Fetching data from {SANRAL_API_URL}")
        response = requests.get(SANRAL_API_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        api_response_dict = response.json()
        
        # The API returns a list of tenders under the 'tenders' key.
        all_tenders = api_response_dict.get('tenders', [])
        # It also returns a count of total tenders available.
        total_filtered = api_response_dict.get('total_filtered', 0)

        logger.info(f"Successfully fetched {len(all_tenders)} of {total_filtered} total tender items from the API.")
        
        # A check to see if pagination might be needed in the future.
        if len(all_tenders) < total_filtered:
            logger.warning("API returned fewer items than total_filtered. Consider re-enabling pagination if totals exceed page size.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from API: {e}")
        return {'statusCode': 502, 'body': json.dumps({'error': 'Failed to fetch data from source API'})}
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from API response. Response text: {response.text}")
        return {'statusCode': 502, 'body': json.dumps({'error': 'Invalid JSON response from source API'})}

    # --- Step 2: Process Each Tender Item Using the Model ---
    processed_tenders = []
    skipped_count = 0

    # Each 'item' from the 'all_tenders' list is a sub-list of tender details.
    for item in all_tenders:
        try:
            # The from_api_response method handles all the complex parsing and scraping.
            tender_object = SanralTender.from_api_response(item)
            
            # The model returns None if the initial data is invalid.
            if tender_object:
                processed_tenders.append(tender_object)
            else:
                skipped_count += 1
        except Exception as e:
            # Catch any unexpected errors during the scraping or parsing process.
            skipped_count += 1
            logger.warning(f"Skipping tender due to a validation/parsing error: {e}. Raw item: {item}")
            continue

    logger.info(f"Successfully processed {len(processed_tenders)} tenders.")
    if skipped_count > 0:
        logger.warning(f"Skipped a total of {skipped_count} tenders due to errors.")

    # --- Step 3: Prepare Data for SQS ---
    processed_tender_dicts = [tender.to_dict() for tender in processed_tenders]

    # --- Step 4: Batch and Send Messages to SQS ---
    batch_size = 10
    message_batches = [
        processed_tender_dicts[i:i + batch_size]
        for i in range(0, len(processed_tender_dicts), batch_size)
    ]

    sent_count = 0
    for batch_index, batch in enumerate(message_batches):
        entries = []
        for i, tender_dict in enumerate(batch):
            entries.append({
                'Id': f'tender_message_{batch_index}_{i}',
                'MessageBody': json.dumps(tender_dict),
                # A specific MessageGroupId for SANRAL tenders.
                'MessageGroupId': 'SanralTenderScrape'
            })

        if not entries:
            continue

        try:
            response = sqs_client.send_message_batch(
                QueueUrl=SQS_QUEUE_URL,
                Entries=entries
            )
            sent_count += len(response.get('Successful', []))
            logger.info(f"Successfully sent a batch of {len(entries)} messages to SQS.")
            if 'Failed' in response and response['Failed']:
                logger.error(f"Failed to send some messages in a batch: {response['Failed']}")
        except Exception as e:
            logger.error(f"Failed to send a message batch to SQS: {e}")

    logger.info(f"Processing complete. Sent a total of {sent_count} messages to SQS.")
    
    # --- Step 5: Return a Success Response ---
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Tender data processed and sent to SQS queue.'})
    }