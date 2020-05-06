=========================
Interactive Project Euler
=========================

Interact with Project Euler https://projecteuler.net/ via the command line.

The main purpose of this tool is for a dedicated place to work on your Project Euler problems.

Installation
++++++++++++

Currently available at github.  One dependency is not yet on pypi so it must be installed separately from github as well::

    % pip install git+https://github.com/liamcryan/ieuler.git
    Collecting git+https://github.com/liamcryan/ieuler.git
    Cloning https://github.com/liamcryan/ieuler.git to /private/var/folders/p2/lmvnwvb554992_wcsc5rh6kw0000gn/T/pip-req-build-6hjf9n9_
    ...
    ...
    % pip install git+https://github.com/liamcryan/rever.git


Quickstart
++++++++++

You are here to see how it feels to work on Project Euler problems from the command line.

Here is the help::

    % ilr --help
    Usage: ilr [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      config  Get or set configuration options.
      fetch   Fetch the problems from Project Euler & Interactive Project Euler.
      ls      List out the problems from Project Euler.
      send    Send the problems to Interactive Project Euler.
      solve   Solve a problem in your language of choice.
      submit  Execute a file and submit its stdout to Project Euler.
      view    View a problem and your associated code or submission information.

There are a few configurations that you might want to check out::

    % ilr config
    {
        "credentials": {
            "password": "*******",
            "username": "limecrayon"
        },
        "language": "python",
        "server": {
            "host": "127.0.0.1",
            "port": 5000
        }
    }

When you log into Project Euler (submitting problems requires a login via this tool), the credentials are saved in your working directory.  A default language is shown - this means generated files to solve will be templated in Python.  Default server information is available as well. The commands fetch and send utilize this server, however, this server must be running or started by you https://github.com/liamcryan/ieuler-server.

If you are starting fresh, or don't have the problems saved locally, you need to fetch them::

    % ilr fetch

This will fetch the problems from Project Euler and Interactive Project Euler.  Interactive Project Euler doesn't exist yet, but will be a server that gets/updates the code and notes you have worked on for a given problem.

Now that we are set up, let's start solving.  We might want to have an idea of what the problems are.  Let's not list out all of the problems from Project Euler, but feel free to type::

    % ilr ls
    {
        "Description / Title": "Multiples of 3 and 5",
        "ID": "1",
        "Solved By": "941172",
        "page_url": "https://projecteuler.net/archives",
        "problem_url": "https://projecteuler.net/problem=1"
    }{
        "Description / Title": "Even Fibonacci numbers",
        "ID": "2",
        "Solved By": "749228",
        "page_url": "https://projecteuler.net/archives",
        "problem_url": "https://projecteuler.net/problem=2"
    }{
        "Description / Title": "Largest prime factor",
    :

You can use the down arrow to continue scrolling through them.  There are 704 right now.  These problems are fetched from Project Euler and stored locally in a file called .problems.

Now that we have an idea of the problems we might want to work on, let's just pick problem 10 to solve::

    % ilr solve -language=python 10
    """{
        "Description / Title": "Summation of primes",
        "ID": 10,
        "Problem": "<div class=\"problem_content\" role=\"problem\">\n<p>The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.</p>\n<p>Find the sum of all the primes below two million.</p>\n</div>",
        "Solved By": "227482",
        "page_url": "https://projecteuler.net/archives",
        "problem_url": "https://projecteuler.net/problem=10"
    }

    """


    def answer():
        """ Solve the problem here! """
        return 0


    if __name__ == "__main__":
        """ Try out your code here """
        print(answer())
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    ~
    "10.py" 20L, 557C


So we are asking to solve problem 10 using Python.  What happened is a .py file is created with a basic template for coding up an answer and printing the answer to stdout.  Also, the file opens in vim so you can edit it.  Don't feel like you need to edit it here; you can always open up the file (10.py in this case) in an editor of your choice.

Once you are happy with the code you have written you will want to run it.  Save the changes to the file then, for this example::

    % python 10.py
    0

Or you can use submit command and the --dry flag to execute the code and print the answer::

    % ilr submit --dry 10
    Result of executing: ['python', '10.py']: 0

It looks like the answer came out to be 0.  Let's submit to Project Euler::

    % ilr submit 10
    A captcha is required.  Would you like to continue? [y/N]: y
    <captcha image will be presented within terminal>
    Please enter the captcha: 37856
    Sorry, 0 is not the answer :(


Ok, so there it is.  0 is not the answer.  Now if we want to view a submitted problem, we can run::

    % ilr view 10
    {
        "Description / Title": "Summation of primes",
        "ID": "10",
        "Problem": "<div class=\"problem_content\" role=\"problem\">\n<p>The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.</p>\n<p>Find the sum of all the primes below two million.</p>\n</div>",
        "Solved": false,
        "Solved By": "227482",
        "code": {
            "python": {
                "filecontent": "\"\"\"{\n    \"Description / Title\": \"Summation of primes\",\n    \"ID\": 10,\n    \"Problem\": \"<div class=\\\"problem_content\\\" role=\\\"problem\\\">\\n<p>The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.</p>\\n<p>Find the sum of all the primes below two million.</p>\\n</div>\",\n    \"Solved By\": \"227482\",\n    \"page_url\": \"https://projecteuler.net/archives\",\n    \"problem_url\": \"https://projecteuler.net/problem=10\"\n}\n\n\"\"\"\n\n\ndef answer():\n    \"\"\" Solve the problem here! \"\"\"\n    return 0\n\n\nif __name__ == \"__main__\":\n    \"\"\" Try out your code here \"\"\"\n    print(answer())\n",
                "filename": "10.py",
                "submission": "0"
            }
        },
        "completed_on": null,
        "correct_answer": null,
        "page_url": "https://projecteuler.net/archives",
        "problem_url": "https://projecteuler.net/problem=10",
    }

This gives us information on the problem as it pertains to us.  It shows the code currently saved, if the problem is completed, and if the answer is correct, along with some data inherent to the problem.

This information is saved in a file called .problems, letting you pick up from where you last left off, and saving your code as well.  You can generate your saved .py file if you need to.  Try deleting the 10.py file and then run::

    % ilr solve 10 --no-edit
    % ls
    10.py

The file, 10.py, has been generated.

If you are finished and would like to send your progress to Interactive Project Euler, you can type::

    % ilr send

Your progress is saved remotely.  If you want to begin again from another computer or environment, you can pick up where you left off.

Roadmap
+++++++

I am playing around with the idea of using ttyd https://github.com/tsl0922/ttyd to make Interactive Project Euler more accessible.  ttyd will let someone access a terminal from a browser.

Create a docker image with the ieuler code, and languages to execute the code.
