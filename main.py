from github import Github
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yaml
import re
import os
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class RequestContentType(BaseModel):
    image: str
    version: str

@app.post('/update-image')

async def update_image(request: RequestContentType):
    """Endpoint to update the version of a specified image in .yaml files in the GitHub repository.

    Args:
        request (RequestContentType): 
            JSON payload with two fields: image (str) and version (str)

    Returns:
        dict: A JSON response with a message listing the updated files.
            

    Raises:
        HTTPException: 
            - 404 if no .yaml or .yml files are found or no files match the provided image.
            - 500 if an unexpected error occurs (e.g., GitHub API failure).
    """
    try:
        gh = Github(os.getenv('githib_token'))
        repo = gh.get_repo('VesAnit/refty-infra-test')

        file_access = repo.get_contents("")
        yaml_files = [file for file in file_access if file.path.endswith(('.yaml', '.yml'))]

        if not yaml_files:
            raise HTTPException(status_code = 404, detail = '.yaml or .yml files not found')
            

        update_files = []

        for file in yaml_files:
            logger.info('Processing file: %s', file.path)
            file_content = repo.get_contents(file.path)
            try:
                decoded_content = file_content.decoded_content.decode('utf-8')
                yaml_dict = yaml.safe_load(decoded_content) # The YAML structure is converted to a dict format for version upd

                # Check the structure of .yaml
                if not isinstance(yaml_dict, dict) or \
                   "spec" not in yaml_dict or \
                   "template" not in yaml_dict["spec"] or \
                   "spec" not in yaml_dict["spec"]["template"] or \
                   "containers" not in yaml_dict["spec"]["template"]["spec"] or \
                   not yaml_dict["spec"]["template"]["spec"]["containers"]:
                    logger.info("Skipping file %s: invalid YAML structure", file.path)
                    continue 

                make_commit = False
                for container in yaml_dict["spec"]["template"]["spec"]["containers"]:
                    if 'image' not in container:
                        logger.info('Skipping container in %s: no image field', file.path)
                        continue
                    
                    current_image = container['image']
                    match = re.match(r"(.+):(.+)", current_image)
                    if not match:
                        continue
                    image_name, _ = match.groups() # Retrieving the image name for further version upd 

                    if image_name != request.image:
                        logger.info('Skipping container in %s: image %s does not match requested %s', file.path, image_name, request.image)
                        continue
                    
                    container['image'] = f'{request.image}:{request.version}'
                    logger.info('Updated image in %s to %s:%s', file.path, request.image, request.version)
                    make_commit=True

                if not make_commit:
                    logger.info('No changes made in file: %s', file.path)
                    continue

                
                new_yaml = yaml.dump(yaml_dict, allow_unicode=True)

                repo.update_file(
                    path = file.path,
                    message = f'Image version updated to {request.version}',
                    content = new_yaml,
                    sha = file_content.sha,
                    branch = 'main'
                )
                update_files.append(file.path)
                logger.info('Successfully commited file: %s', file.path)
            
            except yaml.YAMLError as e:
                logger.error('YAML parsing error in file %s: %s', file.path, str(e))
                continue
            except Exception as e:
                logger.error('Error processing file %s: %s', file.path, str(e))
                continue

        if not update_files:
            raise HTTPException(status_code = 404, detail = 'Image not found in files')
            
        return {'message': f'Image version updated in {update_files}'}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Local test
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Swagger available here: http://0.0.0.0:8000/docs (or change port)


              
            







