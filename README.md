# c3-python-sdk
Python client for C3 Exchange  (v1 API).



## Developer Environment Set Up

1. Install pre-commit tools

- Mac

```bash
brew install pre-commit gawk coreutils
```

- Windows (pending)
- Linux (pending)

2. Create and activate virual python environment with pyenv or venv (python 3.11)

```bash
python3 -m venv local_env
source /local_env/bin/activate
```

Install dependencies

```bash
python -m pip install --upgrade pip wheel setuptools
```

Run the make file with the pre-commit validations

```bash
make install_pre_commit
```