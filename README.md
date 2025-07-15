# GitHub YAML Image Updater

This is a FastAPI application that updates Docker image versions in `.yaml` or `.yml` files in a GitHub repository. 
It processes Kubernetes deployment files, modifies the `image` field in the `spec.template.spec.containers` section, and commits changes to the repository.

## Features
- Updates Docker image versions in YAML files in the repository (`VesAnit/refty-infra-test` for example)
- Supports POST requests with JSON payload containing `image` and `version`
- Validates YAML structure and skips invalid files
- Logs processing steps and errors for debugging
- Uses Github API for file operations

### How to use
To use the service:
- Run python main.py in your terminal
- Open http://0.0.0.0:8000/docs in your browser to access the Swagger UI
- Click "Try it out", enter the image and version, and press "Execute" to send the request
  
Swagger available here: http://0.0.0.0:8000/docs (but if this port is busy you may need to change the port)
