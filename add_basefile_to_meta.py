import csv
import re
import yaml

from github import Github 
from pathlib import Path




def update_repo(g, pecha_id, file_path, commit_msg, new_content):
    try:
        repo = g.get_repo(f"Openpecha/{pecha_id}")
        contents = repo.get_contents(f"{file_path}", ref="master")
        repo.update_file(contents.path, commit_msg, new_content, sha=contents.sha, branch="master")
        print(f'{pecha_id} update completed..')
    except:
        print(f"{pecha_id} repo not found")


def get_pagination_info(pagination_content,pagination_path):
    vol_num = Path(f"{pagination_path}").name
    paginations = pagination_content['annotations'][4:]
    for pg_uuid, pg_info in enumerate(paginations,1):
       image_group = pg_info['reference'][:-4]
       return image_group, vol_num


def get_pagination_content(g, pagination_path, pecha_id, repo):
    pagination_path = pagination_path.path
    pagination_content = repo.get_contents(f"./{pagination_path}/pagination.yml")
    pagination_content = pagination_content.decoded_content.decode()
    pagination_content = yaml.safe_load(pagination_content)
    image_group, vol_num = get_pagination_info(pagination_content, pagination_path)
    return image_group, vol_num

def get_layers_of_opf(g, pecha_id):
    layers = []
    pagination_info = {}
    cur_text = {}
    try:
        repo = g.get_repo(f"Openpecha/{pecha_id}")
        contents = repo.get_contents(f"./{pecha_id}.opf/layers")
        num = 1
        for content_file in contents:
            image_group, vol_num = get_pagination_content(g, content_file, pecha_id, repo)
            cur_text[f'{num}'] = {
                'Image_group': image_group,
                'Vol': vol_num
            }
            pagination_info.update(cur_text)
            num += 1
            cur_text = {}
    except:
        print('Repo not found')
    return pagination_info

def get_meta_from_opf(g, pecha_id):
    try:
        repo = g.get_repo(f"Openpecha/{pecha_id}")
        contents = repo.get_contents(f"./{pecha_id}.opf/meta.yml")
        return contents.decoded_content.decode()
    except:
        print('Repo Not Found')
        return ''

def get_new_meta( meta_data, pagination_info):
    volumes = meta_data['source_metadata']['volume']
    for info_num, pg_info in pagination_info.items():
        image_group = pg_info['Image_group']
        vol_num = pg_info['Vol']
        for vol_id, vol_info in volumes.items():
            if vol_info['image_group_id'] == image_group:
                vol_info['base_file'] = f"{vol_num}.txt"
                break
    meta_yml = yaml.safe_dump(meta_data, default_flow_style=False, sort_keys=False,  allow_unicode=True)
    return meta_yml



if __name__ == "__main__":
    token = ""
    g = Github(token)
    commit_msg = 'meta updated'
    pecha_id = "P008105"
    file_path = f"./{pecha_id}.opf/meta.yml"
    old_meta_data = get_meta_from_opf(g, pecha_id)
    old_meta_data = yaml.safe_load(old_meta_data)
    pagination_info = get_layers_of_opf(g, pecha_id)
    new_meta_data = get_new_meta(old_meta_data, pagination_info)
    update_repo(g, pecha_id, file_path, commit_msg, new_meta_data)
    print(f'INFO: {pecha_id} meta updated..')

