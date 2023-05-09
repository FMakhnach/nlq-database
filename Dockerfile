# start by pulling the python image
FROM python:3.10-slim-buster

RUN pip install --upgrade pip

# switch working directory
WORKDIR /app

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /app

EXPOSE 80

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port", "80"]
