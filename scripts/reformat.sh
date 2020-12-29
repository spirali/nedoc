cd `dirname $0`/..
isort --profile black nedoc tests
black nedoc tests
flake8 nedoc tests --max-line-length=120 --ignore=E203,W503
