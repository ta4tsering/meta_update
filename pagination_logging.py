import csv
import re
import yaml
import logging
import uuid

from github import Github 
from pathlib import Path 

logging.basicConfig(
    filename="pagination_anomalies.log",
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)

def notifier(msg):
    logging.info(msg)

def get_new_annotations(pagination_content,pagination_path):
    vol_num = Path(f"{pagination_path}").name
    paginations = pagination_content['annotations']
    if paginations != []:
        for pg_uuid, pg_info in enumerate(paginations,1):
            if type(pg_info) != str:
                notifier( f'Pecha id :{pecha_id} pagination has id')
                print( f'Pecha id :{pecha_id} pagination has id')
                return True
            else:
                print( f'Pecha id :{pecha_id} pagination updated')
                return True
    else:
        notifier( f'Pecha id :{pecha_id} vol_num:{vol_num} empty pagination')
        print( f'Pecha id :{pecha_id} vol_num:{vol_num} empty pagination')
        return False


def get_pagination_content(g, pagination_path, pecha_id, repo):
    pagination_path = pagination_path.path
    pagination_content = repo.get_contents(f"./{pagination_path}/pagination.yml")
    pagination_content = pagination_content.decoded_content.decode()
    pagination_content = yaml.safe_load(pagination_content)
    answer = get_new_annotations(pagination_content, pagination_path)
    return answer


def get_pagination_info(g, pecha_id):
    repo = g.get_repo(f"Openpecha/{pecha_id}")
    contents = repo.get_contents(f"./{pecha_id}.opf/layers")
    for content_file in contents:
        answer = get_pagination_content(g, content_file, pecha_id, repo)
        if answer == True:
            break
        else:
            continue

if __name__=='__main__':
    token = ""
    g = Github(token) 

    with open("catalog.csv", newline="") as csvfile:
        pechas = list(csv.reader(csvfile, delimiter=","))
        for pecha in pechas[3626:]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            get_pagination_info(g, pecha_id)
