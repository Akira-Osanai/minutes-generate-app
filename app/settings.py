# https://qiita.com/harukikaneko/items/b004048f8d1eca44cba9

import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

ANTHROPIC_API_KEY=os.environ.get("ANTHROPIC_API_KEY")
AI_MODEL=os.environ.get("AI_MODEL")