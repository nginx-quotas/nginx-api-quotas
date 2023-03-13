FROM python:3.7
LABEL maintainer="Shawn"

COPY ./services/nginx-quota-simulator/. /var/www/nginx-quota-simulator/

WORKDIR /var/www/nginx-quota-simulator/app
ENV PYTHONPATH "${PYTHONPATH}:/var/www/nginx-quota-simulator/"

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
