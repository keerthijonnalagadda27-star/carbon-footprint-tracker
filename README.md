# Carbon Footprint Tracker

Serverless web app that estimates daily CO₂ from travel, electricity, and food. Live on AWS in `ap-south-1` (Mumbai).

**Live demo:** [S3 website](http://carbon-tracker-106834399198-ap-south-1.s3-website.ap-south-1.amazonaws.com)

## What it does

- Log travel (km), electricity (kWh), and meals
- Convert each entry to kg CO₂ using documented emission factors
- Dashboard for today / this week / this month, plus a last-7-days chart
- Email alert via Amazon SNS when today’s total crosses 15 kg CO₂

## Architecture

Browser → **Amazon S3** (static HTML/CSS/JS) → **API Gateway** → **AWS Lambda** (Python 3.12) → **DynamoDB**. If the daily total is over the threshold, Lambda publishes to **SNS**. **CloudWatch** watches Lambda errors. **IAM** gives Lambda only DynamoDB, SNS, and logging permission. The full stack is one **CloudFormation** / SAM template (`template.yaml`).

## Emission factors

| Category | Type | Factor |
|---|---|---|
| Travel | Car / Bus / Train / Flight / Walk or cycle | 0.21 / 0.089 / 0.041 / 0.255 / 0.00 kg per km |
| Electricity | Grid | 0.82 kg per kWh |
| Food | Meat / Mixed / Vegetarian / Vegan | 3.5 / 1.7 / 0.8 / 0.5 kg per meal |

Example: 20 km car × 0.21 + 50 kWh × 0.82 + 3 veg meals × 0.80 = **47.60 kg**.

## Run locally (no AWS)

Open `frontend/index.html` in a browser, or:

```bash
cd frontend
python -m http.server 8080
```

Visit http://localhost:8080. With `apiUrl` empty in `frontend/js/config.js`, data stays in the browser.

## Deploy (AWS Free Tier)

Needs AWS CLI + SAM CLI. Do not add EC2, RDS, or NAT Gateways.

```bash
sam build
sam deploy --guided --parameter-overrides AlertEmail=you@example.com
```

Confirm the SNS subscription email. Then:

```bash
aws s3 sync frontend s3://BUCKET_NAME --delete
```

Paste the API Gateway URL into `frontend/js/config.js` as `apiUrl`, and sync the frontend again.

## Project layout

```
frontend/          S3 static site
backend/handler.py  Lambda (CO₂ math, DynamoDB, SNS)
template.yaml      IAM, Lambda, S3, DynamoDB, API Gateway, SNS, CloudWatch
```
