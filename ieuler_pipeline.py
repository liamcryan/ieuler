"""
### **CI/CD Pipeline**

The pipeline to build and test ieuler.

python pipeline.py --local

https://www.conducto.com/app/s/uim-ssp/820837802c5070f7891b4f13f93273ce35705984eb4e26cdc71d5bc01dce80d7
"""

import conducto as co


def run() -> co.Serial:
    image = co.Image("python:3.7", copy_branch="master",
                     copy_url="https://github.com/liamcryan/ieuler.git")
    with co.Serial(image=image, doc=co.util.magic_doc()) as pipeline:
        co.Exec('pip install -r requirements.txt', name='build')
        co.Exec('pytest', name='tests')
    return pipeline


if __name__ == "__main__":
    print(__doc__)
    co.main(default=run)
