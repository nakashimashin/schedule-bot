import datetime
import os.path
import pdfplumber
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']


def readschedule(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        year = None
        month = None

        for page in pdf.pages:
            text = page.extract_text()

            # 年月の取得
            year_month_search = re.search(r"(\d{4})/(\d{1,2})/(\d{1,2})", text)
            print("正規表現: ", year_month_search)
            if year_month_search:
                year = year_month_search.group(1)
                month = year_month_search.group(2)
    return year, month


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


    year, month = readschedule("教室希望_教養_12月.pdf")
    print("年: ", year, "月: ", month)


    # service = build('calendar', 'v3', credentials=creds)

    # lines1 = readschedule()
    # print(lines1)

    # yearmonth = readschedule()[0]
    # a = yearmonth.split('.')
    # year = int(a[0])
    # mon = int(a[1])

    # if mon == 1 or mon == 3 or mon == 5 or mon == 7 or mon == 8 or mon == 10 or mon == 12:
    #     num_days = 31
    # elif mon == 2:
    #     num_days = 28
    # else :
    #     num_days = 30

    # for i in readschedule():
    #     s = i.split(' ')
    #     if(len(s) == 1):
    #         continue

    #     d_s = int(s[0])
    #     d_e = int(s[0])
    #     m_s = mon
    #     m_e = mon
    #     y_s = year
    #     y_e = year

    #     if(mon == 12 and d_e == 31):
    #         y_e = year + 1

    #     if(num_days == d_e):
    #         d_e = 1
    #         if mon == 12:
    #             m_e = 1
    #         else:
    #             m_e = m_e + 1



    #     event = {
    #     'summary': '{}'.format(s[1]),
    #     'location': 'Japan',
    #     'description': '{}'.format(s[1]),
    #     'start': {
    #         'date': '{}-{}-{}'.format(y_s,m_s,d_s),
    #         'timeZone': 'Japan',
    #     },
    #     'end': {
    #         'date': '{}-{}-{}'.format(y_e,m_e,d_e),
    #         'timeZone': 'Japan',
    #     },
    #     }
    #     event = service.events().insert(calendarId='primary',body=event).execute()
    #     print (event['id'])

if __name__ == '__main__':
    main()