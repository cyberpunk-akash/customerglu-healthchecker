import json
import psutil
import subprocess
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

health_stats_path = "/healthstats"
running_processes_path = "/runningprocesses"
vm_health_check_path = "/vmhealthcheck"

getMethod = "GET"

def lambda_handler(event, context):
    httpMethod = event['httpMethod']
    path = event['path']

    if path == health_stats_path:
        response = get_health_stats()

    elif path == running_processes_path:
        response = get_running_processes()

    elif path == vm_health_check_path:
        response = vm_health_check()

    else:
        response = buildResponse(404, 'Wrong URL')

    return response


def get_health_stats():
    cpu_freq = psutil.cpu_freq()
    cpu_times_percent = psutil.cpu_times_percent(interval=0.1)

    virtual_memory = psutil.virtual_memory()

    response = {}

    response['cpu_times_utilization_percentage'] = cpu_times_percent
    response['current_frequency'] = cpu_freq[0]
    response['total_physical_memory'] = virtual_memory[0]
    response['total_available_physical_memory'] = virtual_memory[1]
    response['percent_usage_physical_memory'] = virtual_memory[2]

    return buildResponse(200, response)
def vm_health_check():
    response = False

    try:
        timeout = 5
        vm = "google.com"
        result = subprocess.run(["ping", "-c", "1", "-W", str(timeout), vm], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)

        if result.returncode != 0:
            response = {"result": True, "Message": "VM is up"}

        elif result.returncode == 0:
            response = {"result": False, "Message": "VM is down"}

        return buildResponse(200, response)

    except subprocess.CalledProcessError as e:
        print(f"CalledProcessError occurred: {str(e)}")
        response = {"result": False, "Message": "VM is down"}

    except Exception as e:
        # Handle other exceptions that may occur
        print(f"An unexpected error occurred: {str(e)}")
        response = {"result": False, "Message": "VM is down"}

    return buildResponse(200, response)

def get_running_processes():
    processes_details = []
    for process in psutil.process_iter():
        process_details = {}
        print("process =" + str(process))
        process_details["pid"] = process.pid
        process_details["name"] = process.name()
        process_details["status"] = process.status()

        processes_details.append(process_details)

    response = processes_details

    return buildResponse(200, response)

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

    if body is not None:
        print("body = " + str(body))
        response['body'] = json.dumps(body)

    return response