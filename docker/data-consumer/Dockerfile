FROM ghcr.io/metpx/sarracenia:latest

RUN mkdir -p /data/wis2node/cache/home/sarra
RUN ln -s /root/.cache /data/wis2node/cache/home/sarra

COPY ./config /root/.config/sr3

CMD sh -c "whoami && sr3 start && sleep infinity"
