'''
description:
The directory structure:
    workspaces
    ├── folder1
    │   ├── a.grapycal
    │   ├── b.grapycal
    │   └── c.grapycal
    └── d.grapycal
becomes:
    workspaces
    ├── folder1
    │   ├── a.grapycal
    │   ├── b.grapycal
    │   ├── c.grapycal
    └─ d.grapycal
    metadata.json
where metadata.json looks like:
    {
        "dirs": [
            "folder1": {
                "files": [
                    {
                        "type": "file",
                        "name": "a.grapycal",
                        "version": "0.9.0",
                        "extensions": [grapycal_torch],
                    }
                    {
                        "type": "file",
                        "name": "b.grapycal",
                        "version": "0.9.0",
                        "extensions": [grapycal_torch],
                    }
                    {
                        "type": "file",
                        "name": "c.grapycal",
                        "version": "0.9.0",
                        "extensions": [grapycal_torch],
                    }
                ]
            },
        ]
        "files": [
            "d.grapycal": {
                "type": "file",
                "name": "d.grapycal",
                "version": "0.9.0",
                "extensions": [grapycal_torch],
            }
        ]
    }
'''

from functools import partial
import gzip
import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Any, Tuple

def read_workspace(path,metadata_only=False) -> Tuple[str,Any,Any]:
    # see if first two bytes are 1f 8b
    with open(path,'rb') as f:
        magic_number = f.read(2)
    if magic_number == b'\x1f\x8b':
        open_func = partial(gzip.open,path,'rt')
    else:
        open_func = partial(open,path,'r',encoding='utf-8')

    with open_func() as f:

        # DEPRECATED: v0.9.0 and before has no version number and metadata
        try:
            version = f.readline().strip()
            metadata = json.loads(f.readline())
        except json.decoder.JSONDecodeError:
            f.seek(0)
            version = '0.9.0'
            metadata = {}
            data = json.loads(f.read()) if not metadata_only else None
            return version, metadata, data
        
        f.seek(0)
        version = f.readline().strip()
        metadata = json.loads(f.readline())
        data = json.loads(f.readline()) if not metadata_only else None
    return version, metadata, data


def get_grapycal_files(path):
    '''
    return a list of all .grapycal files in the directory
    '''
    return list(Path(path).rglob('*.grapycal'))

def process_dir(path):
    '''
    recursively return the metadata
    '''
    folders = []
    files = []
    for p in os.listdir(path):
        full_path = os.path.join(path,p)
        if os.path.isdir(full_path):
            folders.append(process_dir(full_path))
        elif os.path.isfile(full_path) and full_path.endswith('.grapycal'):
            version, metadata, _ = read_workspace(full_path,metadata_only=True)
            metadata['name'] = p
            files.append(metadata)

    return {
        'name': os.path.basename(path),
        'files': files,
        'dirs': folders
    }

def main():
    '''
    main function
    '''
    
    # get the root directory
    root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # get the workspaces directory
    workspaces = os.path.join(root,'files')
    # get the metadata file
    metadata_file = os.path.join(root,'metadata.json')
    
    # get the metadata
    metadata = process_dir(workspaces)
    # write the metadata
    with open(metadata_file,'w') as f:
        json.dump(metadata,f,indent=4)

        

if __name__ == '__main__':
    main()