#!/usr/bin/python3

import os
from datetime import datetime
import pprint

from kubernetes import client, config
from kubernetes.stream import stream


CONFIG = '/home/alayna/.kube/my-sandbox'
NAMESPACE = "dev-kuznetsova"
EXPECTED_VARS = ["OTEL_TRACING_ENABLED", "OTEL_TRACING_SAMPLER_RATIO", "OTEL_OTLP_COLLECTOR_URL"]


config.load_kube_config(CONFIG)
cl = client.CoreV1Api()


script_dir = os.path.dirname(os.path.realpath(__file__))
timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
out_file = open(f'{script_dir}/env_vars_{timestamp}.txt', 'w')
out_file.write('\n==========================\nОтсутствуют переменные\n==========================\n')


# Получаем список платформы (т.е. подов, кроме инфраструктурных)
platform_pods = []
for pod in cl.list_namespaced_pod(NAMESPACE, field_selector='status.phase=Running', label_selector='zyfra.com/product').items:
    platform_pods.append(pod.metadata.name)
platform_pods.sort()


# Получаем список платформы (т.е. подов, кроме инфраструктурных)
def get_platform_pods():
    platform_pods = []
    for pod in cl.list_namespaced_pod(NAMESPACE, field_selector='status.phase=Running', label_selector='zyfra.com/product').items:
        platform_pods.append(pod.metadata.name)
    return platform_pods.sort()


# Получаем список инфраструктурных подов
def get_infrastructure_pods():
    infrastructure_pods = []
    for pod in cl.list_namespaced_pod(NAMESPACE, field_selector='status.phase=Running', label_selector='!zyfra.com/product').items:
        infrastructure_pods.append(pod.metadata.name)
    infrastructure_pods.sort()
    return infrastructure_pods.sort()



def check_env_vars_of_a_pod():
    
    pod_desc = cl.read_namespaced_pod(name=pod, namespace=NAMESPACE)
    containers = [c.name for c in pod_desc.spec.containers]
    containers.sort()
    for c in containers:

        pod_env_vars = stream(
                  cl.connect_get_namespaced_pod_exec, pod, NAMESPACE, container=c,
                  command="env", stderr=True, stdin=True, stdout=True, tty=True
        )
        missing_vars = []
        for v in EXPECTED_VARS:
            if not v in pod_env_vars:
                missing_vars.append(v)
        if missing_vars:
            out_file.write(f'    {c}\n')
            [out_file.write(f'        {v}\n') for v in missing_vars]




# def main():
    # script_dir = os.path.dirname(os.path.realpath(__file__))
    # timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    # out_file = open(f'{script_dir}/env_vars_{timestamp}.txt', 'w')
    # out_file.write('\n==========================\nОтсутствуют переменные\n==========================\n')

    # pods_to_check = get_platform_pods()
    # print(pods_to_check)
    #pods_to_check = get_infrastructure_pods(cl)

    # i = 1
    # for pod in pods_to_check:
    #     out_file.write(f'{i}) {pod}\n')
    #     check_env_vars_of_a_pod(cl, pod)
    #     i += 1
    # out_file.write(f'\n==========================\nВсего проверено) {len(pods_to_check)} подов\n')



i = 1
for pod in platform_pods:
    out_file.write(f'{pod}\n')
    check_env_vars_of_a_pod()
    i += 1
out_file.write(f'\nВсего проверено {len(platform_pods)} подов\n')





