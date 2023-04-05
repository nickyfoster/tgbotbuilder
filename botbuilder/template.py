from pathlib import Path

import jinja2


def render_template(template_data):
    template_loader = jinja2.FileSystemLoader(searchpath=Path(__file__).parent / "templates")
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "bot_template.py.j2"
    template = template_env.get_template(template_file)
    template_data = prepare_template_data(template_data)
    template_data["token"] = ""


    return template.render(template_data=template_data)


def prepare_template_data(template_data):
    for block_id, block in template_data["blocks"].items():

        # Update keyboards with callback data
        if block.get("buttons"):
            for button_name, button_callback_data in block["buttons"].items():
                template_data["blocks"][block_id]["buttons"][
                    button_name] = f"BLOCK_{button_callback_data['next_block']}_PATH"

    return template_data
