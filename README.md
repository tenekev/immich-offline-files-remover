# 🐳 Immich Auto Remove Offline Files - Docker Edition
This is a simple Pyhon script, dressed as a Docker container, that removes Offline Files from **External** Immich libraries. It can be used to either run the script manually, or via cronjob by providing a crontab expression to the container. The container can then be added to the Immich compose stack directly.

### 🔑 Obtaining an Immich API key
Instructions can be found in the Immich docs - [Obtain the API key](https://immich.app/docs/features/command-line-interface#obtain-the-api-key)

### 🔂 Running once
To perform a manually triggered run, use the following command:

```bash
docker run --rm -e API_URL="https://immich.mydomain.com/api/" -e API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" ghcr.io/tenekev/immich-offline-files-remover:latest /script/immich_auto_remove_offline_files.sh
```

### 🔁 Running on a schedule
```bash
docker run --name immich-offline-files-remover -e TZ="Europe/Sofia" -e CRON_EXPRESSION="0 * * * *" -e API_URL="https://immich.mydomain.com/api/" -e API_KEY="xxxxx" ghcr.io/tenekev/immich-offline-files-remover:latest
```

### 📃 Running as part of the Immich docker-compose.yml
Adding the container to Immich's `docker-compose.yml` file:

```yml
version: "3.8"
...
services:
  immich-server:
    container_name: immich_server
  ...

  immich-offline-files-remover:
    container_name: immich-offline-files-remover
    image: ghcr.io/tenekev/immich-offline-files-remover:latest
    restart: unless-stopped
    environment:
      API_URL: http://immich_server:3001/api
      API_KEY: xxxxxxxxxxxxxxxxx               # https://immich.app/docs/features/command-line-interface#obtain-the-api-key
      CRON_EXPRESSION: "0 */1 * * *"           # Run every hour
      TZ: Europe/Sofia
```

You can still trigger the script manually by issuing the following command in the container shell:
```sh
/script/immich_auto_remove_offline_files.sh
```
Or with Docker exec:
```sh
docker exec -it immich-offline-files-remover /script/immich_auto_remove_offline_files.sh
```
## License

This project is licensed under the GNU Affero General Public License version 3 (AGPLv3) to align with the licensing of Immich, which this script interacts with. For more details on the rights and obligations under this license, see the [GNU licenses page](https://opensource.org/license/agpl-v3).

