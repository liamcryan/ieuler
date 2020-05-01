import json
import os
import subprocess
import threading
import time

import click

from ieuler import ieuler


class Session(object):
    def __init__(self):
        self.client = ieuler.Client(
            cookies_filename='../.cookies',
            credentials_filename='../.credentials',
            problems_filename='../.problems'
        )
        self.get_all_problems_thread = None
        if not self.client.problems:
            self.get_all_problems_thread = threading.Thread(target=self.client.get_all_problems)
            self.get_all_problems_thread.start()


@click.group()
@click.pass_context
def cli(ctx):
    # this gets called each time a cli.command is invoked (not for --help)
    ctx.obj = Session()


@cli.command()
@click.pass_obj
def ls(session):
    """ List out the problems from Project Euler. """

    def _generate_output():
        for _ in session.client.problems:
            yield json.dumps(_, sort_keys=True, indent=4)

    while not session.client.problems:
        time.sleep(.25)  # assumes background thread successful in fetching at least 1 problem otherwise infinite

    click.echo_via_pager(_generate_output, color='green')


@cli.command()
@click.option('-language', nargs=1, type=str)
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_obj
def solve(session, problem_number, language):
    """ Solve a problem in your language of choice. """

    problem = session.client.get_detailed_problem(number=problem_number)
    # todo possible race condition - if background thread updates problems (list) when
    #   this tries to update.  note i suppose any time this is called there is a race condition
    #   if the background thread runs
    session.client.update_problems([problem])

    # todo should check the language by running a check like python --version
    # todo then pull in the language template
    if not language:
        language = 'python'
    if language != 'python':
        click.confirm('sorry, only python right now :/. Continue?')

    filename = f'{problem["ID"]}.py'

    if not os.path.exists(filename):
        with open(filename, 'wt') as f:
            content = json.dumps(problem, sort_keys=True, indent=4)
            f.write(
                f'"""{content}\n\n"""\n\n\ndef answer():\n    """ Solve the problem here! """\n    return 0\n\n\nif __name__ == "__main__":\n    """ Try out your code here """\n    print(answer())\n')
    click.edit(filename=filename)


@cli.command()
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_obj
def status(session, problem_number):
    """ Get the status of a problem. """
    problem = session.client.problems[int(problem_number) - 1]
    json.dumps(problem, sort_keys=True, indent=4)


@cli.command()
@click.argument('problem-number', nargs=1, type=int, required=True)
@click.pass_obj
def submit(session, problem_number):
    """ Execute a file and submit its stdout to Project Euler. """
    # todo look in the session.client.problems for the code key,
    #   get the correct filename and language
    filename = f'{problem_number}.py'

    # execute the file
    # get the result from stdout
    answer = subprocess.run(['python', filename], capture_output=True)
    if answer.returncode != 0:
        click.echo('Oops, there was an error running the file:')
        click.echo(answer.stderr)
        return

    answer = answer.stdout.decode().strip('\n')

    with open(filename, 'rt') as f:
        problem = {'ID': str(problem_number),
                   'code': {'python': {'filecontent': f.read(), 'submission': answer, 'filename': filename}}}

    response = session.client.submit(problem_number, int(answer))
    response.update({'ID': problem_number})

    if answer == response['correct_answer']:
        click.echo('Yay! You did it :)')
        click.echo(f'{response["completed_on"]}')
    else:
        click.echo("Sorry, that's not it :(")
        if response['completed_on']:
            click.echo(f"But you've already solved this problem...")
            click.echo(f'{response["completed_on"]}')

    response.update(problem)  # update the response with the executed code/language (saves to .problems)
    # todo possible race condition - if background thread updates problems (list) when
    #   this tries to update.  note i suppose any time this is called there is a race condition
    #   if the background thread runs
    session.client.update_problems([response])
