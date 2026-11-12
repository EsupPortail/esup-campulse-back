#!/bin/bash

echo "📦️ generating common.txt"
uv pip compile pyproject.toml -o requirements/common.txt --index-strategy unsafe-best-match --no-annotate

for env in saas test preprod prod; do
    echo "📦️ generating $env.txt"
    uv pip compile pyproject.toml --group $env -o requirements/$env.txt --index-strategy unsafe-best-match --no-annotate
done

echo "📦️ generating dev.txt"
uv pip compile pyproject.toml -o requirements/dev.txt --index-strategy unsafe-best-match --no-annotate

