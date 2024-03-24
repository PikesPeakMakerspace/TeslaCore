export FLASK_APP=app/app.py
export FLASK_DEBUG=1
source auth/Scripts/activate

if [ -r secret.sh ]; then
    source secret.sh
    export GOT_API_SECRETS=1
else
    if [ -z "${GOT_API_SECRETS}" ]; then
        echo "error: please create secret.sh to define the api secrets"
    fi
fi
