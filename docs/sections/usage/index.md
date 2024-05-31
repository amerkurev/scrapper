# Usage

## Getting Scrapper
The Scrapper Docker image is based on the Playwright image, which includes all the dependencies needed to run a browser in Docker and also includes the browsers themselves.
As a result, the image size is quite large, around 2 GB. Make sure you have enough free disk space, especially if you plan to take and store screenshots frequently.

To get the latest version of Scrapper, run:
```console
docker pull amerkurev/scrapper:latest
```

## Creating directories
Scrapper uses two directories on the disk. The first one is the `user_data` directory. This directory contains browser session data such as cookies and local storage.
Additionally, the cache of Scrapper's own results (including screenshots) is stored in this directory.

The second directory is `user_scripts`. In this directory, you can place your own JavaScript scripts, which you can then embed on pages through the Scrapper API.
For example, to remove ads blocks or click the "Accept Cookies" button (see the `user-scripts` parameter in the [API Reference](/sections/api) section for more information).

**Scrapper does not work from the root** user inside the container. Instead, it uses a user with UID `1001`.
Since you will be mounting the `user_data` and `user_scripts` directories from the host using [Bind Mount](https://docs.docker.com/storage/bind-mounts/), you will need to set write permissions for UID `1001` on these directories on the host. 

Here is an example of how to do this:
```console
mkdir -p user_data user_scripts

chown 1001:1001 user_data/ user_scripts/

ls -l
```
The last command (`ls -l`) should output a result similar to this:
```
drwxr-xr-x 2 1001 1001 4096 Mar 17 23:23 user_data
drwxr-xr-x 2 1001 1001 4096 Mar 17 23:23 user_scripts
```

## Managing Scrapper Cache
Over time, the Scrapper cache will grow in size, especially if you are making frequent requests with screenshots.
The scrapper's cache is stored in the `user_data/_res` directory. You will need to set up automatic clearing of this directory yourself.

For example, you could add the following task to your cron jobs:
```console
find /path/to/user_data/_res -ctime +7 -delete
```
This command will use the `find` utility to locate all files in the cache that were created more than 7 days ago. All such files will be deleted because the `find` utility accepts the `-delete` option.

This is just an example of how you might deal with the scrapper's cache growing over time. You can come up with other strategies for this and implement them yourself.
The main thing to remember is where Scrapper stores its cache data - it's in the `user_data/_res`.

## Using Scrapper
Once the directories have been created and write permissions have been set, you can run Scrapper using the following command:
```console
docker run -d -p 3000:3000 -v $(pwd)/user_data:/home/user/user_data -v $(pwd)/user_scripts:/home/user/user_scripts --name scrapper amerkurev/scrapper:latest
```
The Scrapper web interface should now be available at [http://localhost:3000/](http://localhost:3000/). Use any modern browser to access it.

To connect to Scrapper logs, use the following command:
```console
docker logs -f scrapper
```
