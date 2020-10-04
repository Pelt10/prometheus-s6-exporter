# Prometheus s6 exporter
Prometheus s6 exporter is a Python Prometheus exporter for s6 process supervision tool. 

## Installation

```bash
cd /opt/
git clone https://github.com/Pelt10/prometheus-s6-exporter.git
cd /prometheus-s6-exporter
pip install -r requirements.txt
```

## Usage

```bash
usage: exporter.py [-h] [--svstat SVSTAT] [--directory DIRECTORY]
                   [--addr ADDR]

S6 Prometheus Exporter

optional arguments:
  -h, --help            show this help message and exit
  --svstat SVSTAT       svstat binary name
  --directory DIRECTORY
                        Path to service directory
  --addr ADDR           Address to expose prometheus metrics on
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
