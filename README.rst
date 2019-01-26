==============
project ieuler
==============

Interact with project euler.

Description
___________

The idea behind this library is to work on project euler problems while being near to your programming environment.

Terminal
________

In your working directory, create a 'problems' folder and a 'certificates' folder.  Then follow along::

    > ieuler template 1
    template for problem 1 is here: problems\problem_1.py
    > ieuler edit 1

A Notepad opens the template file which looks like this::
    """

    name:
    Multiples of 3 and 5

    content:
    If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9. The sum of these multiples is 23.
    Find the sum of all the multiples of 3 or 5 below 1000.

    """


    def answer():
        """ The answer to Problem 1: Multiples of 3 and 5.

        Solve the problem here!

        :return: your answer
        """
        return


    if __name__ == "__main__":
        """ You can test your code here, just run or debug this file! """
        print(answer())


Well, now, if you want to submit your answer to project euler, how about editing the file and return 10000.  Then save
the file.  Back at the terminal::

    > ieuler submit 1

You will be prompted to input your username, password, and a couple of captcha codes.  10000 is not the answer, and
you will see the project euler message saying so on the console.  If you submit the correct answer, a html page
will be saved in your 'certificates' directory.
