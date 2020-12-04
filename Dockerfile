# Most of the time, Alpine is a great base image to start with.
# If we're building a container for Python, we use something different.
# Learn why here: https://pythonspeed.com/articles/base-image-python-docker-images/
# TLDR: Alpine is very slow when it comes to running Python!

# STEP 1: Install base image.
FROM library/python:3.7-alpine as base
FROM base as builder
RUN mkdir /install
WORKDIR /install

# STEP 2: Copy the source code in the current directory to the container.
# Store it in a folder named /app.
ADD . /app

# STEP 3: Set working directory to /app so we can execute commands in it
WORKDIR /app
# Path to install pillow globally.
ENV LIBRARY_PATH=/lib:/usr/lib

# STEP 4: Dependencies for Pillow
# Pillow dependencies as listed from stackoverflow https://stackoverflow.com/questions/57787424/django-docker-python-unable-to-install-pillow-on-python-alpine
# This will create a virtual container where we install the Pillow build dependences
# After installing Pillow, we will delete the container containing the dependencies as they are not needed at runtime
# This process will decrease our docker filesize from bloating
RUN apk update \
    && apk add --virtual build-dependencies gcc python3-dev musl-dev \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install Pillow \
    && apk del build-dependencies

# STEP 5: Install required dependencies. -Pillow
RUN pip install -r requirements.txt

# STEP 6: Declare environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# STEP 7: Expose the port that Flask is running on
EXPOSE 5000

# STEP 8: Run Flask!
CMD ["flask", "run", "--host=0.0.0.0"]
