# Connecting to Cloud SQL - Postgres

## Before you begin

1. If you haven't already, set up a Python Development Environment by following the [python setup guide](https://cloud.google.com/python/setup) and
   [create a project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project).

1. Create a 2nd Gen Cloud SQL Instance by following these
   [instructions](https://cloud.google.com/sql/docs/postgres/create-instance). Note the connection
   string, database user, and database password that you create.

1. Create a database for your application by following these
   [instructions](https://cloud.google.com/sql/docs/postgres/create-manage-databases). Note the database
   name.

1. Create a service account with the 'Cloud SQL Client' permissions by following these
   [instructions](https://cloud.google.com/sql/docs/postgres/connect-external-app#4_if_required_by_your_authentication_method_create_a_service_account).
   Download a JSON key to use to authenticate your connection.

## Running locally

To run this application locally, download and install the `cloud_sql_proxy` by
following the instructions [here](https://cloud.google.com/sql/docs/postgres/sql-proxy#install).

Instructions are provided below for using the proxy with a TCP connection or a Unix Domain Socket.
On Linux or Mac OS you can use either option, but on Windows the proxy currently requires a TCP
connection.

### Launch proxy with TCP

To run the sample locally with a TCP connection, set environment variables and launch the proxy as
shown below.

#### Linux / Mac OS

Use these terminal commands to initialize environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service/account/key.json
export INSTANCE_HOST='127.0.0.1'
export DB_PORT='5432'
export DB_USER='<YOUR_DB_USER_NAME>'
export DB_PASS='<YOUR_DB_PASSWORD>'
export DB_NAME='<YOUR_DB_NAME>'
```

Note: Saving credentials in environment variables is convenient, but not secure - consider a more
secure solution such as [Secret Manager](https://cloud.google.com/secret-manager/docs/overview) to
help keep secrets safe.

Then use this command to launch the proxy in the background:

```bash
./cloud_sql_proxy -instances=<PROJECT-ID>:<INSTANCE-REGION>:<INSTANCE-NAME>=tcp:5432 -credential_file=$GOOGLE_APPLICATION_CREDENTIALS &
```

### Launch proxy with Unix Domain Socket

NOTE: this option is currently only supported on Linux and Mac OS. Windows users should use the
[Launch proxy with TCP](#launch-proxy-with-tcp) option.

To use a Unix socket, you'll need to create a directory and give write access to the user running
the proxy. For example:

```bash
sudo mkdir /path/to/the/new/directory
sudo chown -R $USER /path/to/the/new/directory
```

Use these terminal commands to initialize other environment variables as well:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service/account/key.json
export INSTANCE_UNIX_SOCKET='./cloudsql/<PROJECT-ID>:<INSTANCE-REGION>:<INSTANCE-NAME>'
export DB_USER='<YOUR_DB_USER_NAME>'
export DB_PASS='<YOUR_DB_PASSWORD>'
export DB_NAME='<YOUR_DB_NAME>'
```

Note: Saving credentials in environment variables is convenient, but not secure - consider a more
secure solution such as [Secret Manager](https://cloud.google.com/secret-manager/docs/overview) to
help keep secrets safe.

Then use this command to launch the proxy in the background:

```bash
./cloud_sql_proxy -dir=./cloudsql --instances=<PROJECT-ID>:<INSTANCE-REGION>:<INSTANCE-NAME> --credential_file=$GOOGLE_APPLICATION_CREDENTIALS &
```

### Testing the application

Next, setup install the requirements into a virtual environment:

```bash
virtualenv --python python3 env
source env/bin/activate
pip install -r requirements.txt
```

Finally, start the application:

```bash
python app.py
```

Navigate towards `http://127.0.0.1:8080` to verify your application is running correctly.

```

```
