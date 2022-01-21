FROM ghcr.io/metpx/sarracenia:latest

RUN ln -s /data/wis2node/cache/home/sarra /root/.cache

COPY ./config /root/.config/sr3

CMD sh -c "whoami && sr3 start && sleep infinity"
