import functools
import json
import os
import random
import subprocess

import click
import requests

from ieuler.client import Client
from ieuler.language_templates import get_template, supported_languages


class Session(object):
    def __init__(self):
        self.client = Client()


def require_fetch(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = args[0]  # notice i am assuming args[0]
        if not session.client.problems:
            click.echo('Please fetch problems first.')
            return

        r = func(*args, **kwargs)
        return r

    return wrapper


@click.group()
@click.pass_context
def ilr(ctx):
    ctx.obj = Session()


@ilr.command()
@click.pass_obj
def fetch(session):
    """ Fetch the problems from Project Euler & Interactive Project Euler. """
    session.client.update_all_problems()
    try:
        ipe_problems = session.client.get_from_ipe()
    except (requests.exceptions.ConnectionError,):
        return
    session.client.update_problems(ipe_problems)


@ilr.command()
@click.pass_obj
@require_fetch
def send(session):
    """ Send the problems to Interactive Project Euler. """
    problems = []
    for _ in session.client.problems:
        problem = {}
        if 'code' in _:
            problem.update({'code': _['code']})
        if 'Solved' in _:
            problem.update({'Solved': _['Solved']})
        if 'completed_on' in _:
            problem.update({'completed_on': _['completed_on']})
        if 'correct_answer' in _:
            problem.update({'correct_answer': _['correct_answer']})

        if problem:
            problem.update({'ID': _['ID']})
            problems.append(problem)

    try:
        session.client.send_to_ipe(problems)
    except (requests.exceptions.ConnectionError,) as e:
        click.echo(f'Unable to send data to server.\n{e}')


@ilr.command()
@click.pass_obj
@require_fetch
def ls(session):
    """ List out the problems from Project Euler. """

    def _generate_output():
        for _ in session.client.problems:
            display_data = {}
            for k in _:
                if k in Client.INHERENT_FIELDS:
                    display_data.update({k: _[k]})
            yield json.dumps(display_data, sort_keys=True, indent=4)

    click.echo_via_pager(_generate_output)


@ilr.command()
@click.option('--edit/--no-edit', default=True)
@click.option('-language', nargs=1, type=str, default=None)
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_obj
@require_fetch
def solve(session, problem_number, language, edit):
    """ Solve a problem in your language of choice. """

    _supported_languages = supported_languages()
    if not language:
        language = random.choice(_supported_languages)
        click.confirm(
            f'Choosing {language} by default.  Here are the supported language templates: {_supported_languages}',
            abort=True)

    language_template = get_template(language)
    if not language_template:
        click.echo(
            f'sorry, could not find the language template for {language}.  Here are the supported language templates: {_supported_languages}')
        return

    problem = session.client.get_detailed_problem(number=problem_number)
    session.client.update_problems([problem])

    file_name = f'{problem["ID"]}{language_template.extension}'
    file_content = None
    if not os.path.exists(file_name):
        # do we need to load the contents or use the default template?
        if problem.get('code'):
            if problem['code'].get(language):
                file_content = problem['code'][language]['filecontent']
        with open(file_name, 'wt') as f:
            content = json.dumps(problem, sort_keys=True, indent=4)
            if not file_content:
                file_content = language_template.template(content)
            f.write(file_content)

    if edit:
        click.edit(filename=file_name)


@ilr.command()
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_obj
@require_fetch
def view(session, problem_number):
    """ View a problem and your associated code or submission information. """

    problem = session.client.problems[int(problem_number) - 1]
    click.echo(json.dumps(problem, sort_keys=True, indent=4))


@ilr.command()
@click.option('--dry/--live', default=False)
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_obj
@require_fetch
def submit(session, problem_number, dry):
    """ Execute a file and submit its stdout to Project Euler. """

    # todo look in the session.client.problems for the code key,
    #   get the correct filename and language
    filename = f'{problem_number}.py'

    # execute the file
    # get the result from stdout
    command = ['python', filename]
    answer = subprocess.run(command, capture_output=True)
    if answer.returncode != 0:
        click.echo('Oops, there was an error running the file:')
        click.echo(answer.stderr)
        return

    answer = answer.stdout.decode().strip('\n')
    if dry:
        click.echo(f'Result of executing: {command}: {answer}')
        return

    with open(filename, 'rt') as f:
        problem = {'ID': str(problem_number),
                   'code': {'python': {'filecontent': f.read(), 'submission': answer, 'filename': filename}}}

    response = session.client.submit(problem_number, int(answer))
    response.update({'ID': problem_number})

    if answer == response['correct_answer']:
        click.echo('Yay! You did it :)')
        click.echo(f'{response["completed_on"]}')
    else:
        click.echo(f"Sorry, {answer} is not the answer :(")
        if response['completed_on']:
            click.echo(f"But you've already solved this problem...")
            click.echo(f'{response["completed_on"]}')

    response.update(problem)  # update the response with the executed code/language (saves to .problems)
    session.client.update_problems([response])
