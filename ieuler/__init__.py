import io
import importlib
import os
import random
import re
import warnings

from PIL import Image
from requests_html import HTMLSession, HTML

__all__ = ('start', 'Euler', 'Submission')

here = os.path.abspath(os.path.dirname(__file__))


def start(problem_number: int) -> 'Euler':
    """ Gets the problem details from project ieuler and creates a template file.

    :param problem_number: the problem number you want to tackle
    :return: an instance of 'Euler'
    """
    p = Euler(problem_number)
    p.get()
    p.template()
    return p


class ProblemDoesNotExist(Exception):
    pass


class CaptchaAttemptsExceeded(Exception):
    pass


class Submission(object):
    DIRECTORY = 'certificates'

    def __init__(self, html: HTML):
        p1_text = html.find('p', first=True).text
        self.status = True if 'Congratulations' in p1_text else False
        self.message = '\n'.join((_.text for _ in html.find('p') if _.text != 'Return to Problems page.'))
        self.number = int(re.search('([0-9]+)', self.message).group())
        self.html_page = html

    def _module_name(self):
        return 'problem_{}_certificate'.format(self.number)

    def _f_name(self):
        return '{}.html'.format(self._module_name())

    def _f_path(self):
        return self.DIRECTORY

    def _file(self):
        return os.path.join(self._f_path(), self._f_name())

    @staticmethod
    def _base(b_html: bytes) -> bytes:
        """ inject the base tag within the <head> tag -> <base href="https://www.projecteuler.net"/> """
        return b_html[:b_html.find(b'<head>\r\n') + 8] + b'<base href="https://projecteuler.net"/>' + b_html[
                                                                                                      b_html.find(
                                                                                                          b'<head>\r\n') + 8:]

    def certify(self):
        if self.status:
            try:
                with open(self._file(), 'wb') as f:
                    f.write(self._base(self.html_page.raw_html))
            except FileNotFoundError:
                os.makedirs(self._f_path())
                self.certify()
        else:
            warnings.warn("Your answer is incorrect, better luck next time! Here's a message:\n{}".format(self.message))


class Euler(object):
    DIRECTORY = 'problems'

    def __init__(self, number: int):
        self.number = number
        self.name = None
        self.content = None
        self.session = None
        self.logged_in = False
        self.submission = None

    def _module_name(self):
        return 'problem_{}'.format(self.number)

    def _f_path(self):
        return self.DIRECTORY

    def _f_name(self):
        return '{}.py'.format(self._module_name())

    def _file(self):
        return os.path.join(self._f_path(), self._f_name())

    def _f_exists(self):
        if os.path.exists(self._file()):
            return True

    def _problem_url(self):
        return 'https://projecteuler.net/problem={}'.format(self.number)

    def _initialize_session(self):
        if not self.session:
            self.session = HTMLSession()
            self.session.verify = False

    def get(self):
        """ Gets the problem information from project ieuler if necessary. """
        self._initialize_session()
        try:
            with open(self._file(), 'rt') as f:
                contents = f.read()
            self.name = contents[contents.find('name:\n') + 6:contents.find('\n\ncontent')]
            self.content = contents[contents.find('content:\n') + 9: contents.find('\n\n"""')]

        except FileNotFoundError:
            url = self._problem_url()
            r = self.session.get(url)
            if r.url != url:
                raise ProblemDoesNotExist(
                    'Problem {} does not exist, you have been redirected here: {}'.format(self.number, r.url))

            self.name = r.html.find('h2', first=True).text
            self.content = '\n'.join(_.text for _ in r.html.find('p'))

    def submit(self):
        """ Submit the answer to project ieuler, requires logging in. """
        answer = self.answer()
        self.post(answer)
        self.submission.certify()

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
        return input(prompt)

    def _log_in(self, captcha_attempts: int = 3) -> None:
        """ Log in to project ieuler.

        Needed when submitting answers.

        :param captcha_attempts: number of attempts before raising exception
        :return: None
        """
        if self.logged_in:
            return
        self._initialize_session()
        username = self._input('enter your project ieuler username: ')
        password = self._input('enter your project ieuler password: ')

        while captcha_attempts > 0:
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
                warnings.warn(message + '\nLet"s try again.')
                captcha_attempts -= 1
        else:
            raise CaptchaAttemptsExceeded('Too many attempts to get the captcha correct, unable to login')

    def post(self, answer):
        """ Posts the problem answer to project ieuler.  Requires logging in. """

        self._log_in()
        captcha = self._captcha('submit')
        data = {'guess_1': answer, 'captcha': captcha}
        r = self.session.post(self._problem_url(), data=data)
        self.submission = Submission(html=r.html)

    def template(self):
        """ Creates the template for the problem if one does not exist. """
        code = '"""' \
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
               '\n'.format(self.name, self.content, self.number, self.name)

        if self._f_exists():
            return

        try:
            with open(self._file(), 'wt') as f:
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
    problem_1 = start(problem_number=1)
    problem_1.submit()
