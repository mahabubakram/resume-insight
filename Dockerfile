#https://github.com/docker/awesome-compose/tree/master/fastapi
#https://fastapi.tiangolo.com/deployment/docker/#dockerfile
FROM python:3.9

#
COPY . /code

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]