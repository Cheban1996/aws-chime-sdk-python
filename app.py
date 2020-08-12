import os
from uuid import uuid4

import aiofiles
import boto3
import fastapi

app = fastapi.FastAPI()

meeting_tables = {}


chime = boto3.client(
    'chime',
    region_name='us-east-1',
    aws_access_key_id=os.getenv('ACCESS_KEY'),
    aws_secret_access_key=os.getenv('SECRET_KEY')
)
chime.endpoint = 'https://service.chime.aws.amazon.com'  # OPTIONAL


@ app.get('/')
async def index():
    async with aiofiles.open('templates/meeting.html', encoding='utf-8') as f:
        index_page = await f.read()
    return fastapi.responses.HTMLResponse(index_page)


@ app.post('/join')
async def join(title: str, name: str, region: str):
    if title and name and region:
        if not meeting_tables.get(title):  # create new meeting
            try:
                meeting_tables[title] = chime.create_meeting(
                    ClientRequestToken=str(uuid4()),
                    MediaRegion=region,
                    ExternalMeetingId=title[0:64]
                )
            except BaseException as e:
                return fastapi.responses.PlainTextResponse(str(e), 400)
        meeting = meeting_tables[title]
        attendee = chime.create_attendee(
            MeetingId=meeting['Meeting']['MeetingId'],
            ExternalUserId=f"{str(uuid4())[0:8]}#{name}"[0:64]
        )
        return fastapi.responses.UJSONResponse({
            'JoinInfo': {
                'Meeting': meeting,
                'Attendee': attendee
            }
        }, status_code=201)

    else:
        return 'Need parameters: title, name, region'


@app.post('/logs')
async def logs():
    return fastapi.responses.PlainTextResponse('Error', status_code=404)


@app.post('/end')
async def end(title):

    chime.deleteMeeting(
        MeetingId=meeting_tables[title]['Meeting']['MeetingId']
    )
