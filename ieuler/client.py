import functools
import io
import json
import os
import random
import re
from typing import Union, Tuple, List, Dict

import click
import requests_html
import requests
import rever
from PIL import Image

from ieuler.language_templates import Python, get_template
from ieuler.terminal_image_viewer import show_image


class Captcha(object):
    def __init__(self, captcha_bytes: bytes):
        self.captcha_bytes = captcha_bytes
        self.img = Image.open(io.BytesIO(self.captcha_bytes))
        self.input = None

    def show_in_terminal(self):
        show_image(self.img)
        self.get_input()

    def get_input(self):
        self.input = input('Please enter the captcha: ')


def require_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        if not self.logged_in():
            credentials = self.load_credentials()
            if not credentials:
                click.confirm('A login is required.  Would you like to continue?', abort=True)
                username, password = self.get_user_input_credentials()
            else:
                username, password = credentials['username'], credentials['password']

            self.login(username, password)
            # after you login, you can update self.problems
            if not self.logged_in():
                raise LoginUnsuccessful('Sorry, the username/password is not right.')

            # save the username and password (so we don't have to keep asking)
            with open(self.credentials_filename, 'wt') as f:
                json.dump({'username': username, 'password': password}, f)

            # now save the cookies (so that we can remain logged in)
            with open(self.cookies_filename, 'wt') as f:
                json.dump(self.session.cookies.get_dict(), f)

        r = func(*args, **kwargs)

        return r

    return wrapper


@rever.rever(exception=(requests.exceptions.ConnectionError,))
def post(session, url, data):
    return session.post(url, data=data)


class ProblemDoesNotExist(Exception):
    pass


class BadCaptcha(Exception):
    pass


class LoginUnsuccessful(Exception):
    pass


class Client(object):
    INHERENT_FIELDS = ('ID', 'Description / Title', 'Solved By', 'problem_url', 'page_url',)
    TEMPLATE_FIELDS = ('ID', 'Description / Title', 'problem_url', 'page_url', 'Problem',)

    def __init__(self, cookies_filename='.cookies', credentials_filename='.credentials', problems_filename='.problems',
                 default_language_filename='.default-language'):
        self.session = requests_html.HTMLSession()
        self.captcha = None

        self.cookies_filename = cookies_filename
        self.credentials_filename = credentials_filename
        self.problems_filename = problems_filename
        self.default_language_filename = default_language_filename

        self.problems = self.load_problems()
        self.language_template = self.load_language_template() or Python()

        self.server_host = os.getenv('IEULER_SERVER_HOST') or '127.0.0.1'
        self.server_port = os.getenv('IEULER_SERVER_PORT') or 2718
        self.server_port = int(self.server_port)

        self.session.cookies.update(self.load_cookies())

    def load_language_template(self):
        try:
            with open(self.default_language_filename, 'rt') as f:
                return get_template(json.load(f).get('language'))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return None

    def set_language(self, language):
        self.language_template = get_template(language)
        with open(self.default_language_filename, 'wt') as f:
            json.dump({'language': language}, f)

    def set_server_config(self, host: str, port: int):
        self.server_host = host
        self.server_port = port
        os.environ['IEULER_SERVER_HOST'] = host
        os.environ['IEULER_SERVER_PORT'] = str(port)

    def load_cookies(self):
        try:
            with open(self.cookies_filename, 'rt') as f:
                return json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}

    def load_problems(self):
        try:
            with open(self.problems_filename, 'rt') as f:
                return json.load(f)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            return []

    def load_credentials(self):
        try:
            with open(self.credentials_filename, 'rt') as f:
                return json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}

    def logged_in(self, username: str = None, cookies: Dict = None):

        if cookies:
            self.session.cookies.update(cookies)

        r0 = self.session.get('https://projecteuler.net')
        # check user is logged in as username
        info = r0.html.find('#info_panel', first=True)
        name = info.find('strong', first=True)
        if not name:
            return False

        if not username:
            return True

        if username == name.text:
            return True
        else:
            return False

    @rever.rever(exception=(requests.exceptions.ConnectionError,))
    def logout(self):
        r0 = self.session.get('https://projecteuler.net')
        for _ in r0.html.find('a'):
            if _.attrs.get('title') == 'Sign Out':
                self.session.get(f'https://projecteuler.net/{_.attrs["href"]}')

    @rever.rever(exception=(requests.exceptions.ConnectionError,))
    def get_captcha_raw(self) -> bytes:
        captcha_url = f'https://projecteuler.net/captcha/show_captcha.php?{random.random()}'
        r2 = self.session.get(captcha_url)
        return r2.content

    def get_user_input_captcha(self):
        click.confirm('A captcha is required.  Would you like to continue?', abort=True)
        self.captcha = Captcha(self.get_captcha_raw())
        self.captcha.show_in_terminal()
        return self.captcha.input

    @staticmethod
    def get_user_input_credentials() -> Tuple[str, str]:
        username = click.prompt('Please enter your Project Euler username', type=str)
        password = click.prompt('Please enter your Project Euler password', type=str, hide_input=True)
        return username, password

    def login(self, username: str, password: str, captcha: Union[str, int] = None):
        if not captcha:
            captcha = self.get_user_input_captcha()

        r = post(self.session, 'https://projecteuler.net/sign_in', {'username': username,
                                                                    'password': password,
                                                                    'captcha': captcha,
                                                                    'sign_in': 'Sign In'})

        if r.url != 'https://projecteuler.net/archives':
            error_message = r.html.find('#message', first=True).text
            if 'Username not known' in error_message:
                raise LoginUnsuccessful(f"{error_message}")
            if 'did not enter the confirmation code' in error_message:
                raise BadCaptcha(f'{error_message}')

    @require_login
    def submit(self, number, answer, captcha: Union[str, int] = None):

        # it is possible you already solved this problem

        r = self.session.get(f'https://projecteuler.net/problem={number}')
        form_e = r.html.find('form', first=True)
        completed = form_e.text
        if 'Completed' in completed:
            # note don't include keys we don't want updated so they don't update good data
            return {'correct_answer': form_e.find('b', first=True).text,
                    'completed_on': form_e.find('span', first=True).text,
                    'Solved': True}

        submit_token = None
        input_e = form_e.find('input')
        for _input in input_e:
            if _input.attrs.get('name') == 'submit_token':
                submit_token = _input.attrs['value']
                break

        if not captcha:  # todo do i need this?
            captcha = self.get_user_input_captcha()

        r = post(self.session, f'https://projecteuler.net/problem={number}',
                 data={f'guess_{number}': answer,
                       'captcha': captcha,  # todo do i need this?
                       'submit_token': submit_token})

        captcha_message_element = r.html.find('#message', first=True)
        if captcha_message_element:
            raise BadCaptcha(captcha_message_element.text)

        # or it is possible you failed to solve it
        p_es = r.html.find('p')
        p_e = p_es[0]
        if 'incorrect' in p_e.text:
            # ok to include all keys because we can only incorrect before being correct
            # ie cannot be correct then incorrect
            return {'correct_answer': None,
                    'completed_on': None,
                    'Solved': False}

        # or you just now solved it
        if 'correct' in p_e.text:
            # call the url again with a get to get the data we are looking for
            r = self.session.get(f'https://projecteuler.net/problem={number}')
            form_e = r.html.find('form', first=True)

            # all valid key/value
            # - ok to overwrite any other key/value in this case in updates
            return {'correct_answer': form_e.find('b', first=True).text,
                    'completed_on': form_e.find('span', first=True).text,
                    'Solved': True}

    def get_problem_details(self, number: int) -> Dict:
        url = f'https://projecteuler.net/problem={number}'
        r = self.session.get(url)
        if r.url != url:
            raise ProblemDoesNotExist(f'Problem {number} does not exist')

        problem_info = r.html.find('h2', first=True).text  # only one h2 element
        problem_content = r.html.find('.problem_content', first=True).html
        for _ in ('<img src="', '<a href="'):
            st = problem_content.find(_)
            if st > -1:
                problem_content = problem_content[:st + len(_)] + 'https://projecteuler.com/' + problem_content[
                                                                                                st + len(_):]
        return {
            'ID': int(number),
            'Description / Title': problem_info,
            'Problem': problem_content,
            'problem_url': url
        }

    def get_problem_list_on_page(self, page: int) -> List:
        data = []
        if page == 1:
            url = 'https://projecteuler.net/archives'
        else:
            url = f'https://projecteuler.net/archives;page={page}'

        r = self.session.get(url)

        column_headers = []  # id, desc, solved_by, difficulty, solved
        for i, tr in enumerate(r.html.find('tr')):
            if not tr.find('.id_column'):
                continue

            row = {_: None for _ in column_headers}
            if i == 0:
                for th in tr.find('th'):
                    if th.text:
                        column_headers.append(th.text)
                continue

            for j, td in enumerate(tr.find('td')):

                if j < len(column_headers):
                    row[column_headers[j]] = td.text

                else:
                    img = td.find('img', first=True)
                    if img:
                        if img.attrs['title'] == 'Solved':
                            row['Solved'] = True
                            break
                    row['Solved'] = False
                    break

            row.update({'problem_url': f'https://projecteuler.net/problem={row["ID"]}'})
            row.update({'page_url': url})
            row.update({'ID': int(row['ID'])})
            data.append(row)

        return data

    def get_page_qty(self) -> int:
        url = 'https://projecteuler.net/archives'
        r = self.session.get(url)

        pages = 15
        for a in reversed(r.html.find('a')):
            href = a.attrs['href']
            s = re.search(r'=([0-9]*)$', href)
            if s:
                pages = int(s.group(1))
                break
        return pages

    @staticmethod
    def get_page_number_from_page_url(page_url: str):
        p = re.search('page=([0-9]*)$', page_url)
        if p:
            return int(p.group(1))
        return 1

    def update_problems(self, problems: List):
        for _ in problems:
            if int(_['ID']) <= len(self.problems):
                self.problems[int(_['ID']) - 1].update(_)
            else:
                self.problems.append(_)  # todo what if the problems are not sorted or there is a gap?

        try:
            with open(self.problems_filename, 'wt') as f:
                json.dump(self.problems, f)
        except TypeError as e:
            raise Exception(f'Problems not updated properly: {e}')

    def get_new_problems(self) -> List:
        """ get any new problems from Project Euler """
        last_problem_number = int(self.problems[-1]['ID'])
        i = 1
        new_problems = []
        while True:
            try:
                new_problems.append(self.get_problem_details(number=last_problem_number + i))
                i += 1
            except ProblemDoesNotExist:
                break
        return new_problems

    def get_last_problem(self) -> Dict:
        last_page = self.get_page_qty()
        problems = self.get_problem_list_on_page(page=last_page)
        return problems[-1]

    def get_all_problems(self) -> List:
        all_problems = []
        with click.progressbar(range(1, self.get_page_qty() + 1), label='Fetching problems from Project Euler.') as bar:
            for page in bar:
                all_problems.extend(self.get_problem_list_on_page(page=page))
        return all_problems

    def update_all_problems(self) -> None:
        all_problems = self.get_all_problems()
        self.update_problems(all_problems)

    def ping_ipe(self):
        r = requests.get(f'http://{self.server_host}:{self.server_port}')

    @require_login
    def get_from_ipe(self):
        username = self.load_credentials()['username']
        cookies = self.load_cookies()
        url = f'http://{self.server_host}:{self.server_port}/api/problems'
        r = requests.get(url, auth=(username, json.dumps(cookies)))
        if r.status_code == 401:
            raise LoginUnsuccessful(f'Unable to login to ieuler-server: {url}')
        return r.json()

    @require_login
    def send_to_ipe(self, data):
        username = self.load_credentials()['username']
        cookies = self.load_cookies()
        url = f'http://{self.server_host}:{self.server_port}/api/problems'
        r = requests.post(url, json=data, auth=(username, json.dumps(cookies)))
        if r.status_code == 401:
            raise LoginUnsuccessful(f'Unable to login to ieuler-server: {url}')
        return r.json()
