import csv
import json
import logging
import re
import requests
import yaml

from github import Github
from pathlib import Path

logging.basicConfig(
    filename="description_added.log",
    format="%(levelname)s: %(message)s",
    level=logging.INFO
)
def notifier(msg):
    logging.info(msg)

def get_title(meta):
    if meta['source_metadata']['title'] != None:
        title = meta['source_metadata']['title']
        return title
    else:
        return None

def get_author(meta):
    if meta['source_metadata']['authors'] != '':
        authors = meta['source_metadata']['authors']
        author = ''.join(authors)
        return author
    else:
        return None

def get_bdrcid(meta):
    if meta['source_metadata']['id'] != None:
        bdrcid = meta['source_metadata']['id']
        return bdrcid
    else:
        return None

def get_work_id(brdcid):
    work_id = bdrcid[4:]
    return work_id

if __name__=="__main__":
    token = "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"
    g = Github(token)
    headers = {"Authorization": f"bearer {token}"}
    with open("catalog.csv", newline="") as csvfile:
        pechas = list(csv.reader(csvfile, delimiter=","))
        for pecha in pechas[4:9]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            repo = g.get_repo(f"Openpecha/{pecha_id}")
            contents = repo.get_contents(f"./{pecha_id}.opf/meta.yml")
            meta_content = contents.decoded_content.decode()
            meta_content = yaml.safe_load(meta_content)
            title = get_title(meta_content)
            author = get_author(meta_content)
            bdrcid = get_bdrcid(meta_content)
            work_id = get_work_id(bdrcid)
            if author != None:
                data = {"description": f"{title} {author} Tsadra ID: {bdrcid}"}
            else:
                data = {"description": f"{title } Tsadra ID: {work_id}"}
            response = requests.patch(f"https://api.github.com/repos/Openpecha/{pecha_id}", headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                notifier(f"{pecha_id} Description added successfully")
                print(f"{pecha_id} Description added successfully")
            else :
                notifier(f"{pecha_id} description not added due to status code {response.status_code}")
                print(f"{pecha_id} description not added due to status code {response.status_code}")