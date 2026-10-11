import json
from pathlib import Path
from typing import Any

import aiofiles


async def read_config(conf_path: Path) -> dict[str, Any]:
	async with aiofiles.open(conf_path) as file:
		config_raw = await file.read()
		config_json = json.loads(config_raw)
		return config_json

async def write_config(conf: dict[str, Any], conf_path: Path):
	async with aiofiles.open(conf_path) as file:
		config_raw = json.dumps(conf)
		await file.write(config_raw)
