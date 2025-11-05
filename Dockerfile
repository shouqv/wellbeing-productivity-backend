#Base Image 
FROM python:3.13

WORKDIR /usr/src/backend

# put the requirements.txt onto the container, and install all of the dependencies from it.
# Doing this here means docker can optimise and cache some things
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download wait-for-it.sh for database waiting
# Basically just says 'hey, don't try to connect to the database until it's actually ready'
RUN curl -o wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x wait-for-it.sh

# Copy all of the project files from here (.) current working directory (WORKDIR) of the container
COPY . .

# Make it so the container will accept connections on port 8000
EXPOSE 8000

# The command line that we want to run when the container is up and running
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]