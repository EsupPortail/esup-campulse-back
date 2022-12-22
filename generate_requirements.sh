#!/bin/bash

echo "📦️ generating common.txt"
poetry export -o requirements/common.txt --without-hashes

for env in test preprod prod;
do
echo "📦️ generating $env.txt"
poetry export -o requirements/$env.txt --with $env
done

echo "📦️ generating dev.txt"
poetry export -o requirements/dev.txt --with dev --without-hashes
