import datetime
import json
import re

from csscompressor import compress

def load_config() -> dict:
    """Loads `config.json`"""
    with open("config.json", 'r+') as f:
        # load config file
        config = json.load(f)
        config["build_no"] += 1

        # write updated config
        f.seek(0)
        f.truncate()
        json.dump(config, f, indent=4)

    return config

def replace_variables(config, css):
    """Replaces css variables with their value"""
    with open(f"{config['directories']['src']}/vars.css") as f:
        for variable, value in re.findall(r"(--[\w\-]+):\s(.*);", f.read()):
            print(variable, value)
            css = css.replace(f"var({variable})", value)

    return css

def generate_css(config, *, minified=False) -> str:
    contents = ""
    css = ""

    for index, filename in enumerate(config["files"]):
        try:
            with open(f"{config['directories']['src']}/{filename}.css") as f:
                    css += f"/* {'-' * 77}\n\t{index + 1} - {filename}\n{'-' * 77} */\n\n{f.read()}\n\n"
                    contents += f"\t\t{index + 1} - {filename}\n"
        except FileNotFoundError:
            print(f"Unable to open file: {config['directories']['src']}/{filename}.css")

    header = ( f"/* - {config['subreddit']} CSS {'-' * (70 - len(config['subreddit']))}\n\n"
        + f"\tBuild Number #{config['build_no']} - {datetime.datetime.utcnow().strftime('%b %d %H:%M:%S UTC %Y')}\n"
        + f"\t{config['authors']}\n"
        + ( f"\n\tFile Contents:\n\n"
            + contents 
            + "\n"
            if not minified else "\n"
            )
        + f"{'-' * 77} */"
        )

    css = replace_variables(config, css)

    if minified:
        return f"{header}\n{compress(css)}"
    
    else:
        return f"{header}\n\n{css}"

if __name__ == "__main__":
    config = load_config()

    print(f"Generating CSS for {config['subreddit']}:\n")

    with open(f"{config['directories']['dist']}/dist.css", 'w') as f:
        f.write(generate_css(config))

    with open(f"{config['directories']['dist']}/dist.min.css", 'w') as f:
        f.write(generate_css(config, minified=True))

    print(f'Done!')
    