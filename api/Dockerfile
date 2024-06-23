FROM python

ENV OPENAI_API_KEY ${OPENAI_API_KEY}

RUN mkdir -p /home/app

COPY . /home/app

RUN pip install -r /home/app/requirements.txt

CMD ["python", "/home/app/api.py"]