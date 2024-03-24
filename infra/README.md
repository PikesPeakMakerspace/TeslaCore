# infrastructure setup
1. github action access to deployment
2. docker
3. secrets

## github action access to deployment
setup vpn access for github actions runner
* make a user and password for the bot to access internal network

setup ssh access for github actions runner
* make a non-privileged user and ssh pub/priv key for the bot to access deployment server

configure `/infra/deploy_env.sh`
* set the vpn host and port

configure `/infra/deploy_secret.sh`
* set the vpn psk, user, and password
* set the ssh LAN host and LAN port
* set the ssh user and ssh priv key



