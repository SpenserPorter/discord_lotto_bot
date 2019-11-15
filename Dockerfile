FROM python:3.6.5

ARG LOTTO_BOT_TOKEN
ENV LOTTO_BOT_TOKEN=$LOTTO_BOT_TOKEN

WORKDIR usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./bot.py" ]
