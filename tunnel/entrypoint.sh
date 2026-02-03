#!/bin/sh

# Ensure .ssh dir exists
mkdir -p /root/.ssh

# Copy the key if it exists in the volume mount
if [ -f /root/ssh/id_ed25519 ]; then
    cp /root/ssh/id_ed25519 /root/.ssh/id_ed25519
    chmod 600 /root/.ssh/id_ed25519
    echo "SSH Key installed."
else
    echo "ERROR: /root/ssh/id_ed25519 not found. Did you mount the volume?"
    # Sleep to prevent loop crash, allowing user to inspect logs
    sleep infinity
fi

echo "Starting SSH Tunnel to ${SSH_HOST}..."
echo "User: ${SSH_USER}"
echo "Forwarding: 0.0.0.0:3306 -> 127.0.0.1:3306"

# Start SSH
# -N: Do not execute a remote command (Forward only)
# -o StrictHostKeyChecking=no: Avoid interactive prompt
# -o ConnectTimeout=10: Fail fast if host down
# -o ServerAliveInterval=60: Keepalive
# -L: Port forward (LocalPort:RemoteHost:RemotePort)
# We map container 3306 to remote localhost 3306 (assuming DB is on the jumpbox)
exec ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=10 \
    -o ServerAliveInterval=60 \
    -N \
    -i /root/.ssh/id_ed25519 \
    -L 0.0.0.0:3306:127.0.0.1:3306 \
    ${SSH_USER}@${SSH_HOST}
