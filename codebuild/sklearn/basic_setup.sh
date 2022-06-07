#!/bin/bash

echo repo=${repo}
echo version=${version}
echo platform=${platform}

git clone https://github.com/aws/${repo}.git
mkdir -p ${repo}/docker/${version}-${platform}
mkdir -p ${repo}/docker/${version}-${platform}/aws-batch-extension

cp -r ${repo}/docker/${version}/* ${repo}/docker/${version}-${platform}/
cp -r docker/${version}-${platform}/* ${repo}/docker/${version}-${platform}/

ls -lrt ${repo}/docker/${version}-${platform}/*

echo Basic setup done!