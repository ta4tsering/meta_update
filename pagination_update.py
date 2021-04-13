import csv
import shutil
import logging
import os
import re
import uuid
import yaml



from github import Github 
from pathlib import Path 

DATA_PATH = Path("./layers")

logging.basicConfig(
    filename="pagination_updated.log",
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)

def notifier(msg):
    logging.info(msg)

def update_repo(g, pecha_id, file_path, commit_msg):
    try:
        new_content = os.listdir(Path(f"./layers/"))
        repo = g.get_repo(f"Openpecha/{pecha_id}")
        contents = repo.get_contents(f"{file_path}", ref="master")
        repo.update_file(contents.path, commit_msg, new_content, sha=contents.sha, branch="master")
        notifier( f'Pecha id :{pecha_id} updated ')
    except Exception as e:
        notifier( f'Pecha id :{pecha_id} not updated with error {e}')

def get_new_annotations(pagination_content,pagination_path):
    vol_num = Path(f"{pagination_path}").name
    new_pagination = {}
    pagination = {}
    paginations = pagination_content['annotations']
    if paginations != []:
        for pg_uuid, pg_info in enumerate(paginations,1):
            uid = pg_info['id']
            new_pagination[f"{uid}"] = { 
                'page_index': pg_info['page_index'],
                'page_info': pg_info['page_info'],
                'reference': pg_info['reference'],
                'span':{
                    'start': pg_info['span']['start'],
                    'end': pg_info['span']['end']
                }
            }
            pagination.update(new_pagination)
            new_pagination = {}
        return pagination, vol_num
    else:
        notifier( f'Pecha id :{pecha_id} vol_num:{vol_num} empty pagination')
        print( f'Pecha id :{pecha_id} vol_num:{vol_num} empty pagination')
        return None


def get_pagination_content(g, content_file, pecha_id, repo):
    pagination_path = content_file.path
    pagination_content = repo.get_contents(f"./{pagination_path}/pagination.yml")
    pagination_content = pagination_content.decoded_content.decode()
    pagination_content = yaml.safe_load(pagination_content)
    pagination, vol_num = get_new_annotations(pagination_content, pagination_path)
    return pagination, pagination_content, pagination_path, vol_num

def clean_dir(layers_output_dir):
    if layers_output_dir.is_dir():
            shutil.rmtree(str(layers_output_dir))

def get_new_layers(g, pecha_id):
    repo = g.get_repo(f"Openpecha/{pecha_id}")
    contents = repo.get_contents(f"./{pecha_id}.opf/layers")
    for content_file in contents:
        pagination, pagination_content, pagination_path, vol_num = get_pagination_content(g, content_file, pecha_id, repo)
        if pagination != None:
            del pagination_content['annotations']
            pagination_content[f'annoatations'] = pagination
            content_yml = yaml.safe_dump(pagination_content, default_flow_style=False, sort_keys=False,  allow_unicode=True)
            layers_output_dir = DATA_PATH / vol_num 
            layers_output_dir.mkdir(exist_ok=True, parents=True)
            Path(f"./layers/{vol_num}/pagination.yml").write_text(content_yml, encoding='utf-8')


if __name__=='__main__':
    token = ""
    g = Github(token) 
    commit_msg = "pagination_updated"
    # with open("catalog.csv", newline="") as csvfile:
    #     pechas = list(csv.reader(csvfile, delimiter=","))
    #     for pecha in pechas[954:]:
            # pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
    pecha_id = "P008165"
    file_path = f"./{pecha_id}.opf/layers"
    get_new_layers(g, pecha_id)
    update_repo(g, pecha_id,  file_path, commit_msg)
    clean_dir(DATA_PATH)
  
