#!/bin/bash

#OD_API='https://2lvd1jdy8l.execute-api.us-west-2.amazonaws.com/test/classify'
OD_API=$1
echo $OD_API

for f in $(ls images/*.jpg)
do
    curl -X POST -H 'content-type: image/jpeg' --data-binary @$f $OD_API | jq .
done
