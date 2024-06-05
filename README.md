# ❗A Docker image repo for [Thoroslives/immich_remove_offline_files](https://github.com/Thoroslives/immich_remove_offline_files)


# Immich Remove Offline Files
A simple way to remove orphaned offline assets from Immich's database.

This Python script assists in managing the Immich database by detecting and removing orphaned media assets. 

These orphans may occur if files are deleted from the filesystem without being properly removed from Immich. 

Orphaned assets can be checked via the repair page within the admin interface of Immich.

### Prepare Configuration
To use the script, you will need:
- An **Admin API key** from Immich for fetching reports.
- A **User-specific API key** for deleting assets.
Store these keys securely and use them as required when running the script.

Instructions for which can be found in the Immich docs - [Obtain the API key](https://immich.app/docs/features/command-line-interface#obtain-the-api-key)

### Docker
A Docker image is provided to be used as a runtime environment. It can be used to either run the script manually, or via cronjob by providing a crontab expression to the container. The container can then be added to the Immich compose stack directly.
git init

#### Run the container with Docker
To perform a manually triggered run, use the following command:

```bash
docker run --rm -e API_URL="https://immich.mydomain.com/api/" -e API_KEY_ADMIN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" -e API_KEY_USER="xxxxxxxxxxxxxxxxxxxxxxxxxxxxx" ghcr.io/tenekev/immich-offline-files-remover:latest /script/immich_auto_remove_offline_files.sh
```
To make a container: 

```bash
docker run --name immich-offline-files-remover -e TZ="Europe/Berlin" -e CRON_EXPRESSION="0 * * * *" -e API_URL="https://immich.mydomain.com/api/" -e API_KEY_ADMIN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" -e API_KEY_USER="xxxxxxxxxxxxxxxxxxxxxxxxxxxxx" ghcr.io/tenekev/immich-offline-files-remover:latest
```

### Run the container with Docker-Compose

Adding the container to Immich's `docker-compose.yml` file:
```yml
version: "3.8"

#
# WARNING: Make sure to use the docker-compose.yml of the current release:
#
# https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml
#
# The compose file on main may not be compatible with the latest release.
#

name: immich

services:
  immich-server:
    container_name: immich_server
    volumes:
     - /path/to/my/photos:/external_libs/photos
  ...
  immich-offline-files-remover:
    container_name: immich-offline-files-remover
    image: ghcr.io/tenekev/immich-offline-files-remover:latest
    restart: unless-stopped
    environment:
      API_URL: http://immich_server:3001/api
      API_KEY_ADMIN: xxxxxxxxxxxxxxxxx
      API_KEY_USER: xxxxxxxxxxxxxxxxx
      CRON_EXPRESSION: "0 * * * *"
      TZ: Europe/Berlin

```

## CMD Usage

### Optional Arguments

- `--admin_apikey [ADMIN_API_KEY]`: Immich admin API key for fetching reports.
- `--user_apikey [USER_API_KEY]`: User-specific Immich API key for deletion.
- `--immichaddress [IMMICH_ADDRESS]`: Full web address for Immich, including protocol and port.
- `--no_prompt`: Enables deleting orphaned media assets without confirmation.

### Examples
```bash
python3 immich_remove_offline_files.py --admin_apikey "your_admin_api_key" --user_apikey "your_user_api_key" --immichaddress "http://IPADDRESS:port"
```

## How It Works

The script performs the following steps:
1. Fetches a report of orphaned media assets from the Immich server using the admin API key.
2. Displays the list of orphaned assets and asks for confirmation before deletion (unless `--no_prompt` is used).
3. Deletes the orphaned assets using the user API key, provided the confirmation was `yes`.

## Error Handling

The script includes basic error handling to manage common issues such as connectivity problems, invalid API keys, and permissions issues. 

Below are some of the errors you might encounter and the suggested steps to resolve them:

### Common Errors

- **Connection Errors**: If the script cannot reach the Immich server, ensure that the server address is correct and that your network connection is stable.
- **API Key Errors**: If you receive an error related to the API key, check that your API keys are correct and have the necessary permissions for the operations you are attempting.
- **Permission Errors**: Ensure the user API key has appropriate permissions to delete assets. Since the results will display all orphaned assets located in the Immich database using the admin API, the delete API of the user only allows deletion of the assets that the user has permission to manage. If you encounter a `400 error`, it may be necessary to assess the assets to determine which library they are located in and use the corresponding user API key that has the necessary permissions to delete those specific assets.

### Debugging Tips

- Ensure that all prerequisites are correctly installed and up-to-date.
- Check the command line for typos in your script arguments.
- Use the verbose or debug mode if available to get more detailed log output that can help in diagnosing problems.

## Contributions

Contributions to this project are welcome! Please feel free to submit issues, forks, or pull requests.

## License

This project is licensed under the GNU Affero General Public License version 3 (AGPLv3) to align with the licensing of Immich, which this script interacts with. For more details on the rights and obligations under this license, see the [GNU licenses page](https://opensource.org/license/agpl-v3).

