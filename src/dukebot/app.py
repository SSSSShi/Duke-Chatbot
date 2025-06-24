import json
from .agent import process_user_query
import time

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    This function is triggered by an API Gateway request. The user's query
    is expected in the 'query' field of the JSON body of the request.
    """
    try:
        start_time = time.time()
        print("--- Lambda handler started ---")
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        query = body.get('query')
        print(f"Received query: {query}")

        if not query:
            print("ERROR: Missing 'query' in request body.")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Missing 'query' in request body"})
            }

        # Process the user's query
        print("Starting process_user_query...")
        response_message = process_user_query(query)
        print("Finished process_user_query.")

        end_time = time.time()
        print(f"--- Lambda handler finished. Total time: {end_time - start_time:.2f} seconds. ---")

        return {
            'statusCode': 200,
            'body': json.dumps({'response': response_message})
        }
    except Exception as e:
        # Log the exception for debugging
        print(f"ERROR in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        } 