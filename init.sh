#!/bin/bash
# this script assumes positional arguments of the form:
# entity{"key":"value"}
# the current possible entities are: 'cookies'
# therefore, there should only be $1 (for now assume $1 is cookies)

# ttyd: (not tried yet)
#   http://127.0.0.1:7681/?arg=cookies{%22PPS%22:123}&arg=default-language-template{%22language%22:%22python3%22}

# zsh: (this works)
#   ./init.sh "cookies{'PHPSESSID':'a81d3ed4c57c24596ecefab68de13b89'}"

if [ "$#" -lt 1 ]
then
  ilr fetch --anonymous
else
  python -c "from ieuler.client import Client;c = Client();c.dump_cookies(${1#'cookies'})"
  ilr fetch
  ilr --help
fi

/bin/bash