FROM python:3.6.5

ARG LOTTO_BOT_TOKEN
ENV LOTTO_BOT_TOKEN=$LOTTO_BOT_TOKEN

WORKDIR usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]

COPY . .

CMD [ "python", "./bot.py" ]
