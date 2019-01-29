"""
The cli will look like:

ieuler template 1
ieuler edit 1
ieuler submit 1

when template is called, a directory called templates will be created where the user calls the command
same for submit

"""
import click

import urllib3
import ieuler

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.group()
def cli():
    pass


@cli.command()
@click.option('-problem_directory', default='problems', type=click.Path(exists=True),
              help='the directory you wish to save your problms')
@click.argument('problem_number', type=int, nargs=-1)
def template(problem_number, problem_directory):
    """ create a template for a problem number"""
    for number in problem_number:
        p = ieuler.template(problem_number=number, problem_directory=problem_directory)
        click.echo('template for problem {} is here: {}'.format(number, p.file()))


@cli.command()
@click.option('-problem_directory', default='problems', type=click.Path(exists=True))
@click.argument('problem_number', type=int, nargs=1)
def edit(problem_number, problem_directory):
    """ edit the template """
    p = ieuler.Euler(problem_number, problem_directory)
    click.edit(filename=p.file())
    click.echo('the editor has been closed')

@cli.command()
@click.option('-certificate_directory', default='certificates', type=click.Path(exists=True))
@click.option('-problem_directory', default='problems', type=click.Path(exists=True))
@click.argument('problem_number', type=int, nargs=-1)
def submit(problem_number, problem_directory, certificate_directory):
    """ submit the problem to project euler """
    for number in problem_number:
        p = ieuler.Euler(number, problem_directory)
        p.retrieve()
        p.submit(certificate_directory=certificate_directory)
        if p.certification.status:
            click.echo('certification for problem {} is here: {}'.format(p.number, p.certification.file()))
