FROM python:3.7
LABEL maintainer="Shawn"

COPY ./services/nginx-quota-limiter-w-db/ /var/www/nginx-quota-limiter-w-db/

WORKDIR /var/www/nginx-quota-limiter-w-db/app
ENV PYTHONPATH "${PYTHONPATH}:/var/www/nginx-quota-limiter-w-db/"

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
