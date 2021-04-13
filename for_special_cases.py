import csv
import re
import yaml
import logging

from github import Github 
from pathlib import Path

logging.basicConfig(
    filename="special_pechas.log",
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)

def notifier(msg):
    logging.info(msg)


def check_for_base_file(meta_data, pecha_id):
    source_meta = meta_data['source_metadata']
    key = 'volumes'
    if key in source_meta.keys():
        if meta_data["source_metadata"]["volumes"] != (None or {} or ''):
            volumes =  meta_data["source_metadata"]["volumes"]
            key = 'base_file'
            for vol_id, vol_info in volumes.items():
                if key in vol_info.keys(): 
                    print(f"{pecha_id} updated")
                    break
                else:
                    notifier(f"{pecha_id} no base file")
                    print(f"{pecha_id} not updated")
                    break
        else:
            notifier(f"{pecha_id} volumes empty")
            print(f"{pecha_id} is empty")
    else:
        notifier(f"{pecha_id} not updated at all")
        print(f"{pecha_id} not updated")

def get_meta_from_opf(g, pecha_id):
    try:
        repo = g.get_repo(f"Openpecha/{pecha_id}")
        contents = repo.get_contents(f"./{pecha_id}.opf/meta.yml")
        return contents.decoded_content.decode()
    except:
        print(f'Repo Not Found {pecha_id}')
        return None

if __name__=='__main__':
    token = "e1cb6529dac22e62efb1df93222e757e851721b4"
    g = Github(token) 

    with open("catalog.csv", newline="") as csvfile:
        pechas = list(csv.reader(csvfile, delimiter=","))
        for pecha in pechas[3626:]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            file_path = f"./{pecha_id}.opf/meta.yml"
            old_meta_data = get_meta_from_opf(g, pecha_id)
            old_meta_data = yaml.safe_load(old_meta_data)
            if old_meta_data != None:
                check_for_base_file(old_meta_data, pecha_id)
