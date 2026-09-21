import csv
import io
import os
import requests
from twilio.rest import Client

def load_env_file():
  env_path = os.path.join(os.path.dirname(__file__), ".env")
  if not os.path.exists(env_path):
    return

  with open(env_path, encoding="utf-8") as env_file:
    for raw_line in env_file:
      line = raw_line.strip()
      if not line or line.startswith("#") or "=" not in line:
        continue
      key, value = line.split("=", 1)
      os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_env_file()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER")

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1BuKSfRWG6OiPrUkvkOAMPtENbgJwohYhV_QHPb0TWxY/export?format=csv"


def fetch_stock_data():
  response = requests.get(SHEET_CSV_URL, timeout=10)
  response.raise_for_status()

  f = io.StringIO(response.text)
  rows = list(csv.reader(f))

  # Keep header plain ASCII (no emojis)
  lines = ["Stock Alert:"]

  i = 1
  while i < len(rows):
    name_row = rows[i]
    if len(name_row) > 1 and name_row[1].strip():
      stock_name = name_row[1].strip()

      if i + 1 < len(rows):
        data_row = rows[i + 1]
        raw_price = data_row[1].strip() if len(data_row) > 1 else "0"
        raw_diff = data_row[2].strip() if len(data_row) > 2 else "0"

        try:
          price_val = float(raw_price)
          formatted_price = f"{price_val:,.2f}"
        except ValueError:
          formatted_price = raw_price

        try:
          diff_val = float(raw_diff)
          formatted_diff = (
              f"+{diff_val:.2f}" if diff_val >= 0 else f"-{abs(diff_val):.2f}"
          )
        except ValueError:
          formatted_diff = raw_diff

        # Clean, short GSM-compatible format (e.g., "Reliance: 1246.40 (+20.00)")
        lines.append(f"{stock_name}: {formatted_price} ({formatted_diff})")

    i += 2

  return "\n".join(lines)


def main():
  required_settings = {
      "TWILIO_ACCOUNT_SID": TWILIO_ACCOUNT_SID,
      "TWILIO_AUTH_TOKEN": TWILIO_AUTH_TOKEN,
      "TWILIO_PHONE_NUMBER": TWILIO_PHONE_NUMBER,
      "MY_PHONE_NUMBER": MY_PHONE_NUMBER,
  }
  missing_settings = [name for name, value in required_settings.items() if not value]
  if missing_settings:
    raise RuntimeError(
        "Missing required settings: " + ", ".join(missing_settings)
        + ". Add them to .env or the environment."
    )

  print("Fetching clean stock data...")
  sms_body = fetch_stock_data()
  print("\nPayload (Length:", len(sms_body), "chars):\n" + sms_body)

  print("\nSending SMS via Twilio...")
  client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
  msg = client.messages.create(
      body=sms_body, from_=TWILIO_PHONE_NUMBER, to=MY_PHONE_NUMBER
  )
  print(f"Message sent successfully! SID: {msg.sid}")


if __name__ == "__main__":
  main()