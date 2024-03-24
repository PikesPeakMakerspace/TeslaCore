# deploy_env.sh
# define all of the following env vars for deployment
export VPN_HOST=ppmsvpn.mooo.com
export VPN_PORT=1701






# check all env vars have been defined
envvars=(VPN_HOST VPN_PORT)
good=1
for s in ${envvars[@]}; do
    v=$(printenv "${s}")
    if [ -z "${v}" ]; then
        echo "error: please define deploy_env.sh: ${s}"
        good=0
    fi
done
if [ "${good}" -eq 1 ]; then
    export GOT_DEPLOY_ENV=1
fi

# source secrets from file or env
if [ -r deploy_secret.sh ]; then
    source deploy_secret.sh
fi

# check all secrets have been defined
secrets=(VPN_PSK VPN_USER VPN_PASSWD)
good=1
for s in ${secrets[@]}; do
    v=$(printenv "${s}")
    if [ -z "${v}" ]; then
        echo "error: please define deploy_secret.sh: ${s}"
        good=0
    fi
done
if [ "${good}" -eq 1 ]; then
    export GOT_DEPLOY_SECRETS=1
fi

