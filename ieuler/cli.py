import functools
import json
import subprocess

import click
import requests

from ieuler.client import Client, LoginUnsuccessful, BadCaptcha, require_login
from ieuler.language_templates import get_template, supported_languages

context_settings = {'context_settings': dict(max_content_width=300)}


class Session(object):
    def __init__(self):
        self.client = Client()


@require_login
def _login(client):
    pass


def require_fetch(func):
    @click.pass_context
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = args[0]
        session = args[1]
        if not session.client.problems:
            ctx.invoke(fetch)

        r = func(*args[1:], **kwargs)
        return r

    return wrapper


@click.group(**context_settings)
@click.pass_context
def ilr(ctx):
    """
    Welcome to Interactive Project Euler Command Line Tool!

    Below are the commands.  For more details on a specific command you can type:

    $ ilr [COMMAND] --help

    Happy trails!
     """
    if not ctx.obj:  # we don't want to overwrite the context when testing
        ctx.obj = Session()


@ilr.command(**context_settings)
@click.option('-language', type=str, nargs=1, help=f'Set language from: {supported_languages()}')
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
    if 'password' in c:
        c['password'] = '*******'
    d.update({'credentials': c})
    d.update({'server': {'host': session.client.server_host, 'port': session.client.server_port}})
    d.update({'language': session.client.language_template.language})
    click.echo(json.dumps(d, sort_keys=True, indent=4))


@ilr.command(**context_settings)
@click.pass_obj
def logout(session):
    """ Log out of Project Euler. """
    session.client.logout()
    if session.client.logged_in():
        click.echo('Unable to log out :(')
    else:
        click.echo('Logged out successfully.')


@ilr.command(**context_settings)
@click.pass_obj
def login(session):
    """ Explicitly log in to Project Euler. """

    try:
        _login(session.client)
    except LoginUnsuccessful as e:
        click.echo(e)


@ilr.command(**context_settings)
@click.option('--update-from-project-euler/--skip-pe-update', default=True)
@click.option('--update-from-ieuler-server/--skip-ipe-update', default=True)
@click.option('--as-user/--anonymous', default=True)
@click.pass_obj
def fetch(session, as_user, update_from_project_euler, update_from_ieuler_server):
    """ Fetch the problems from Project Euler & Interactive Project Euler. See config for default server. """

    if as_user:
        try:
            _login(session.client)
        except LoginUnsuccessful as e:
            click.echo(e)
            return

    if update_from_ieuler_server:
        try:
            session.client.ping_ipe()
            try:
                ipe_problems = session.client.get_from_ipe()
                click.echo('Fetched problems from ieuler-server successfully.')
                if ipe_problems:
                    if not session.client.problems:
                        # don't care if they don't want to fetch from ieuler, they need to because there are no problems
                        session.client.update_all_problems()
                        update_from_project_euler = False  # since we just did, don't need to do it again
                    session.client.update_problems(ipe_problems)

            except BadCaptcha as e:
                click.echo(e)
            except LoginUnsuccessful as e:
                click.echo(e)

        except requests.exceptions.ConnectionError:
            click.echo('ieuler server is not running.')

    if update_from_project_euler:
        session.client.update_all_problems()


@ilr.command(**context_settings)
@click.option('--echo/--silent', default=True)
@click.argument('problem-number', nargs=1, type=int, required=False, default=0)
@click.pass_obj
@require_fetch
def send(session, problem_number, echo):
    """ Send the problem(s) to Interactive Project Euler.  See config for default server. """
    problems = []
    if problem_number == 0:
        _problems = session.client.problems
    else:
        _problems = [session.client.problems[int(problem_number) - 1]]

    for _ in _problems:
        problem = {}
        # save problems for which there is code
        if 'code' in _:
            problem.update({'code': _['code']})
            problem.update({'Solved': _.get('Solved')})
            problem.update({'completed_on': _.get('completed_on')})
            problem.update({'correct_answer': _.get('correct_answer')})

        if problem:
            problem.update({'ID': _['ID']})
            problems.append(problem)

    if not problems:
        click.echo('No work to send.  Try ilr solve.')
    else:
        try:
            session.client.ping_ipe()
        except requests.exceptions.ConnectionError:
            if echo:
                click.echo('ieuler server is not running.  Cannot send/save to server.')
            return
        try:
            r = session.client.send_to_ipe(problems)
            if r and echo:
                click.echo('Response:')
                click.echo(json.dumps(r, sort_keys=True, indent=4))

        except BadCaptcha as e:
            click.echo(e)
        except LoginUnsuccessful as e:
            click.echo(e)


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
@click.option('-language', nargs=1, type=str, default=None, help=f'Choose from: {supported_languages()}')
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_context
@click.pass_obj
@require_fetch
def solve(session, ctx, problem_number, language, edit):
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

    if not problem.get('code'):
        content_dict = {_: problem[_] for _ in problem if _ in Client.TEMPLATE_FIELDS}
        content = json.dumps(content_dict, sort_keys=True, indent=4)
        problem['code'] = {
            language_template.language: {'filename': file_name,
                                         'filecontent': language_template.template(content),
                                         'submission': None}}

    if not problem['code'].get(language_template.language):
        content_dict = {_: problem[_] for _ in problem if _ in Client.TEMPLATE_FIELDS}
        content = json.dumps(content_dict, sort_keys=True, indent=4)
        problem['code'][language_template.language] = {'filename': file_name,
                                                       'filecontent': language_template.template(content),
                                                       'submission': None}

    file_content = problem['code'][language_template.language]['filecontent']
    try:
        with open(file_name, 'wt') as f:
            f.write(file_content)
    except FileExistsError:
        with open(file_name, 'rt') as f:
            file_content = f.read()
            problem['code'][language_template.language].update({'filecontent': file_content})

    if edit:
        click.edit(filename=file_name)
        # we also want to update the problem after they edit it
        with open(file_name, 'rt') as f:
            problem['code'][language_template.language].update({'filecontent': f.read()})

    # let's update session.client.problems with updated
    session.client.update_problems([problem])
    # and send to the server
    ctx.invoke(send, problem_number=problem_number, echo=False)


@ilr.command(**context_settings)
@click.option('-language', type=str, nargs=1, help=f'Choose from: {supported_languages()}')
@click.option('--dry/--live', default=False,
              help=f'The --dry option will execute your file but not submit to Project Euler.')
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_context
@click.pass_obj
@require_fetch
def submit(session, ctx, problem_number, dry, language):
    """ Execute a file and submit its stdout to Project Euler. """

    # look for the code to run in session.self.problems
    problem = session.client.problems[problem_number - 1]
    code = problem.get('code')
    if not code:
        click.echo('There is no code to run.  Use ilr solve first.')
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
            if submission_language != session.client.language_template.language:
                click.confirm(
                    f'You have solved this problem in {len(submissions)} languages.  Submission will be in {submission_language}. Next time specify -language or continue.',
                    abort=True)
    else:
        submission_language = _language[0]

    language_template = get_template(submission_language)

    filename = f'{problem_number}{language_template.extension}'

    # update the filecontent (we want self.problems.problem to be in sync with potential changes to file by user)
    try:
        with open(filename, 'rt') as f:
            code[submission_language].update({'filecontent': f.read()})
            problem['code'].update(code)
    except FileNotFoundError:
        with open(filename, 'wt') as f:
            f.write(code[submission_language]['filecontent'])

    session.client.update_problems([problem])

    # execute the file
    # get the result from stdout
    command = [submission_language, filename]
    try:
        answer = subprocess.run(command, capture_output=True, timeout=60)
    except subprocess.TimeoutExpired as e:
        click.echo(e)
        return

    if answer.returncode != 0:
        click.echo('Oops, there was an error running the file:')
        click.echo(answer.stderr)
        return

    answer = answer.stdout.decode().strip('\n')
    if dry:
        click.echo(f'Result of executing: {command}: {answer}')
        return

    # here we will submit to Project Euler
    try:
        response = session.client.submit(problem_number, answer)
    except LoginUnsuccessful as e:
        click.echo(e)
        return

    problem.update(response)

    # update code if successful (if execution makes it here)
    code[submission_language].update({'submission': answer})

    if answer == response['correct_answer'] and answer is not None:
        click.echo('Yay! You did it :)')
        click.echo(f'{response["completed_on"]}')
    else:
        click.echo(f"Sorry, {answer} is not the answer :(")
        if response['completed_on']:
            click.echo(f"But you've already solved this problem...")
            click.echo(f'{response["completed_on"]}')

    problem['code'].update(code)
    session.client.update_problems([problem])
    ctx.invoke(send, problem_number=problem_number, echo=False)
