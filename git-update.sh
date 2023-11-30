#!/bin/bash
echo What is the commit message?

read message

hugo && git add . && git commit -am "message" && git push
