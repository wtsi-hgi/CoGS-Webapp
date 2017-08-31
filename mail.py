import os
import smtplib
from asyncio import get_event_loop
from concurrent.futures import ThreadPoolExecutor
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict

import aiofiles
from bs4 import BeautifulSoup, NavigableString, CData
from jinja2 import Environment, BaseLoader


async def send_user_email(app, user: str, template_name: str, attachments: Dict[str, str]=None, **kwargs):
    config = app["email"]
    web_config = app["webserver"]

    contents = {}
    for message_type in ("subject", "contents"):
        async with aiofiles.open(os.path.join("email_template", f"{template_name}_{message_type}.jinja2")) as template_f:
            env = Environment(loader=BaseLoader).from_string((await template_f.read()).replace("\n", ""))
        rendered = env.render(config=config, user=user, web_config=web_config, **kwargs)
        contents[message_type] = rendered

    await send_email(to=user.email,
                     **contents,
                     attachments=attachments,
                     **config)


async def send_email(*, host: str, port: int, to: str, from_: str, subject: str, contents: str, attachments: Dict[str, bytes]=None):
    loop = get_event_loop()
    with ThreadPoolExecutor() as executor:
        loop.run_in_executor(executor, _send_email, host, port, to, from_, subject, contents, attachments)


def _send_email(host: str, port: str, to: str, from_: str, subject: str, contents: str, attachments: Dict[str, bytes]=None):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = from_
    message["To"] = to

    html = contents
    text = get_text(html)
    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(html, 'html'))

    if attachments is not None:
        for name, data in attachments.items():
            part = MIMEApplication(
                data,
                Name=name
            )
            part["Content-Disposition"] = f'attachment; filename="{name}"'
            message.attach(part)

    s = smtplib.SMTP(host, port)
    s.sendmail(from_, to, message.as_string())
    s.quit()


def get_text(html: str):
    soup = BeautifulSoup(html, "html.parser")
    rtn = []
    for descendant in soup.descendants:
        if isinstance(descendant, (NavigableString, CData)):
            parent = descendant.parent
            if parent.name == "a":
                rtn.append(f"{descendant} ({parent['href']})")
            else:
                rtn.append(str(descendant))
        elif descendant.name == "br":
            rtn.append("\n")
    return "".join(rtn)


if __name__ == "__main__":
    from config import load_config
    config = load_config(os.path.join("config", "config.yaml"))["email"]
    config["from_"] = config["from"]
    del config["from"]
    _send_email(to="sb48@sanger.ac.uk",
                subject="test",
                contents="<h1>test</h1> <br><a href='http://127.0.0.1/project_feedback/2'>mark their project</a>",
                attachments={"filename.txt": b"test"},
                **config)