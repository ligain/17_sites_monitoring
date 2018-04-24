  
# Sites Monitoring Utility
This tool gives you information of domain expiration and HTTP status of URLs.  It take plain `txt` file with URLs. Each URL on a new line.
  
# Installation
**Python 3 should be already installed.**

0) Get source code
```bash
$ git clone https://github.com/ligain/17_sites_monitoring.git
```

1) Create virtual environment in the directory where you want to place project.
```bash
$ cd 17_sites_monitoring/
python3 -m venv .env
```

2) Activate virtual environment
```bash
$ . .env/bin/activate
```

3) Install all dependencies via pip
```bash  
pip install -r requirements.txt # alternatively try pip3  
```  
# Usage
```bash
$ cd 17_sites_monitoring/
$ python check_sites_health.py -p ../urls.txt
Checked URLs:
---------------------------------------------------------------------------------------------------------
Url                                                          |      Is URL ok       |    Domain status
---------------------------------------------------------------------------------------------------------
http://www.i.ua/                                             |         yes          |        error
https://habrahabr.ru/                                        |         yes          |          OK
https://www.gismeteo.ua/                                     |         yes          |        error
...
```
  
# Project Goals  
  
The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)