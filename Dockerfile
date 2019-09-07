FROM nikolaik/python-nodejs:python3.7-nodejs12
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY package.json /code/
COPY package-lock.json /code/
RUN npm install
COPY . /code/
RUN npm run build

