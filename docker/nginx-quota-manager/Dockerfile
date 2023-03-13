FROM python:3.7
LABEL maintainer="Shawn"

COPY ./services/nginx-quota-manager/ /var/www/nginx-quota-manager/

WORKDIR /var/www/nginx-quota-manager/app
ENV PYTHONPATH "${PYTHONPATH}:/var/www/nginx-quota-manager/"

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
