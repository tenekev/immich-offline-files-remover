FROM python:3.12-alpine

COPY *.sh *.py *.txt /script/

RUN pip install --no-cache-dir -r /script/requirements.txt \
    && chmod +x /script/setup_cron.sh /script/immich_auto_remove_offline_files.sh \
    && rm -rf /tmp/* /var/tmp/* /var/cache/apk/* /var/cache/distfiles/*

WORKDIR /script
CMD ["sh", "-c", "/script/setup_cron.sh && crond -f"]