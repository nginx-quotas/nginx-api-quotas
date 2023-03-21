FROM python:3.7
LABEL maintainer="Shawn"

COPY ./services/nginx-quota-limiter/ /var/www/nginx-quota-limiter/

WORKDIR /var/www/nginx-quota-limiter/app
ENV PYTHONPATH "${PYTHONPATH}:/var/www/nginx-quota-limiter/"

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
