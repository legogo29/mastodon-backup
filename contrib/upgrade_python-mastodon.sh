#!/bin/bash
# upgrade the python-mastodon module if Debian/RPM package was outdated
# -----------------------------------------------------------------------------
# this is intended for the case your distribution ships with an outdated version
# of the python-mastodon package (pre-1.5.1). It will simply replace the module
# scripts where your packaging placed them.
#
# © 2022 Izzy <izzysoft AT qumran DOT org>; GPL-3.0-or-later

# -----------------------------------------------------------------------------
# define temp dir and exit-on-error
function cleanup() {
  msg="${1:-"Something went wrong, aborting."}"
  lvl=${2:-1}
  [[ -n "${msg}" && "${msg}" != "-" ]] && {
    echo
    echo "${msg}"
  }
  echo
  rm -rf $tmpdir
  exit $lvl
}

tmpdir=$(mktemp -d)
trap cleanup ERR


# ==============
# ===[ Main ]===
# ==============
# -----------------------------------------------------------------------------
# check whether we need to update python3-mastodon
echo
echo "Let's see if your distribution has a recent version of python3-mastodon..."
if [[ -f /etc/debian_version ]]; then
  mver="$(dpkg -l python3-mastodon |tail -n 1 |awk '{print $3}')"
elif [[ -f /etc/redhat_release || -f /etc/fedora-release ]]; then
  mver="$(yum info python3-Mastodon |grep -Ei '^Version' |awk '{print $3}')"
else
  echo
  echo "Could not determine whether your system is DEB or RPM based."
  echo "To continue, this script would assume that the 'python3-mastodon' module"
  echo "was installed to '/usr/lib/python3/dist-packages/mastodon'."
  echo "Please make sure that this directory exists and contains at least a file"
  echo "named 'Mastodon.py'. If it does not, you better abort this attempt."
  echo ""
  read -n 1 -p "Continue this way? (y/n) " REPLY
  if [[ "${REPLY,,}" = 'y' || "${REPLY,,}" = 'j' ]]; then
    echo
    echo "Assuming package version 1.5.0 to continue."
    echo
    mver="1.5.0-1"
  else
    cleanup "Aborting on user request." 10
  fi
fi

if [[ -z "$mver" ]]; then   # package not even installed or not found
  echo
  echo "Looks like python3-mastodon is not installed at all, so we cannot update it."
  echo "Please install it first and then try again:"
  echo
  if [[ -f /etc/debian_version ]]; then
    echo "  sudo apt install python3-mastodon"
  else
    echo "  yum install python3-Mastodon"
  fi
  cleanup "-"
fi

mver="${mver%%-*}"
IFS='.'; arr=($mver); unset IFS
typeset -i vercode=${arr[2]}+${arr[1]}*100+${arr[0]}*10000
if [[ $vercode -gt 10500 ]]; then    # we need at least v1.5.1 = 10501
  echo "Found version '$mver' – all is fine!"
else
  echo "Found version '$mver' – that's too old. Let's get v1.5.1 and replace the required files."
  if [[ -f /usr/lib/python3/dist-packages/mastodon/Mastodon.py ]]; then
    read -n 1 -p "Continue? (y/n) " REPLY
    echo
    if [[ "${REPLY,,}" = 'y' || "${REPLY,,}" = 'j' ]]; then
      echo "Downloading, extracting and copying (via sudo) files"
      cd $tmpdir
      wget -q --show-progress https://files.pythonhosted.org/packages/7c/80/f12b205fc529fff8e3245fe8e6cafb870f1783476449d3ea2a32b40928c5/Mastodon.py-1.5.1-py2.py3-none-any.whl
      unzip Mastodon.py-1.5.1-py2.py3-none-any.whl
      sudo cp mastodon/__init__.py mastodon/Mastodon.py mastodon/streaming.py /usr/lib/python3/dist-packages/mastodon
      cd - >/dev/null
    else
      cleanup "Aborting on user request." 10
    fi
  else
    echo
    echo "ERROR: Target directory '/usr/lib/python3/dist-packages/mastodon' was not found"
    echo "(or did not contain a 'Mastodon.py')."
    cleanup "-" 5
  fi
  rm -rf $tmpdir
fi


# -----------------------------------------------------------------------------
# Finito
echo
echo "If you saw no errors in the last step, all should be ready now. Enjoy!"
echo
