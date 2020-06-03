# Algorithm-Tips-App

# Running Locally

This app has two main components: the back-end API (written in Python), and the
front-end (written in JS using Vue). As they are written in different
languages, there are two different pieces of setup.

## Setting Up Python

First, install Python 3.6+ and virtualenv. Then, use the following commands to set up the required Python environment:

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

You must also install `uwsgi`. If it is available in your distribution's repository, use that. On Debian, this can be done via:

```bash
sudo apt-get install uwsgi uwsgi-plugin-python3
```

If it is not available through your distribution, you can install it with `pip` or `conda`:

```bash
pip install uwsgi  # this WILL NOT WORK if you got Python via Anaconda,
                   # use the below command instead
conda install uwsgi 
```

## Setting up Node

This project uses [yarn](https://yarnpkg.com/) for package management. After installing both Node and Yarn, setup is straightforward:

```bash
cd frontend
yarn install
```

## Configuring `keys.conf`

Before running anything, you need to connect to the database. Credentials and
other configuration settings are stored in `keys.conf` which is *not* committed
to the repository. To initialize it, copy `keys.conf.sample` to `keys.conf` and
fill out the required fields.

## Running Locally

The backend **must** be run via uWSGI to be mounted at the right endpoint:

```bash
DEBUG=true uwsgi api-dev.ini --plugin python3
```

After modifying the API, kill uWSGI and and run it again.

The `DEBUG` environment variable enables cross-domain cookies for local
development (required due to the frontend and backend running on different ports). **NEVER** set it in a production environment.

The front-end can be run similarly easily:

```bash
cd frontend
yarn serve
```

This command does not need to be re-run when the front-end code changes.

## Testing & Linting

This project has a few tests to cover key features, though coverage of the project as a whole is incomplete. The tests & lints can be run as follows:

```bash
pytest api  # test the API
flake8 api  # lint the API
cd frontend
yarn test   # test the front-end
yarn lint   # lint the front-end
```

These are all run on GitHub each time new commits are pushed.

# Deployment

## Building

The backend does not have a required build step. However, the frontend does:

```
cd frontend
yarn build
```

## Server Setup

The server is setup to host the backend via uWSGI hidden behind an NGINX
instance. All paths beginning with `/api` are mapped to the API. All other
paths are mapped to the front-end. See the wiki for details on NGINX configuration.

## Starting & Stopping the API

The API will start on boot, but if you need to (re)start it manually, use the following commands:

```bash
./stop-api.sh  # stop the API, if it is running
./start-api.sh  # start the API in the background
```

Logs for the API can be found at `/var/log/api.log`.

## Deploying the Front-End

To deploy the front-end, first build it (see above) and then copy the contents of the `frontend/dist/` folder to `/var/www/` on the server. Ensure that the contents are readable by the server. A simple way to do this is to run:

```bash
chown -R nginx:nginx /var/www
```

## Setting up Periodic Alert Triggers

This only needs to be done once. To initialize periodic triggers, run the following command *as root:*

```bash
python trigger-setup.py  # Not Yet Implemented
```

## Manually Triggering Alerts

Alerts can only be triggered from the server by default. To trigger one manually, log into the server and run:

```bash
curl -X POST http://localhost/api/alert/trigger
```