import json
import boto3
import requests
from datetime import datetime
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)