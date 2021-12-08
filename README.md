# sns-event-to-newrelic
## Description

- Send AWS RDS and AWS ElastiCache SNS notifications to New Relic Custom Event

## Requirements

- AWS SAM

# Usage
## Build

```bash
sam build 
```

## Deploy
### First Deploy

```bash
sam deploy --stack-name sns-event-to-newrelic sns-event-to-newrelic --confirm-changeset --capabilities CAPABILITY_IAM --guided
```

### Normal Deploy

```bash
sam deploy
```

## Put SSM Parameter Store

```bash
aws ssm put-parameter --name "/newrelic/endpoint_url" --value "YOUR_ENDPOINT_URL" --type SecureString
aws ssm put-parameter --name "/newrelic/insert_api_key" --value "YOUR_INSERT_API_KEY" --type SecureString
```

## Test invoke function

```bash
aws lambda invoke --function-name sns-event-to-newrelic --payload file://sample/test-event.json output.json --cli-binary-format raw-in-base64-out
```

## Uninstall

```bash
aws cloudformation delete-stack --stack-name sns-event-to-newrelic
```
