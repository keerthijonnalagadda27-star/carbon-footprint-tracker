# Carbon Footprint Tracker

A serverless web application for logging daily travel, electricity, and food activity and converting each entry into kilograms of CO₂. The stack is fully managed on AWS: a static frontend on S3, a REST API on API Gateway, Python 3.12 compute on Lambda, persistence on DynamoDB, and threshold emails through SNS.

[Live application](http://carbon-tracker-106834399198-ap-south-1.s3-website.ap-south-1.amazonaws.com)

## Features

- Activity logging for travel (km), electricity (kWh), and meals
- Instant CO₂ estimates from documented emission factors
- Dashboard totals for today, the current week, and the current month
- Category breakdown and a seven-day emissions chart
- Configurable daily threshold with Amazon SNS email alerts
- Activity history persisted in DynamoDB

## Architecture

```
Browser  →  Amazon S3 (HTML, CSS, JS)
         →  Amazon API Gateway (REST)
         →  AWS Lambda (Python 3.12)
         →  Amazon DynamoDB (users, activities)
         →  Amazon SNS (threshold email)
         →  Amazon CloudWatch (Lambda errors)
```

Infrastructure is defined in a single SAM / CloudFormation template (`template.yaml`). The Lambda execution role is limited to DynamoDB, SNS, and CloudWatch Logs. The frontend does not embed AWS credentials.

## Tech stack

| Layer | Services / tools |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| API | Amazon API Gateway |
| Compute | AWS Lambda, Python 3.12 |
| Data | Amazon DynamoDB |
| Notifications | Amazon SNS |
| Hosting | Amazon S3 static website |
| IaC | AWS SAM, CloudFormation |
| Observability | Amazon CloudWatch |

## Emission factors

| Category | Factor |
|---|---|
| Travel — car / bus / train / flight / walk or cycle | 0.21 / 0.089 / 0.041 / 0.255 / 0.00 kg CO₂ per km |
| Electricity — grid | 0.82 kg CO₂ per kWh |
| Food — meat / mixed / vegetarian / vegan | 3.5 / 1.7 / 0.8 / 0.5 kg CO₂ per meal |

Sample total: 20 km by car + 50 kWh + 3 vegetarian meals = **47.60 kg CO₂**.

## Repository structure

```
frontend/             Static client (S3)
backend/handler.py    Lambda handler
template.yaml         SAM template
```

## Local development

```bash
cd frontend
python -m http.server 8080
```

The UI is available at `http://localhost:8080`. If `apiUrl` in `frontend/js/config.js` is empty, activity data is stored in `localStorage`.

## Deployment

Requires AWS CLI and AWS SAM CLI.

```bash
sam build
sam deploy --guided --parameter-overrides AlertEmail=you@example.com
aws s3 sync frontend s3://<bucket-name> --delete
```

Set `frontend/js/config.js` `apiUrl` to the deployed API Gateway stage URL, then sync the frontend again. Confirm the SNS subscription from the inbox used in `AlertEmail`.

## License

Personal / academic project.
