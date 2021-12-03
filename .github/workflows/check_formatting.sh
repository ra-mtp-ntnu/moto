#!/bin/bash
# MIT License

# Copyright (c) 2021 Raymond Gasper, Sebastian Grans

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://github.com/rgasper/python-black-pull-request-action



if [[ -z ${GITHUB_TOKEN} ]]
then
    echo "Githubs API requires a token. Define the environment variable GITHUB_TOKEN: 'GITHUB_TOKEN : \$\{\{ secrets.GITHUB_TOKEN \}\}' in your workflow's main.yml."
    exit 1
fi

pip install black

github_pr_url=`jq '.pull_request.url' ${GITHUB_EVENT_PATH}`
echo "The pull request url: ${github_pr_url}"
# Removing potential leading/trailing quotes. 
github_pr_url=`sed -e 's/^"//' -e 's/"$//' <<<"$github_pr_url"`
# echo "Downloading PR diff from: ${github_pr_url}"
curl --request GET --url ${github_pr_url} --header "authorization: Bearer ${GITHUB_TOKEN}" --header "Accept: application/vnd.github.v3.diff" > github_diff.txt
all_changed_files=`cat github_diff.txt | grep -E -- "\+\+\+ |\-\-\- " | awk '{print $2}'`
# echo "All files listed in the PR: ${all}"
python_files=`echo "${all_changed_files}" | grep -Po -- "(?<=[ab]/).+\.py$"`
echo "Python files edited in this PR: ${python_files}"

black --check ${python_files}
