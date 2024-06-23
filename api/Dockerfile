FROM python

ENV OPENAI_API_KEY sk-proj-3is3ZkWDCHnRf1D7WcL0T3BlbkFJVIuhLeMKsV0YVnK5rASP

RUN mkdir -p /home/app

COPY . /home/app

RUN pip install -r /home/app/requirements.txt

CMD ["python", "/home/app/api.py"]