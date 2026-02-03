FROM alpine:latest

# Install SSH Client during build
RUN apk add --no-cache openssh-client

# Prepare entrypoint
WORKDIR /root
COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh

CMD ["/root/entrypoint.sh"]
