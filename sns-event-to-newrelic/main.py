import os
import logging
import json
import gzip
import requests
import boto3
from botocore.exceptions import ClientError

# json Log Setting
class JsonFormatter:
  def format(self, record):
    return json.dumps(vars(record))

logging.basicConfig()
logging.getLogger().handlers[0].setFormatter(JsonFormatter())

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))


def get_parameters(param_key):
  ssm_client = boto3.client('ssm')
  response = ssm_client.get_parameters(
    Names=[
      param_key,
    ],
    WithDecryption=True
  )
  return response['Parameters'][0]['Value']

def lambda_handler(event, context):
  logger.info(event, extra={'custom_description': 'var: event'})
  message_event = json.loads(event['Records'][0]['Sns']['Message'])

  # set AWS Info to SNS Topic
  event_aws_account = event['Records'][0]['Sns']['TopicArn'].split(':')[4]
  event_aws_region = event['Records'][0]['Sns']['TopicArn'].split(':')[3]
  nr_event_type = event['Records'][0]['Sns']['TopicArn'].split(':')[5]

  # get nr secrets
  nr_endpoint_url = get_parameters("/newrelic/endpoint_url")
  nr_ｘ_insert_key = get_parameters("/newrelic/insert_api_key")

  nr_additional_headers = { 
    'Content-Type': 'application/json',
    'X-Insert-Key': nr_ｘ_insert_key,
    'Content-Encoding': 'gzip'
  }
  
  nr_event_opt = {
    'eventType': nr_event_type,
    'AWSAccount': event_aws_account,
    'AWSRegion': event_aws_region
  }

  # merge nr_event_opt
  nr_event = message_event.copy()
  nr_event.update(nr_event_opt)
  logger.info(nr_event, extra={'custom_description': 'var: nr_event'})

  # post custom event to newrelic
  request_json_gz = gzip.compress(json.dumps(nr_event).encode('utf-8'))
  try:
    r = requests.post(nr_endpoint_url, data=request_json_gz, headers=nr_additional_headers)
    r.raise_for_status()
    logger.info(r.text, extra={'custom_description': 'result: post custom event to newrelic'})
  except requests.exceptions.RequestException as e:
    raise e

if __name__ == "__main__":
  args = sys.argv
  lambda_handler(args[1], args[2])
