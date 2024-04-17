FROM python

ENV OPENAI_API_KEY=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

RUN mkdir -p /home/app

COPY ./app /home/app

RUN pip install -r /home/app/requirements.txt

CMD ["python", "/home/app/server.py"]
