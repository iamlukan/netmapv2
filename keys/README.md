# SSH Credentials

Place your private key here with the name `id_ed25519`.

This file is mounted by the `netmap-tunnel` container to establish a connection to the OCS Gateway.

## Security
- Do not commit your private key to Git.
- This directory is (or should be) in `.gitignore`.
