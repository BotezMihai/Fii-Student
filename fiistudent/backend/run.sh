echo "[i] Installing requirements..."
pip3 install -Ur requirements.txt
pip3 install -e .
gunicorn fiistudentrest.app:__hug_wsgi__
