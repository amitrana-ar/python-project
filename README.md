import csv
import io
import requests
from twilio.rest import Client

# Twilio Configuration
TWILIO_ACCOUNT_SID = "YOUR_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_AUTH_TOKEN"
TWILIO_PHONE_NUMBER = "+1XXXXXXXXXX"
MY_PHONE_NUMBER = "+91XXXXXXXXXX"

# Google Sheet Export Link
SHEET_CSV_URL = (
    "[https://docs.google.com/spreadsheets/d/](https://docs.google.com/spreadsheets/d/)<SPREADSHEET_ID>/export?format=csv"
)


def fetch_stock_data():
  response = requests.get(SHEET_CSV_URL, timeout=10)
  response.raise_for_status()

  rows = list(csv.reader(io.StringIO(response.text)))
  lines = ["Stock Alert:"]

  # Start from row index 1 to skip header
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

        # Maintain ASCII/GSM-7 compatibility (Avoid ₹ or emoji symbols)
        lines.append(f"{stock_name}: {formatted_price} ({formatted_diff})")

    i += 2

  return "\n".join(lines)


def main():
  print("Extracting market metrics...")
  sms_body = fetch_stock_data()
  print(f"Message payload ({len(sms_body)} chars):\n{sms_body}")

  print("Dispatching via Twilio...")
  client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
  msg = client.messages.create(
      body=sms_body, from_=TWILIO_PHONE_NUMBER, to=MY_PHONE_NUMBER
  )
  print(f"Delivered successfully! SID: {msg.sid}")


if __name__ == "__main__":
  main()