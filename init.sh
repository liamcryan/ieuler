#!/bin/bash
# this script assumes positional arguments of the form:
# entity{"key":"value"}
# the current possible entities are: 'cookies' & 'credentials'
# therefore, there should only be $1 & $2 (for now assume $1 is cookies & $2 is credentials)
# *** Note -> only username required in credentials - password not needed ***

# zsh: (this works)
#   ./init.sh "cookies{'PHPSESSID':'a81d3ed4c57c24596ecefab68de13b89'}" "credentials{'username':'limecrayon','password':''}"

if [ "$#" -lt 1 ]
then
  ilr fetch --anonymous
else
  echo "cookies arg: ${1#'cookies'}"
  echo "credentials arg: ${2#'credentials'}"
  python3 -c "from ieuler.client import Client;c = Client();c.dump_cookies(${1#'cookies'});c.dump_credentials(${2#'credentials'})"
  ilr fetch
fi
ilr --help
/bin/bash