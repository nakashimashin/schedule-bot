import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def main():
    creds = None
    # ユーザーのアクセスとリフレッシュトークンを格納するtoken.jsonファイルが存在する場合、token.jsonを使用して認証する。
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 有効な資格情報がない場合、ユーザーにログインを求める。
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 次回の実行のために資格情報を保存する
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


    try:
        # GoogleカレンダーAPIのサービスオブジェクトを作成
        service = build('calendar', 'v3', credentials=creds)

        # 現在のUTC日時を取得
        now = datetime.datetime.utcnow().isoformat() + 'Z'

        print("次の1件のイベントを取得中")
        # カレンダーのイベントを取得
        events_result = (
            service.events()
            .list(
                calendarId='primary',
                timeMin=now,
                maxResults=1,
                singleEvents=True,
                orderBy='startTime',
            )
            .execute()
        )
        events = events_result.get('items', [])

        if not events:
            print("次のイベントはありません")
            return
        # イベントのタイトルと開始日時を表示
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    except HttpError as error:
        print(f'エラーが発生しました: {error}')

if __name__ == '__main__':
    main()