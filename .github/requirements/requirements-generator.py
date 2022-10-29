from __future__ import annotations

import configparser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if (BASE_DIR / "Pipfile").exists():
    config = configparser.ConfigParser()
    config.read(BASE_DIR / "Pipfile")
    config_dict = config._sections["packages"]
    config_dict.update(config._sections["dev-packages"])
    list_req = []
    for i in config_dict:
        name = i.strip('"')
        version = None
        if config_dict[i].startswith("{"):
            formatted_value = config_dict[i].strip("{").strip("}").split(",")
            for i in formatted_value:
                if i.startswith("extras"):
                    name = name.strip() + i.split("=")[1].strip().strip('"').replace(
                        '["',
                        "[",
                    ).replace('"]', "]")
                if i.startswith("version"):
                    version = name.strip() + "==" + i.split("=")[1].strip().strip('"')
                if i.startswith("git"):
                    name = "git+" + i.split("=")[1].strip().strip('"')
                    if not name.endswith(".git"):
                        name = name + ".git"
        list_req.append(name + "\n")
    with open(BASE_DIR / ".github/requirements/requirements.txt", "w") as f:
        f.writelines(list_req)
