name: Post or Update Articles to API

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  process-articles:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests

    - name: Process articles
      env:
        API_KEY: ${{ secrets.API_KEY }}
        API_URL: ${{ secrets.API_URL }}
      run: python hack/upload.py
