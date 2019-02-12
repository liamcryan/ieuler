import getpass
import io
import importlib
import os
import random
import re
import warnings
from typing import Dict, Optional, Union, List

from PIL import Image
from requests_html import HTMLSession, HTML

__all__ = ('template', 'Euler', 'Certification', 'Client')

here = os.path.abspath(os.path.dirname(__file__))


def template(problem_number: int, problem_directory: str) -> 'Euler':
    """ Gets the problem details from project ieuler and creates a template file.

    :param problem_number: the problem number you want to tackle
    :param problem_directory: the directory you would like to keep your problems
    :return: an instance of 'Euler'
    """
    p = Euler(problem_number, problem_directory)

    p.get()
    p.template()
    return p


class ProblemDoesNotExist(Exception):
    pass


class CaptchaAttemptsExceeded(Exception):
    pass


class PasswordAttemptsExceeded(Exception):
    pass


class InvalidUsername(Exception):
    pass


class Certification(object):

    def __init__(self, html: HTML, directory: str = None):
        p1_text = html.find('p', first=True).text
        self.status = True if 'Congratulations' in p1_text else False
        self.message = '\n'.join((_.text for _ in html.find('p') if _.text != 'Return to Problems page.'))
        self.number = int(re.search('([0-9]+)', self.message).group())
        self.html_page = html
        self.directory = directory

    def _module_name(self):
        return 'problem_{}_certificate'.format(self.number)

    def _f_name(self):
        return '{}.html'.format(self._module_name())

    def _f_path(self):
        return self.directory

    def file(self):
        return os.path.join(self._f_path(), self._f_name())

    @staticmethod
    def _base(b_html: bytes) -> bytes:
        """ inject the base tag within the <head> tag -> <base href="https://www.projecteuler.net"/> """
        return b_html[:b_html.find(
            b'<head>\r\n') + 8] + b'<base href="https://projecteuler.net"/>' + b_html[b_html.find(b'<head>\r\n') + 8:]

    def certify(self):
        if self.status:
            try:
                with open(self.file(), 'wb') as f:
                    f.write(self._base(self.html_page.raw_html))
            except FileNotFoundError:
                os.makedirs(self._f_path())
                self.certify()
        else:
            warnings.warn("Your answer is incorrect, better luck next time! Here's a message:\n{}".format(self.message))


# https://projecteuler.net/show=all

class Problem(object):
    def __init__(self, number, name, content):
        self.number = number
        self.name = name
        self.content = content
        self.url = self.problem_url(number)

    @staticmethod
    def problem_url(number):
        return 'https://projecteuler.net/problem={}'.format(number)

    @staticmethod
    def all_problems_url():
        return 'https://projecteuler.net/show=all'


class Client(object):
    def __init__(self, cookies: Dict = None, logged_in: bool = False):
        """ usage:
            c = Client()
            c.login()
            c.submit()
            ...
        """
        self.logged_in = logged_in
        if cookies:
            self.session = HTMLSession()
            self.session.cookies.update(cookies)
        else:
            self.session = None

    def _initialize_session(self):
        if not self.session:
            self.session = HTMLSession()
            self.session.verify = False

    def captcha(self) -> bytes:
        """ a fun project will be to interpret the captcha from bytes so the user doesn't need to enter it """
        self._initialize_session()
        captcha_url = 'https://projecteuler.net/captcha/show_captcha.php?{}'.format(random.random())
        r2 = self.session.get(captcha_url)
        return r2.content

    def login(self, username, password, captcha) -> Optional[Dict]:
        self._initialize_session()
        r = self.session.post('https://projecteuler.net/sign_in', data={'username': username,
                                                                        'password': password,
                                                                        'captcha': captcha,
                                                                        'sign_in': 'Sign In'})
        if r.url == 'https://projecteuler.net/archives':
            self.logged_in = True
        else:
            message = r.html.find('#message', first=True).text
            return {'message': message}

    def get(self, number: int):
        """ Gets the problem information from project euler. """
        self._initialize_session()
        url = Problem.problem_url(number)
        r = self.session.get(url)
        if r.url != url:
            raise ProblemDoesNotExist(
                'Problem {} does not exist, you have been redirected here: {}'.format(number, r.url))

        name = r.html.find('h2', first=True).text
        content = '\n'.join(_.text for _ in r.html.find('p'))
        return Problem(number, name, content)

    def submit(self, number, answer, captcha) -> Dict:
        """ Submit the answer to project ieuler, requires logging in. """
        self._initialize_session()
        data = {'guess_1': answer, 'captcha': captcha}
        r0 = self.session.post(Problem.problem_url(number), data=data)  # todo what if user not logged in...
        captcha_message_element = r0.html.find('#message', first=True)
        if captcha_message_element:
            return {'status': False, 'message': captcha_message_element.text}
        r0_text = r0.html.find('p', first=True).text
        status = True if 'Congratulations' in r0_text else False
        message = '\n'.join((_.text for _ in r0.html.find('p') if _.text != 'Return to Problems page.'))
        return {'status': status, 'message': message}


class Euler(object):
    def __init__(self, number: int = None, directory: str = None):
        self.number = number
        self.name = None
        self.content = None
        self.url = None

        self.session = None
        self.logged_in = False
        self.certification = None
        self.directory = directory

    def _module_name(self):
        return 'problem_{}'.format(self.number)

    def _f_path(self):
        return self.directory

    def _f_name(self):
        return '{}.py'.format(self._module_name())

    def file(self):
        return os.path.join(self._f_path(), self._f_name())

    def _f_exists(self):
        if os.path.exists(self.file()):
            return True

    def _problem_url(self):
        return 'https://projecteuler.net/problem={}'.format(self.number)

    def _initialize_session(self):
        if not self.session:
            self.session = HTMLSession()
            self.session.verify = False

    def get(self):
        """ Gets the problem information from project euler. """
        self._initialize_session()
        url = self._problem_url()
        r = self.session.get(url)
        if r.url != url:
            raise ProblemDoesNotExist(
                'Problem {} does not exist, you have been redirected here: {}'.format(self.number, r.url))

        self.url = r.url
        self.name = r.html.find('h2', first=True).text
        self.content = '\n'.join(_.text for _ in r.html.find('p'))

    def retrieve(self):
        """ Retrieves the problem information from a file (or database tbd) """
        with open(self.file(), 'rt') as f:
            contents = f.read()
        self.url = contents[contents.find('url:\n') + 4:contents.find('\n\nname')]
        self.name = contents[contents.find('name:\n') + 6:contents.find('\n\ncontent')]
        self.content = contents[contents.find('content:\n') + 9: contents.find('\n\n"""')]

    def submit(self, certificate_directory):
        """ Submit the answer to project ieuler, requires logging in. """
        answer = self.answer()
        self.post(answer=answer, certificate_directory=certificate_directory)
        self.certification.certify()

    def _captcha(self, _id: str):
        """ a fun project will be to interpret the captcha from bytes so the user doesn't need to enter it """
        captcha_url = 'https://projecteuler.net/captcha/show_captcha.php?{}'.format(random.random())
        r2 = self.session.get(captcha_url)
        captcha_image = io.BytesIO(r2.content)
        img = Image.open(captcha_image)
        img.show()
        return self._input('enter the captcha code from the image ({}): '.format(_id))

    @staticmethod
    def _input(prompt):
        """ alias for built in input function -> facilitates testing"""
        if 'password' in prompt:
            return getpass.getpass(prompt)
        return input(prompt)

    def log_in(self, captcha_attempts: int = 3, password_attempts: int = 3) -> None:
        """ Log in to project ieuler.

        Needed when submitting answers.

        :param captcha_attempts: number of attempts before raising exception
        :return: None
        """
        user_prompt = 'enter your project ieuler username: '
        pass_prompt = 'enter your project ieuler password: '
        if self.logged_in:
            return
        self._initialize_session()
        username = self._input(user_prompt)
        password = self._input(pass_prompt)

        while captcha_attempts > 0 and password_attempts > 0:
            captcha = self._captcha('sign in')
            r = self.session.post('https://projecteuler.net/sign_in', data={'username': username,
                                                                            'password': password,
                                                                            'captcha': captcha,
                                                                            'sign_in': 'Sign In'})
            if r.url == 'https://projecteuler.net/archives':
                self.logged_in = True
                break  # good, you are logged in
            else:
                message = r.html.find('#message', first=True).text
                warnings.warn(message)
                if message == 'Sign In Failed':
                    password = self._input(pass_prompt)
                    password_attempts += 1
                elif message == 'Username not known':
                    raise InvalidUsername(message)
                elif message == 'You did not enter the confirmation code':
                    captcha_attempts -= 1
        else:
            if captcha_attempts == 0:
                raise CaptchaAttemptsExceeded(
                    'Too many attempts to get the captcha correct. Limit is: {}'.format(captcha_attempts))
            elif password_attempts == 0:
                raise PasswordAttemptsExceeded(
                    'Too many attempts to get the password correct. Limit is: {}'.format(password_attempts))

    def post(self, answer, certificate_directory: str = None):
        """ Posts the problem answer to project ieuler.  Requires logging in. """

        self.log_in()
        captcha = self._captcha('submit')
        data = {'guess_1': answer, 'captcha': captcha}
        r = self.session.post(self._problem_url(), data=data)
        self.certification = Certification(html=r.html, directory=certificate_directory)

    def template(self):
        """ Creates the template for the problem if one does not exist. """
        code = '"""' \
               '\n\n' \
               'url:' \
               '\n' \
               '{}' \
               '\n\n' \
               'name:' \
               '\n' \
               '{}' \
               '\n\n' \
               'content:' \
               '\n' \
               '{}' \
               '\n\n"""' \
               '\n\n\n' \
               'def answer():' \
               '\n' \
               '    """ The answer to Problem {}: {}.' \
               '\n\n' \
               '    Solve the problem here!' \
               '\n\n' \
               '    :return: your answer' \
               '\n' \
               '    """' \
               '\n' \
               '    return' \
               '\n\n\n' \
               'if __name__ == "__main__":' \
               '\n' \
               '    """ You can test your code here, just run or debug this file! """' \
               '\n' \
               '    print(answer())' \
               '\n'.format(self.url, self.name, self.content, self.number, self.name)

        if self._f_exists():
            return

        try:
            with open(self.file(), 'wt') as f:
                f.write(code)
        except FileNotFoundError:
            os.makedirs(self._f_path())
            self.template()

    def answer(self):
        """ Read the problem's template file and call the answer function. """
        f_path = self._f_path()
        basename = os.path.basename(f_path)
        dirname = os.path.dirname(f_path)
        while basename[0] != '.':
            try:
                module = importlib.import_module(name='{}.{}'.format(basename, self._module_name()))
                return module.answer()
            except ModuleNotFoundError:
                basename = os.path.basename(dirname) + '.' + basename
                dirname = os.path.dirname(dirname)
            except TypeError as e:
                raise ImportError(e)


if __name__ == '__main__':
    import time
    st = time.time()
    c = Client()
    probs = c.all_problems()
    print(f'took {time.time() - st}s')
    print(probs)

    # problem_1 = template(problem_number=1, problem_directory='problems')
    # problem_1.submit(certificate_directory='certificates')
