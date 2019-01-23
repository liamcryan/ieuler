==============
project ieuler
==============

Interact with project euler.

Description
___________

The idea behind this library is to work on project euler problems while being near to your programming environment.

Currently, you interact via the Python Console.  Plans for terminal will be next.

If you know the problem you want to work on, you can create a template file in your working directory containing
the problem details like this:::

    >>> import ieuler
    >>> problem_1 = ieuler.start(problem_number=1)


A file called problem_1.py will be created for you to begin solving.  The file has the problem content so you know
what the actual problem is.  Also, your file won't get overwritten if you call euler.get with problem number 1 again.

Let's suppose you go to problem_1.py and fill out the function answer in the template like this::

    def answer():
    """ The answer to Problem 1: Multiples of 3 and 5.

    Solve the problem here!

    :return: your answer
    """

    def series():
        # this is not the answer to this problem :)
        v = 0
        while True:
            yield v
            v += 1

    total = 0
    for i in series():
        if i >= 1000:
            break
        total += i

    return total

Each template contains a function called answer and you should not change its name.  This is because if we want to
submit our answer to project euler, the answer function will be called, and the value that is returned will be
submitted.  Here is what that looks like (go back to the python console)::

    >>> problem_1.submit(guess=p1)

Now, you have submitted your answer to project euler.  If you have the correct answer, then you will get a
certificate.  A file called problem_1_certificate.html will be saved with your congratulations.
