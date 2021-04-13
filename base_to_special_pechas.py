import csv
import re
import yaml
import logging

from github import Github
from pathlib import Path

logging.basicConfig(
    filename="meta_updated.log",
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)

def notifier(msg):
    logging.info(msg)

def update_repo(repo, pecha_id, file_path, commit_msg, new_content):
    try:
        contents = repo.get_contents(f"{file_path}", ref="master")
        repo.update_file(contents.path, commit_msg, new_content, sha=contents.sha, branch="master")
        notifier( f'Pecha id :{pecha_id} updated ')
        print( f'Pecha id :{pecha_id} updated ')
    except Exception as e:
        notifier( f'Pecha id :{pecha_id} not updated with error {e}')


def write_to_meta(meta_data, pagination_info,pecha_id):
    num = 0
    volumes = meta_data['source_metadata']['volumes']
    for info_num, pg_info in pagination_info.items():
        image_group = pg_info['Image_group']
        vol_num = pg_info['Vol']
        for vol_id, vol_info in volumes.items():
            if vol_info['image_group_id'][1:] == image_group:
                vol_info['base_file'] = f"{vol_num}.txt"
                num += 1
                break
    if num != 0:        
        meta_yml = yaml.safe_dump(meta_data, default_flow_style=False, sort_keys=False,  allow_unicode=True)
        return meta_yml
    else:
        return None

def get_image_group_and_vol_num(pagination_content,pagination_path):
    vol_num = Path(f"{pagination_path}").name
    paginations = pagination_content['annotations']
    if paginations != []:
        for pg_uuid, pg_info in enumerate(paginations,1):
            image_group = paginations[f'{pg_info}']['reference'][:-4]
            return image_group, vol_num
    else:
        return None, None


def get_pagination_content(repo, pagination_path, pecha_id):
    pagination_path = pagination_path.path
    pagination_content = repo.get_contents(f"./{pagination_path}/pagination.yml")
    pagination_content = pagination_content.decoded_content.decode()
    pagination_content = yaml.safe_load(pagination_content)
    image_group, vol_num = get_image_group_and_vol_num(pagination_content, pagination_path)
    return image_group, vol_num


def get_pagination_info(repo, pecha_id):
    layers = []
    pagination_info = {}
    cur_text = {}
    contents = repo.get_contents(f"./{pecha_id}.opf/layers")
    num = 1
    for content_file in contents:
        image_group, vol_num = get_pagination_content(repo, content_file, pecha_id)
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
   

def get_old_meta(repo, pecha_id):
    contents = repo.get_contents(f"./{pecha_id}.opf/meta.yml")
    meta_content = contents.decoded_content.decode()
    meta_content = yaml.safe_load(meta_content)
    return meta_content

if __name__ == "__main__":
    token = ''
    g = Github(token)
    commit_msg = 'meta updated'
    with open(f'./nobase.txt') as f:
        pechas = f.readlines()
        for _id in pechas[0:]:
            pecha_id = _id[:-1]
            file_path = f"./{pecha_id}.opf/meta.yml"
            repo = g.get_repo(f"Openpecha/{pecha_id}")
            meta = get_old_meta(repo, pecha_id)
            pagination_info = get_pagination_info(repo, pecha_id)
            if pagination_info != None:
                new_meta = write_to_meta(meta, pagination_info, pecha_id)
                if new_meta != None:
                    update_repo(repo, pecha_id, file_path, commit_msg, new_meta)


