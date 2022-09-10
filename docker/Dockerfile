# Jupyter-Python image builder
# ==============================
# Building an image:
# docker build --tag com506_jupyter_python .
# Starting stand-alone container (w/o docker-compose):
# docker run -d -p 10001:10001 --user root --name com506 -v $(pwd):/root/work com506:latest

# based on Debian linux
FROM python:3.7-slim

RUN python -m pip install --upgrade pip

# Intsall web browser and virtual display for Selenium
# https://velog.io/@jmon/%EC%9A%B0%EB%B6%84%ED%88%AC-%EC%84%9C%EB%B2%84%EC%97%90%EC%84%9C-%ED%8C%8C%EC%9D%B4%EC%8D%AC-%EC%85%80%EB%A0%88%EB%8B%88%EC%9B%80-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0-Ubuntu-Server-Python-Selenium-JMON
WORKDIR /root
RUN apt-get update -y \
  && apt-get install wget gnupg -y \
  && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update -y \
  && apt-get install google-chrome-stable=105.0.5195.102-1 -y \
  && google-chrome --version 
# Install webdriver with versione matched to the browser
# https://sites.google.com/chromium.org/driver/
#RUN apt-get install unzip -y
RUN apt-get install unzip xvfb -y \
  && wget -N https://chromedriver.storage.googleapis.com/105.0.5195.52/chromedriver_linux64.zip \
  && unzip chromedriver_linux64.zip \
  && rm chromedriver_linux64.zip
# Install tor service to use proxy
RUN apt-get install tor -y \
  && service tor start
# Install cron (and its task) to automate script run
RUN apt-get install nano cron -y \
  && (crontab -l ; echo "00 13 * * * /root/work/scheduled_run.sh") | crontab - \
  && service cron restart

# Install required Python packages
# (Rebuilds upon every requirements file change)
COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

# Generate jupyter configs
# COPY jupyter_server_config.py /etc/jupyter/
RUN jupyter notebook --generate-config \
  && echo "c.NotebookApp.token='com506termproject'" >> /root/.jupyter/jupyter_notebook_config.py \
  && echo "c.NotebookApp.notebook_dir='/root/work/notebook'" >> /root/.jupyter/jupyter_notebook_config.py

# Additional setup for Google colab connectivity
# supports http only, source and destination port must be the same
RUN echo "c.NotebookApp.allow_origin='https://colab.research.google.com'" >> /root/.jupyter/jupyter_notebook_config.py \
  && echo "c.NotebookApp.port_retries=0" >> /root/.jupyter/jupyter_notebook_config.py \
  && pip install --upgrade jupyter_http_over_ws==0.0.7 \
  && jupyter serverextension enable --py jupyter_http_over_ws

# Launch jupyter notebook server
EXPOSE 10001
ENTRYPOINT jupyter notebook \
    --ip 0.0.0.0 --port 10001 \
    --allow-root --no-browser
