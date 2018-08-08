FROM python:3.6.5

WORKDIR usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]

COPY . .

CMD [ "python", "./bot.py" ]
