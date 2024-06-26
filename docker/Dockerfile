FROM python:3.12-slim-bookworm

ENV APP_HOME /app
WORKDIR $APP_HOME

ENV PYTHONUNBUFFERED 1

COPY requirements.txt $APP_HOME/requirements.txt
RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

COPY ./src/ $APP_HOME

CMD ["uvicorn", "com_agent.api.app:app", "--host", "0.0.0.0", "--port", "80"]
