import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

USERS_TABLE = os.environ.get("USERS_TABLE", "CarbonUsers")
ACTIVITIES_TABLE = os.environ.get("ACTIVITIES_TABLE", "CarbonActivities")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

FACTORS = {
    "travel": {
        "car": 0.21,
        "bus": 0.089,
        "train": 0.041,
        "flight": 0.255,
        "walk": 0.0,
        "cycle": 0.0,
    },
    "electricity": {"grid": 0.82},
    "food": {"meat": 3.5, "mixed": 1.7, "veg": 0.8, "vegan": 0.5},
}


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,PUT,OPTIONS",
        },
        "body": json.dumps(body, default=_json_default),
    }


def _json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"Cannot serialize {type(value)}")


def _parse_body(event):
    if not event.get("body"):
        return {}
    return json.loads(event["body"])


def _path(event):
    return event.get("path", "/") or "/"


def _qs(event):
    return event.get("queryStringParameters") or {}


def _decimal(value):
    return Decimal(str(round(float(value), 2)))


def estimate(category, activity_type, amount):
    try:
        factor = FACTORS[category][activity_type]
    except KeyError as exc:
        raise ValueError("Unknown category or activity type") from exc
    return round(float(amount) * factor, 2)


def _put_user(user_id, email, threshold_kg, name=""):
    table = dynamodb.Table(USERS_TABLE)
    item = {
        "userId": user_id,
        "email": email or "",
        "name": name or "",
        "thresholdKg": _decimal(threshold_kg),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
    table.put_item(Item=item)
    return item


def _get_user(user_id):
    table = dynamodb.Table(USERS_TABLE)
    result = table.get_item(Key={"userId": user_id})
    return result.get("Item")


def _daily_total(user_id, date):
    table = dynamodb.Table(ACTIVITIES_TABLE)
    result = table.query(
        KeyConditionExpression=Key("userId").eq(user_id) & Key("activityKey").begins_with(date)
    )
    return sum(float(item["co2Kg"]) for item in result.get("Items", []))


def _maybe_alert(user, date, total_kg):
    if not SNS_TOPIC_ARN:
        return False
    threshold = float(user.get("thresholdKg", 15))
    if total_kg <= threshold:
        return False
    email = user.get("email") or "configured SNS subscriber"
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="Carbon tracker: daily threshold crossed",
        Message=(
            f"Daily CO2 for {date} is {total_kg:.2f} kg, "
            f"which exceeds the {threshold:.2f} kg threshold. "
            f"Notify: {email}."
        ),
    )
    return True


def create_activity(body):
    user_id = body.get("userId") or str(uuid.uuid4())
    category = body["category"]
    activity_type = body["type"]
    amount = float(body["amount"])
    date = body.get("date") or datetime.now(timezone.utc).date().isoformat()
    co2 = estimate(category, activity_type, amount)
    activity_id = body.get("id") or str(uuid.uuid4())
    item = {
        "userId": user_id,
        "activityKey": f"{date}#{activity_id}",
        "activityId": activity_id,
        "date": date,
        "category": category,
        "type": activity_type,
        "amount": _decimal(amount),
        "co2Kg": _decimal(co2),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    dynamodb.Table(ACTIVITIES_TABLE).put_item(Item=item)

    user = _get_user(user_id)
    if user is None:
        user = _put_user(
            user_id,
            body.get("email", ""),
            body.get("thresholdKg", 15),
            body.get("name", ""),
        )
    total = _daily_total(user_id, date)
    alerted = _maybe_alert(user, date, total)
    return {
        "activity": item,
        "dailyTotalKg": round(total, 2),
        "alertSent": alerted,
    }


def list_activities(params):
    user_id = params.get("userId")
    if not user_id:
        raise ValueError("userId is required")
    result = dynamodb.Table(ACTIVITIES_TABLE).query(
        KeyConditionExpression=Key("userId").eq(user_id)
    )
    items = result.get("Items", [])
    start = params.get("from")
    end = params.get("to")
    if start:
        items = [item for item in items if item["date"] >= start]
    if end:
        items = [item for item in items if item["date"] <= end]
    items.sort(key=lambda item: item["activityKey"], reverse=True)
    return {"activities": items}


def summary(params):
    payload = list_activities(params)
    totals = {}
    for item in payload["activities"]:
        totals[item["date"]] = totals.get(item["date"], 0) + float(item["co2Kg"])
    return {
        "dailyTotals": [
            {"date": date, "kg": round(kg, 2)} for date, kg in sorted(totals.items())
        ],
        "totalKg": round(sum(totals.values()), 2),
    }


def save_settings(body):
    if not body.get("userId"):
        raise ValueError("userId is required")
    item = _put_user(
        body["userId"],
        body.get("email", ""),
        body.get("thresholdKg", 15),
        body.get("name", ""),
    )
    return {"settings": item}


def lambda_handler(event, context):
    method = (event.get("httpMethod") or "GET").upper()
    path = _path(event).rstrip("/") or "/"

    if method == "OPTIONS":
        return _response(200, {"ok": True})

    try:
        if method == "POST" and path.endswith("/activities"):
            return _response(201, create_activity(_parse_body(event)))
        if method == "GET" and path.endswith("/activities"):
            return _response(200, list_activities(_qs(event)))
        if method == "GET" and path.endswith("/summary"):
            return _response(200, summary(_qs(event)))
        if method == "PUT" and path.endswith("/settings"):
            return _response(200, save_settings(_parse_body(event)))
        if method == "GET" and path.endswith("/settings"):
            user_id = _qs(event).get("userId")
            if not user_id:
                raise ValueError("userId is required")
            return _response(200, {"settings": _get_user(user_id)})
        if method == "GET" and path.endswith("/health"):
            return _response(200, {"status": "ok"})
        return _response(404, {"error": f"No route for {method} {path}"})
    except ValueError as exc:
        return _response(400, {"error": str(exc)})
    except Exception as exc:
        return _response(500, {"error": "Internal error", "detail": str(exc)})
