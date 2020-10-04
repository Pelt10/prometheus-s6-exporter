import argparse
import os
import shutil
import subprocess
import time

from prometheus_client import Gauge, start_http_server
import re

status_re = re.compile('(up|down) \(.*\) (\d+) seconds(?:.*want (up|down))?')

S6_SERVICE_UP = Gauge(
    's6_service_up',
    'State of s6 service, 1 = up, 0 = down',
    ['service']
)
S6_SERVICE_WANT_UP = Gauge(
    's6_service_wanted_up',
    'Wanted state of s6 service, 1 = up, 0 = down',
    ['service']
)
S6_SERVICE_STATE_CHANGE_TIMESTAMP_SECONDS = Gauge(
    's6_service_state_change_timestamp_seconds',
    'Unix timestamp of service\'s last state change.',
    ['service']
)


def get_status(svstat_bin, services_dir, service):
    command_process = subprocess.Popen(
        [svstat_bin, ('%s/%s' % (services_dir, service))],
        stdout=subprocess.PIPE,
        universal_newlines=True
    )

    while True:
        return_code = command_process.poll()
        if return_code is not None:
            if return_code == 0:
                command_output = [line.strip() for line in command_process.stdout.readlines()]
            else:
                raise ProcessLookupError('%s return code : %i', (svstat_bin, return_code))
            break

    match = status_re.match(command_output[0])
    up = 1 if match.group(1) == 'up' else 0
    sc = int(match.group(2))
    want = up
    if match.group(3):
        want = 1 if match.group(3) == 'up' else 0
    return up, want, sc


def collect(services_dir, svstat_bin):
    for service in os.listdir(services_dir):
        if service == '.s6-svscan' or os.path.isfile('%s/%s' % (services_dir, service)):
            continue
        up, want, sc = get_status(svstat_bin, services_dir, service)
        S6_SERVICE_UP.labels(service=service).set(up)
        S6_SERVICE_WANT_UP.labels(service=service).set(want)
        S6_SERVICE_STATE_CHANGE_TIMESTAMP_SECONDS.labels(service=service).set(sc)


def exporter(args):
    if not shutil.which(args.svstat):
        raise AttributeError('%s not found' % args.svstat)
    if not os.path.isdir(args.directory):
        raise AttributeError('%s is not directory' % args.directory)
    print('Prometheus S6 exporter Starting...')
    start_http_server(args.addr)
    print('Prometheus S6 exporter running on : 0.0.0.0:%i' % args.addr)
    while True:
        collect(args.directory, args.svstat)
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='S6 Prometheus Exporter')
    parser.add_argument('--svstat', help='svstat binary name', default='s6-svstat')
    parser.add_argument('--directory', help='Path to service directory', default='/etc/service')
    parser.add_argument('--addr', help='Address to expose prometheus metrics on', default='9164', type=int)
    args = parser.parse_args()

    exporter(args)
