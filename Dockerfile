FROM python:3.8

WORKDIR /Airbnb-Scraper

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./Scraper ./Scraper

CMD ["python", "./Scraper"]