import csv
import re
import yaml
import logging

from github import Github
from pathlib import Path


logging.basicConfig(
    filename="meta_with_no_base.log",
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)

def notifier(msg):
    logging.info(msg)

def check_for_base(meta, pecha_id):
    source_meta = meta['source_metadata']
    out_key = 'volumes'
    if out_key in source_meta.keys():
        if source_meta['volumes'] != ({} or ''):
            volumes = source_meta['volumes']
            for vol_id, vol_info in volumes.items():
                key = 'base_file'
                if key in vol_info.keys():
                    print(f"{pecha_id} has base_file")
                    break
                else:
                    notifier(f"[{pecha_id}] has no base_file")
                    print(f"{pecha_id} has no base_file")
                    break
        else:
            print(f"[{pecha_id}] has no volumes")
    else:
        notifier(f"[{pecha_id}] meta data not updated")
        print(f"{pecha_id} has no volumes")


if __name__ == "__main__":
    token = ''
    g = Github(token)
    with open("catalog.csv", newline="") as csvfile:
        pechas = list(csv.reader(csvfile, delimiter=","))
        for pecha in pechas[3626:4302]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            repo = g.get_repo(f"Openpecha/{pecha_id}")
            contents = repo.get_contents(f"./{pecha_id}.opf/meta.yml")
            meta_content = contents.decoded_content.decode()
            meta_content = yaml.safe_load(meta_content)
            check_for_base(meta_content, pecha_id)
    
