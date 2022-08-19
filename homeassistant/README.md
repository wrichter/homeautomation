Add your homeassistant configuration into the subdirectory "config" (see kustomization.yaml)

The kustomization assumes that you built the homeassistant image locally using 
`podman build -t homeassistant .` in order to add python libs that certain used custom plugins use.