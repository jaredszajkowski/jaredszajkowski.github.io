#!/bin/bash
echo What is the commit message?

read message

rm -r public/* && hugo && git add . && git commit -am "$message" && git push
# hugo && git add . && git commit -am "$message" && git push
