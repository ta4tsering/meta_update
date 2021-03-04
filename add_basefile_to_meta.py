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



def check_volumes(meta_data, pagination_info,pecha_id):
    volumes = meta_data['source_metadata']['volumes']
    if volumes != (None | '') :
        for info_num, pg_info in pagination_info.items():
            image_group = pg_info['Image_group']
            vol_num = pg_info['Vol']
            for vol_id, vol_info in volumes.items():
                if vol_info['image_group_id'] == image_group:
                    vol_info['base_file'] = f"{vol_num}.txt"
                    break
    else:
        console.log(pech_id)
    return meta_data

def check_initial_type(initial_creation_type, meta_data, pagination_info, pecha_id):
    if initial_creation_type == 'ocr':
                meta_data['source_metadata']['volumes'] = meta_data['source_metadata']['volume']
                del meta_data['source_metadata']['volume']
                new_meta = check_volumes(meta_data,pagination_info,pecha_id)
                return new_meta


def get_new_meta( meta_data, pagination_info, pecha_id):
    key = list(meta_data.keys())[0] 
    if key == 'id':
        if meta_data['id'] != pecha_id:
            meta_data['id'] = pecha_id
            meta_data = check_initial_type(meta_data['initial_creation_type'], meta_data, pagination_info, pecha_id)
    if key == 'initial_creation_type':
        meta_data['id'] = pecha_id
        meta_data = check_initial_type(meta_data['initial_creation_type'], meta_data, pagination_info, pecha_id)     
    meta_yml = yaml.safe_dump(meta_data, default_flow_style=False, sort_keys=False,  allow_unicode=True)
    return meta_yml

def get_image_group_and_vol_num(pagination_content,pagination_path):
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
    image_group, vol_num = get_image_group_and_vol_num(pagination_content, pagination_path)
    return image_group, vol_num


def get_pagination_info(g, pecha_id):
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

def update_ebook_meta(meta_data):
    key = list(meta_data.keys())[0] 
    if key == 'ebook_metadata':
        meta_data['id'] = pecha_id
        meta_data['initial_creation_type'] = 'ebook'
        meta_data['source_metadata'] = meta_data['ebook_metadata']
        del meta_data['ebook_metadata']
        meta_data['source_metadata']['id'] = meta_data['source_metadata']['sku']
        del meta_data['source_metadata']['sku']
        web_meta = meta_data['web_metadata']
        del meta_data['web_metadata']
        meta_data['web_metadata'] = web_meta
        meta_yml = yaml.safe_dump(meta_data, default_flow_style=False, sort_keys=False,  allow_unicode=True)
        return meta_yml
    elif key == 'source_metadata':
        meta_data['id'] = pecha_id
        meta_data['initial_creation_type'] = 'ebook'
        meta_yml = yaml.safe_dump(meta_data, default_flow_style=False, sort_keys=False,  allow_unicode=True)
        return meta_yml
    else:
        return None



def get_meta_from_opf(g, pecha_id):
    try:
        repo = g.get_repo(f"Openpecha/{pecha_id}")
        contents = repo.get_contents(f"./{pecha_id}.opf/meta.yml")
        return contents.decoded_content.decode()
    except:
        print('Repo Not Found')
        return ''


if __name__ == "__main__":
    token = '894e1585a5b4b606f83a45684185669809cf786a'
    g = Github(token)
    commit_msg = 'meta updated'
    pecha_id = "P000103"
    file_path = f"./{pecha_id}.opf/meta.yml"
    old_meta_data = get_meta_from_opf(g, pecha_id)
    old_meta_data = yaml.safe_load(old_meta_data)
    new_ebook_meta = update_ebook_meta(old_meta_data)
    if new_ebook_meta == None:
        pagination_info = get_pagination_info(g, pecha_id)
        new_meta_data = get_new_meta(old_meta_data, pagination_info, pecha_id)
        if new_meta_data != None:
            update_repo(g, pecha_id, file_path, commit_msg, new_meta)
    else:
        update_repo(g, pecha_id, file_path, commit_msg, new_ebook_meta)
    
    print(f'INFO: {pecha_id} meta updated..')

