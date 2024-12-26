import json
import boto3
from schedule import readschedule, add_event_to_calendar
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Googleカレンダー認証設定
def get_google_service():
    creds = service_account.Credentials.from_service_account_file(
        '/var/task/service-account-key.json',
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    return build('calendar', 'v3', credentials=creds)

def lambda_handler(event, context):
    # SQSメッセージ処理
    print("Event: ", event)

    # メッセージの取得
    for record in event['Records']:
        body = json.loads(record['body'])
        file_url = body['file_url']
        print(f"ファイルURL: {file_url}")

        # PDFファイルの処理
        process_pdf(file_url)

    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }

def process_pdf(file_url):
    # SlackからPDFをダウンロード
    headers = {'Authorization': f'Bearer {os.getenv("SLACK_BOT_TOKEN")}'}
    response = requests.get(file_url, headers=headers, stream=True)
    file_name = '/tmp/temp.pdf'

    with open(file_name, 'wb') as pdf_file:
        for chunk in response.iter_content(chunk_size=8192):
            pdf_file.write(chunk)

    # PDFからスケジュールを取得
    year, month, available_dates = readschedule(file_name)

    # Googleカレンダーに登録
    service = get_google_service()
    add_event_to_calendar(service, year, month, available_dates)
    print("スケジュールをGoogleカレンダーに追加しました。")
