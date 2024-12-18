import os
import json
import requests
from flask import Flask, request, jsonify
from schedule import readschedule, add_event_to_calendar, service_account
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CALENDAR_ID = os.getenv("CALENDAR_ID")

# Flaskアプリの作成
app = Flask(__name__)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Slackからのリクエストボディを取得
    body = request.json

    # SlackのVerification用 (最初の一回)
    if 'challenge' in body:
        return jsonify({"challenge": body["challenge"]})

    # ファイル共有イベントが来た時の処理
    if 'event' in body and body['event']['type'] == 'file_shared':
        file_id = body['event']['file']['id']

        # Slack APIを使ってファイルのURLを取得
        headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
        file_info_url = f'https://slack.com/api/files.info?file={file_id}'
        response = requests.get(file_info_url, headers=headers)
        file_url = response.json()['file']['url_private']

        print(f"PDFファイルのURL: {file_url}")

        # PDFファイルをダウンロード
        download_and_process_pdf(file_url)

        return jsonify({'status': 'File processing successfully'})

    return jsonify({'status': 'Event not handled'})

def download_and_process_pdf(file_url, file_name='temp.pdf'):
    """SlackからPDFをダウンロードし、スケジュールを取得してGoogleカレンダーに登録する"""
    headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
    response = requests.get(file_url, headers=headers, stream=True)

    with open(file_name, 'wb') as pdf_file:
        for chunk in response.iter_content(chunk_size=8192):
            pdf_file.write(chunk)

    # PDFからスケジュールを取得
    year, month, available_dates = readschedule(file_name)

    # Googleカレンダーに登録
    creds = service_account.Credentials.from_service_account_file(
        'service-account-key.json', scopes=['https://www.googleapis.com/auth/calendar']
    )

    service = build('calendar', 'v3', credentials=creds)
    add_event_to_calendar(service, year, month, available_dates)


if __name__ == '__main__':
    app.run(port=5001, debug=True)
