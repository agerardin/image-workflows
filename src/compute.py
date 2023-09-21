from token_service import get_access_token
from pathlib import Path
import json
import requests
import utils 

if __name__ == "__main__":
    token = get_access_token()

    WORKING_DIR = Path("").absolute() # preprend to all path to make them absolute
    compute_path = WORKING_DIR / "data" /  Path("compute")

    for workflow in compute_path.iterdir():
        if (workflow.is_file() and workflow.suffix == ".json"):
            print(f"sending to compute : {workflow}")
            workflow = utils.load_json(workflow)
            # workflow = utils.load_json(Path("data/out/compute_workflow.json"))
            # workflow = utils.load_json(Path("data/out/compute_compatibility.json"))

            headers = {'Authorization': f"Bearer {token}"}
            r = requests.get("https://compute.ci.ncats.io/compute/health/argo", headers=headers)
            print(r)

            url = 'https://compute.ci.ncats.io/compute/workflows'
            x = requests.post(url, headers=headers, json = workflow)
            print(x.text)
