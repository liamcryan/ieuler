"""
The first run of the tests, vcr uses keyword all=True.
Once the cassettes are recorded, switch to none=True
Also, once they are recorded, MagicMock is used...so comment out on first run.
"""

import os
from unittest.mock import MagicMock

from PIL.Image import Image
from vcr import VCR

from ieuler import Euler, Certification

Euler._input = MagicMock(return_value='not significant')
Image.show = MagicMock(return_value=None)

here = os.path.abspath(os.path.dirname(__file__))
my_vcr = VCR(cassette_library_dir=os.path.join(here, 'cassettes'))

problem_dir = os.path.join(here, 'problems')
sample_problem_dir = os.path.join(here, 'sample_problems')
certificate_dir = os.path.join(here, 'certificates')
p_1 = Euler(number=1, directory=problem_dir)


@my_vcr.use_cassette(none=True)
def test_get_project_by_number_http():
    """ tests that the correct response is received from project ieuler """
    assert os.path.isfile(p_1.file()) is False
    p_1.get()  # populates p_1.name & p_1.content
    assert p_1.name == 'Multiples of 3 and 5'
    assert p_1.content == 'If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9. The sum of these multiples is 23.\nFind the sum of all the multiples of 3 or 5 below 1000.'
    assert p_1.url == 'https://projecteuler.net/problem=1'

def test_get_project_by_number_local():
    """ this time test from local instead """
    p_1.directory = sample_problem_dir
    p_1.get()  # populates from sample_problems this time
    assert p_1.name == 'Multiples of 3 and 5'
    assert p_1.content == 'If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9. The sum of these multiples is 23.\nFind the sum of all the multiples of 3 or 5 below 1000.'
    p_1.directory = problem_dir


def test_create_new_template():
    try:
        os.remove(p_1.file())
    except OSError:
        pass
    p_1.name = 'The elastic problem of individual efforts'
    p_1.content = 'Given a name and number, how many combinations of pi are there?'
    p_1.template()
    p_1.name = None
    p_1.content = None
    p_1.get()  # populates from the template just created
    assert p_1.name == 'The elastic problem of individual efforts'
    assert p_1.content == 'Given a name and number, how many combinations of pi are there?'
    try:
        os.remove(p_1.file())
    except OSError:
        pass


def test_get_answer():
    p_1.directory = sample_problem_dir
    assert callable(p_1.answer)
    assert p_1.answer() is None
    p_1.directory = problem_dir


@my_vcr.use_cassette(none=True)
def test_submit_guess():
    p_1.directory = sample_problem_dir
    assert p_1.logged_in is False
    assert p_1.certification is None
    p_1.post(3.14)  # incorrect answer, but we aren't testing that
    assert p_1.logged_in is True
    assert isinstance(p_1.certification, Certification)
    p_1.directory = problem_dir


@my_vcr.use_cassette(none=True)
def test_certify_incorrect():
    p_1.post(3.14, certificate_dir)  # the wrong answer
    assert p_1.certification.status is False
    p_1.certification.certify()


@my_vcr.use_cassette(none=True)
def test_certify_correct():
    try:
        os.remove(os.path.join(certificate_dir, 'problem_1_certificate.html'))
    except OSError:
        pass
    p_1.post(233168, certificate_dir)  # sorry everyone for the spoiler
    assert p_1.certification.status
    p_1.certification.certify()  # saves the certificate
    assert os.path.isfile(p_1.certification.file())

    try:
        os.remove(os.path.join(certificate_dir, 'problem_1_certificate.html'))
    except OSError:
        pass
