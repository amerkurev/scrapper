# HTTPS and Authentication
Enhance the security of your Scrapper deployment with HTTPS and Basic Authentication by integrating [Caddy server](https://github.com/caddyserver/caddy).

This approach is recommended for instances exposed to the internet and can be configured with minimal effort using Docker Compose.

## Configuring Caddy for Security

Caddy handles SSL certificate issuance and renewal through Let's Encrypt and supports Basic Authentication for added security.

To configure Caddy with Scrapper:

### 1. Customize the [Caddyfile](https://github.com/amerkurev/scrapper/blob/master/Caddyfile) 

Update `scrapper.localhost` to your domain name. For Basic Authentication, generate a secure hashed password with [`caddy hash-password`](https://caddyserver.com/docs/command-line#caddy-hash-password) and update the Caddyfile with this hash.
To generate a password hash:

```console
caddy hash-password -plaintext 'your_new_password'
```
    
Replace `your_new_password` with a strong password, then insert the hashed result into the [Caddyfile](https://github.com/amerkurev/scrapper/blob/master/Caddyfile).

### 2. Launch with Docker Compose
With your [`docker-compose.yml`](https://github.com/amerkurev/scrapper/blob/master/docker-compose.yml) and edited Caddyfile ready, deploy the services:
```console
docker compose up -d
```

## Secure Access to Scrapper

Once deployed, access Scrapper at `https://your_domain`. You'll be asked for the username and password specified in the Caddyfile.

## Automatic Certificate Renewal

Caddy automatically renews SSL certificates before they expire, requiring no action from the user. Enjoy uninterrupted HTTPS protection for your Scrapper instance without manual intervention.
