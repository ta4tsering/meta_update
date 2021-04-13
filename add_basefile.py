import csv
import re
import yaml
import logging

from github import Github
from pathlib import Path

def write_to_meta(meta_content, image_group, vol_num):
    volumes = meta_content['source_metadata']['volumes']
    for vol_id, vol_info in volumes.items():
        if vol_info['image_group_id'] == image_group:
            vol_info['basefile'] = f"{vol_num}.txt"
            new_meta = yaml.safe_dump(meta_content)
            return new_meta  

def get_pagination_info(g, pecha_id, meta_data):
    layers = []
    pagination_info = {}
    cur_text = {}
    volumes = meta_data['source_metadata']['volume']
    if volumes != (None or '') :
        repo = g.get_repo(f"Openpecha/{pecha_id}")
        contents = repo.get_contents(f"./{pecha_id}.opf/layers")
        num = 1
        for content_file in contents:
            image_group, vol_num = get_pagination_content(g, content_file, pecha_id, repo)
            if image_group and vol_num != None:
                cur_text[f'{num}'] = {
                    'Image_group': image_group,
                    'Vol': vol_num
                }
                pagination_info.update(cur_text)
                num += 1
                cur_text = {}
            else:
                return None
        return pagination_info
    else:
        return None

def get_pagination_content(pagination_path):
    pagination_content = Path(f"{pagination_path}/pagination.yml").read_text(encoding="utf-8")
    pagination_content = yaml.safe_load(pagination_content)
    image_group, vol_num = get_pagination_info(pagination_content, pagination_path)
    return image_group, vol_num

if __name__ == "__main__":
    token = 'b9953a24355f8a275b523d9da4f2b62f1d0aed08'
    g = Github(token)
    commit_msg = 'meta updated'

    with open("catalog.csv", newline="") as csvfile:
        pechas = list(csv.reader(csvfile, delimiter=","))
        for pecha in pechas[104:278]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            file_path = f"./{pecha_id}.opf/meta.yml"
            meta_file = Path(f"../P008105/P008105.opf/meta.yml").read_text(encoding = "utf-8")
            meta_content = yaml.safe_load(meta_file)
            pagination_files = list(Path(f"../P008105/P008105.opf/layers").iterdir())
            pagination_files.sort()
            for pagination_num, pagination_path in enumerate(pagination_files,1):
                image_group, vol_num = get_pagination_content(pagination_path)
                new_meta = write_to_meta(meta_content, image_group, vol_num)
                Path(f"../P008105/P008105.opf/meta.yml").write_text(new_meta, encoding='utf-8')

