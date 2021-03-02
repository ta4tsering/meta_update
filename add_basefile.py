from pathlib import Path
import yaml

def write_to_meta(meta_content, image_group, vol_num):
    volumes = meta_content['source_metadata']['volume']
    for vol_id, vol_info in volumes.items():
        if vol_info['image_group_id'] == image_group:
            vol_info['basefile'] = f"{vol_num}.txt"
            new_meta = yaml.safe_dump(meta_content)
            return new_meta  

def get_pagination_info(pagination_content,pagination_path):
    vol_num = pagination_path.name
    paginations = pagination_content['annotations'][4:]
    for test_id, test in enumerate(paginations,1):
       reference = test['reference']
       image_group = (reference[:-4])
       return image_group, vol_num

def get_pagination_content(pagination_path):
    pagination_content = Path(f"{pagination_path}/pagination.yml").read_text(encoding="utf-8")
    pagination_content = yaml.safe_load(pagination_content)
    image_group, vol_num = get_pagination_info(pagination_content, pagination_path)
    return image_group, vol_num

if __name__ == "__main__":
    meta_file = Path(f"../P008105/P008105.opf/meta.yml").read_text(encoding = "utf-8")
    meta_content = yaml.safe_load(meta_file)
    pagination_files = list(Path(f"../P008105/P008105.opf/layers").iterdir())
    pagination_files.sort()
    for pagination_num, pagination_path in enumerate(pagination_files,1):
        image_group, vol_num = get_pagination_content(pagination_path)
        new_meta = write_to_meta(meta_content, image_group, vol_num)
        Path(f"../P008105/P008105.opf/meta.yml").write_text(new_meta, encoding='utf-8')

