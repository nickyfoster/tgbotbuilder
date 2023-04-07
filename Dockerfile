FROM python:3.10-slim

WORKDIR "/application"
ENV PYTHONPATH=/application
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml pyproject.toml
COPY requirements.txt requirements.txt
COPY botbuilder botbuilder

RUN pip --version && pip install . --no-cache-dir

ENTRYPOINT ["python","./botbuilder/app.py"]