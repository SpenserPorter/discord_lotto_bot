FROM python:3.6.5

WORKDIR usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]

COPY . .

ENV LOTTO_BOT_TOKEN NDU2NDYwOTQ1MDc0NDIxNzgx.DgK4Dg.G4Tm0ZU-MgQ4ESMP_rmI4SBNvFY

CMD [ "python", "./bot.py" ]
