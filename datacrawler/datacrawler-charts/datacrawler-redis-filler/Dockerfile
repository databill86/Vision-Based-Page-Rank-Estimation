FROM redis:latest

COPY top100000_redis.csv /opt/apt/
COPY push_urls.sh /opt/apt/

ENTRYPOINT ["/bin/bash", "/opt/apt/push_urls.sh"]



