import os
import signal
import subprocess
import sys
from json import JSONDecodeError
from pathlib import Path

import yaml
from dotenv import load_dotenv

from botbuilder.template import render_template


def get_variable_from_dot_env(var_name):
    load_dotenv()
    return os.environ.get(var_name)


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
    config_node_id = "tg-bot-config"
    config_node_exists = tg_bot_config_block_exists = False

    if not user_data["drawflow"]["Home"]["data"]:
        return False, "Empty data"

    start_node_count = 0
    for node_id, node_data in user_data["drawflow"]["Home"]["data"].items():
        if node_data["class"] == start_node_id:
            start_node_count += 1
            if not node_data["data"]["text"]:
                return False, f"Block text is missing"

        if node_data["class"] == config_node_id:
            config_node_exists = True
            if not node_data["data"]["token"]:
                return False, f"Telegram API Token is missing"

    if start_node_count != 1:
        return False, f"[Telegram Bot] Start block is missing"
    if not config_node_exists:
        return False, f"[Telegram Bot] Config block is missing"

    return True, ""


def parse_data(data):
    res = {'blocks': {}}
    for block_id, block_data in data['drawflow']['Home']['data'].items():
        if block_data['name'] == 'tg-bot-config':
            res['config'] = {
                'api_token': block_data['data']['token']
            }
        elif block_data['name'] == 'tg-bot-start':
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


def get_process_args_by_pid(pid):
    """
    Returns process name (with arguments) by pid
    @param pid: int, process PID
    """
    p = subprocess.Popen([f"ps -p {pid} -o args="], stdout=subprocess.PIPE, shell=True)
    raw_res = p.communicate()[0]
    res = raw_res.decode().split(' ', 1)
    if len(res) > 1:
        res = res[1].split()
    else:
        res = []
    return res


def process_login_data(login_data: bytes):
    res = {}
    login_data_list = login_data.decode().split("&")
    for item in login_data_list:
        if item:
            res[item.split("=")[0]] = item.split("=")[1]

    return res


def do_deploy_bot(bot_uuid=None):
    is_success = True
    error_msg = ""

    pids_raw = subprocess.check_output(['pidof', 'python'])
    pids = [int(x) for x in pids_raw.decode().split()]
    for pid in pids:
        args = get_process_args_by_pid(pid)
        try:
            py_script_name = args[0].split('/')[-1]
            if py_script_name == "bot.py":
                print(f"Killing {py_script_name} with PID:{pid}")
                os.kill(pid, signal.SIGTERM)
        except:
            pass

    p = subprocess.Popen([sys.executable, "./rendered/bot.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Started bot process with PID:{p.pid}")
    stdout, stderr = p.communicate()
    if stderr and "telegram.error.InvalidToken" in stderr.decode():
        print("INVALID TOKEN")
        is_success = False
        error_msg = "Invalid Telegram Token"

    return is_success, error_msg
