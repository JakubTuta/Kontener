FROM python

ENV MONGO_DB_USERNAME=admin \
    MONGO_DB_PWD=password \
    OPENAI_API_KEY=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

RUN mkdir -p /home/app

COPY ./app /home/app

RUN pip install -r /home/app/requirements.txt

CMD ["python", "/home/app/server.py"]