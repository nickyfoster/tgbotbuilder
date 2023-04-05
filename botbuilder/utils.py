from json import JSONDecodeError
from pathlib import Path

import yaml

from botbuilder.template import render_template


def load_yml(file):
    file = Path(file)
    try:
        with file.open() as f:
            d = yaml.full_load(f)
            if d is None:
                d = dict()
    except (FileNotFoundError, JSONDecodeError) as e:
        print(f"Error opening YAML file: {e}")
        d = {}
    return d


def get_blocks_file(blocks_filename):
    return load_yml(Path(__file__).parent / blocks_filename)


def validate_user_data(user_data) -> tuple[bool, str]:
    start_node_id = "tg-bot-start"
    if not user_data["drawflow"]["Home"]["data"]:
        return False, "Empty data"

    start_node_count = 0
    for node_id, node_data in user_data["drawflow"]["Home"]["data"].items():
        if node_data["class"] == start_node_id:
            start_node_count += 1

    if start_node_count != 1:
        return False, f"Invalid {start_node_id} node count"

    return True, ""


def parse_data(data):
    res = {'blocks': {}}
    for block_id, block_data in data['drawflow']['Home']['data'].items():
        if block_data['name'] == 'tg-bot-start':
            try:
                next_block = int(block_data['outputs']['output_1']['connections'][0]['node'])
            except IndexError:
                next_block = None
            res['blocks']['start'] = {
                'text': block_data['data']['text'],
                'next_block': next_block
            }
        else:
            if block_data['data'].get('btn'):
                buttons = {}
                for output_id, output in block_data['outputs'].items():
                    if output.get('connections'):
                        btn_text = block_data['data']['btn'][output_id.split('_')[1]]

                        buttons[btn_text] = {'next_block': output['connections'][0]['node']}

            else:
                buttons = None

            res['blocks'][str(block_data['id'])] = {
                'text': block_data['data']['text'],
                'buttons': buttons,
                'next_block': None
            }

    return res


def render_bot(data):
    blocks = parse_data(data)
    print("parsed:", blocks)
    rendered = render_template(blocks)
    with open(Path(__file__).parent / "rendered/bot.py", "w") as f:
        f.write(rendered)
    print("Template created!")
