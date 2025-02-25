#!/bin/bash

CLI_NAME="capital-soap"
CLI_MODULE="demo.cli"
DST_FILE="docs/cli.md"

uv run -m typer $CLI_MODULE utils docs --name $CLI_NAME --output $DST_FILE
