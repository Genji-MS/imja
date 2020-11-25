# Most of the time, Alpine is a great base image to start with.
# If we're building a container for Python, we use something different.
# Learn why here: https://pythonspeed.com/articles/base-image-python-docker-images/
# TLDR: Alpine is very slow when it comes to running Python!

# STEP 1: Install base image. Optimized for Python.
FROM library/python:3.7-alpine as base
FROM base as builder
RUN mkdir /install
WORKDIR /install

# STEP 2: Copy the source code in the current directory to the container.
# Store it in a folder named /app.
ADD . /app

# STEP 3: Set working directory to /app so we can execute commands in it
WORKDIR /app

# Install pillow globally.
ENV LIBRARY_PATH=/lib:/usr/lib

# STEP 4: Dependencies for Pillow
#RUN apk add zlib-dev jpeg-dev gcc musl-dev
#--virtual build-dependencies 
RUN apk update \
    && apk add --virtual build-dependencies jpeg-dev zlib-dev libjpeg \
    #gcc python3-dev musl-dev \
    #&& apk add jpeg-dev zlib-dev libjpeg \
    && pip install Pillow \
    && apk del build-dependencies
#&& apt-get del build-dependencies
#RUN apt-get install gcc python3-dev musl-dev \
#    && apt-get install jpeg-dev zlib-dev libjpeg \
#RUN apt-get install libjpeg-dev \
#    && pip install Pillow

# STEP 4.5: Install required dependencies.
RUN pip install -r requirements.txt

# STEP 5: Declare environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# STEP 6: Expose the port that Flask is running on
EXPOSE 5000

# STEP 7: Run Flask!
CMD ["flask", "run", "--host=0.0.0.0"]
