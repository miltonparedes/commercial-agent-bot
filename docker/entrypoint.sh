#!/bin/bash

exec fastapi dev com_agent/api/app.py --reload --host 0.0.0.0 --port 8000
