import requests

url = "http://localhost:8000/api"
EXAMPLE_GRASP_UNTIL_EMPTY = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "robot.grasp_until_empty",
    "params": {
        "palletId": "qrf343",
        "pickArea": "pick_1",
        "placeArea": "place_1"
    }
}


EXAMPLE_ROBOT_CHECK_READY = {
    
    "jsonrpc": "2.0",
    "id": 1,
    "method": "robot.check_ready",

}

def call_api(data, header={}):
    response = requests.post(url, json=data, headers=header)
    return response.json()

def check_ready(header={}):
    return call_api(EXAMPLE_ROBOT_CHECK_READY, header)

def grasp_until_empty(header={}):
    return call_api(EXAMPLE_GRASP_UNTIL_EMPTY, header)

header = {
    "X-RAISE-ERROR": "1"
}
if __name__ == "__main__":
    print(check_ready())
    print(grasp_until_empty())
    print(grasp_until_empty(header))
