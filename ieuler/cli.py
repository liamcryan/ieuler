import functools
import json
import os
import subprocess

import click
import requests

from ieuler.client import Client
from ieuler.language_templates import get_template, supported_languages

context_settings = {'context_settings': dict(max_content_width=120)}


class Session(object):
    def __init__(self):
        self.client = Client()


def require_fetch(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = args[0]  # notice i am assuming args[0] will be the session
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


@ilr.command(**context_settings)
@click.option('-language', type=str, nargs=1)
@click.option('-host', type=str, nargs=1)
@click.option('-port', type=int, nargs=1)
@click.pass_obj
def config(session, language, host, port):
    """ Get or set configuration options. """

    if (host and port) or (host and not port) or (port and not host):
        session.client.set_server_config(host, port)
    if language:
        if language in supported_languages():
            session.client.set_language(language)
        else:
            click.echo(f'Sorry, there is no language template for {language}')
            return

    d = {}
    c = session.client.load_credentials()
    d.update({'credentials': {'username': c['username'], 'password': '*******'}})
    d.update({'server': {'host': session.client.server_host, 'port': session.client.server_port}})
    d.update({'language': session.client.language_template.language})
    click.echo(json.dumps(d, sort_keys=True, indent=4))


@ilr.command(**context_settings)
@click.pass_obj
def fetch(session):
    """ Fetch the problems from Project Euler & Interactive Project Euler. See config for default server. """
    session.client.update_all_problems()
    try:
        ipe_problems = session.client.get_from_ipe()
    except (requests.exceptions.ConnectionError,):
        return
    session.client.update_problems(ipe_problems)


@ilr.command(**context_settings)
@click.pass_obj
@require_fetch
def send(session):
    """ Send the problems to Interactive Project Euler.  See config for default server. """
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


@ilr.command(**context_settings)
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


@ilr.command(**context_settings)
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_obj
@require_fetch
def view(session, problem_number):
    """ View a problem and your associated code or submission information. """

    problem = session.client.problems[int(problem_number) - 1]
    click.echo(json.dumps(problem, sort_keys=True, indent=4))


@ilr.command(**context_settings)
@click.option('--edit/--no-edit', default=True)
@click.option('-language', nargs=1, type=str, default=None)
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_obj
@require_fetch
def solve(session, problem_number, language, edit):
    """ Solve a problem in your language of choice.  See config for defaults. """

    if not language:
        language_template = session.client.language_template
    else:
        language_template = get_template(language)

    if not language_template:
        click.echo(
            f'sorry, could not find the language template for {language}.  Here are the supported language templates: {supported_languages()}')
        return

    # get the rest of the problem from Project Euler (if we need to)
    problem = session.client.problems[problem_number - 1]
    if 'Problem' not in problem:
        problem = session.client.get_problem_details(number=problem_number)
        session.client.update_problems([problem])  # update session.client.problems
        problem = session.client.problems[problem_number - 1]  # we really want session.client.problems

    file_name = f'{problem["ID"]}{language_template.extension}'

    # start by getting the code from .problems if it is there
    # or the default template code if it is not
    # (we will use the actual file content later if we can)

    # todo test cases:
    #   code in memory for 1 language
    #   code in memory for 2 languages
    #   file exists for 1 language
    #   file exists for 2 languages
    #   check combinations of above that resulting session.client.problem is correct

    if problem.get('code'):
        if problem['code'].get(language_template.language):
            file_content = problem['code'][language_template.language]['filecontent']
        else:
            content_dict = {_: problem[_] for _ in problem if _ in Client.TEMPLATE_FIELDS}
            content = json.dumps(content_dict, sort_keys=True, indent=4)
            file_content = language_template.template(content)
            problem['code'][language_template.language] = {'filename': file_name, 'filecontent': file_content,
                                                           'submission': None}

    else:
        content_dict = {_: problem[_] for _ in problem if _ in Client.TEMPLATE_FIELDS}
        content = json.dumps(content_dict, sort_keys=True, indent=4)
        file_content = language_template.template(content)
        problem['code'] = {
            language_template.language: {'filename': file_name, 'filecontent': file_content, 'submission': None}}

    if not os.path.exists(file_name):
        with open(file_name, 'wt') as f:
            f.write(file_content)

    else:
        # a file exists, let's use this instead
        with open(file_name, 'rt') as f:
            file_content = f.read()
        # now update the filecontent
        # there will be a code and language_template.language - it was populated above
        problem['code'][language_template.language].update({'filecontent': file_content})

    # file_content is ready
    # code has been updated

    if edit:
        click.edit(filename=file_name)

    # let's update session.client.problems with updated
    session.client.update_problems([problem])


@ilr.command(**context_settings)
@click.option('-language', type=str, nargs=1)
@click.option('--dry/--live', default=False)
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_obj
@require_fetch
def submit(session, problem_number, dry, language):
    """ Execute a file and submit its stdout to Project Euler. """

    # look for the code to run in session.self.problems
    problem = session.client.problems[problem_number - 1]
    code = problem.get('code')
    if not code:
        click.echo('There is no code to run.  Use solve first.')
        return

    # verify language is in code
    if language:
        if language not in code:
            if language in supported_languages():
                click.echo(f'It looks like you need to solve a file in {language} first.')
            else:
                click.echo(f'There is no language template for {language}.')

            return

    _language = list(code.keys())
    submissions = {_: None for _ in _language}
    for lang in code:
        submissions[lang] = code[lang]['submission']

    # {python: 123, node: None}
    if len(submissions) > 1:
        submission_language = None
        for lang in submissions:
            if submissions[lang] is None:
                submission_language = lang
                break  # take the first language that has not been submitted
        if submission_language is None:
            click.echo(
                f'You have already submitted this problem in {_language}.  You may solve it again in another language (or manually change a "submission" key to null in {session.client.problems_filename}).')
            return

        if language:
            submission_language = language
        else:
            click.confirm(
                f'You have solved this problem in {len(submissions)} languages.  Submission will be in {submission_language}. Next time specify -language or continue.',
                abort=True)
    else:
        submission_language = _language[0]

    language_template = get_template(submission_language)

    filename = f'{problem_number}{language_template.extension}'

    # update the filecontent (we want self.problems.problem to be in sync with potential changes to file by user)
    with open(filename, 'rt') as f:
        code[submission_language].update({'filecontent': f.read()})

    problem['code'].update(code)

    session.client.update_problems([problem])

    # execute the file
    # get the result from stdout
    command = [submission_language, filename]
    answer = subprocess.run(command, capture_output=True)
    if answer.returncode != 0:
        click.echo('Oops, there was an error running the file:')
        click.echo(answer.stderr)
        return

    answer = answer.stdout.decode().strip('\n')
    if dry:
        click.echo(f'Result of executing: {command}: {answer}')
        return

    # here we will submit to Project Euler
    response = session.client.submit(problem_number, answer)
    problem.update(response)

    # update code if successful (if execution makes it here)
    code[submission_language].update({'submission': answer})

    if answer == response['correct_answer']:
        click.echo('Yay! You did it :)')
        click.echo(f'{response["completed_on"]}')
    else:
        click.echo(f"Sorry, {answer} is not the answer :(")
        if response['completed_on']:
            click.echo(f"But you've already solved this problem...")
            click.echo(f'{response["completed_on"]}')

    problem['code'].update(code)
    session.client.update_problems([problem])
