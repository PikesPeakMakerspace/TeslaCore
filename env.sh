export FLASK_APP=app
export FLASK_DEBUG=1
source auth/bin/activate

if [ -r secret.sh ]; then
    source secret.sh
    export GOT_API_SECRETS=1
else
    echo "error: please create secret.sh to define the api secrets"
fi
