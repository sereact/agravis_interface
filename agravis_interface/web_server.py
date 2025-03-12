import random
import asyncio
import json
import os
from tinydb import TinyDB, Query
from aiohttp import web
import aiohttp
import aiohttp_cors
import os
import datetime
from datetime import datetime, timezone
from agravis_interface.logger import SereactLogger
from agravis_interface.error_codes import ERROR_CODE_DESCRIPTION, ERROR_CODE_MAP, JsonRpcError

logger = SereactLogger("sereact_server")


def generate_timestamp() -> str:
    """
    Generate a timestamp.
    Returns:
        str: Timestamp.
    """
    return datetime.now(tz=timezone.utc).isoformat()


PORT = os.getenv("SEREACT_PORT", 8000)
ACTIVEANTS_URL = os.getenv("ACTIVEANTS_URL", "http://localhost:8001")
SLEEP_TIME_SECONDS = int(os.getenv("SLEEP_TIME_SECONDS", 3))
MAX_ITEMS_PER_PALLET = int(os.getenv("MAX_ITEMS_PER_PALLET", 20))
MAX_ITEMS_PER_PLACE = int(os.getenv("MAX_ITEMS_PER_PLACE", 7))
TIME_PER_PICK = int(os.getenv("TIME_PER_PICK", 5))

STATION_ID = os.getenv("STATION_ID", "SEREACT_1")

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
    {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "robot.check_ready",
}
}

EXAMPLE_ROBOT_CHECK_READY_RESPONSE = {
    "jsonrpc": "2.0",
    "id": 1,    
    "result": {
        "success": True,
    }
}

EXAMPLE_GRASP_UNTIL_EMPTY_RESPONSE = {
    "jsonrpc": "2.0",
    "id": 1,
    "result":
    {
        "success": True,
        "payload": {
            "itemsPicked": 6,
            "itemsPlaced": 6,
            "isTargetFull": True,
            "isPalletEmpty": True,
        }
    }
}

EXAMPLE_ERROR_RESPONSE = {
    "jsonrpc": "2.0",
    "error": {
        "code": "ERROR_CODE",
        "message": "ERROR_MESSAGE",
    "data": {
        "status": "error",
        "title": "ERROR_TYPE",
        "description": "ERROR_DESCRIPTION",
        "itemsPicked": 1,
        "itemsPlaced": 0,
        "isTargetFull": False,
        "isPalletEmpty": False,
    }
    },
    "id": 2
}

class PicksDB:
    def __init__(self) -> None:
        self.db = TinyDB("picks.json")
        self.picks = self.db.table("picks")
        self.query = Query()
        self.remove_all_picks()

    def remove_all_picks(self):
        self.picks.truncate()
        self.cancelled_picks.truncate()
        self.completed_picks.truncate()
        self.cell_status_updates.truncate()

    def add_completed_pick(self, pick):
        pick_id = pick["jobId"]
        pick["_id"] = pick_id
        self.completed_picks.insert(pick)

    def add_new_cell_status(self, status):
        self.cell_status_updates.insert(status)

    def get_cell_status(self):
        all_statuses = self.cell_status_updates.all()
        if all_statuses:
            return sorted(all_statuses, key=lambda x: x["timeStamp"], reverse=True)[0]
        else:
            return {}

    def add_pick(self, pick):
        pick["state"] = "PENDING"
        self.picks.insert(pick)

    def get_active_picks(self):
        return self.picks.all()

    def remove_pick(self, pick_id):
        self.picks.remove(self.query._id == pick_id)

    def update_pick(self, pick_id, update_dict):
        # print(f"Updating pick {pick_id} with {update_dict}")
        # check if self.picks contains the pick_id
        if not self.picks.contains(self.query._id == pick_id):
            raise ValueError(f"Pick {pick_id} not found")
        # else:
        #     print("Pick found")
        self.picks.update(update_dict, self.query._id == pick_id)

    def get_pick(self, pick_id):
        return self.picks.get(self.query._id == pick_id)



class Server:
    def __init__(self, host="0.0.0.0", port=PORT):
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.main_loop())
        self.setup_app()
        self.request = None
        self.request_called = None
        self.ws_clients = set()
        
        self.error_code = ""
        self.error_description = ""
        self.test_change_state_called = False

        self.pick_area_empty = {
            "pick_1": False,
            "pick_2": False,
            "pick_3": False,
        }
        self.item_picked = {
            "pick_1": 0,
            "pick_2": 0,
            "pick_3": 0,
        }
        self.max_item_per_pallet = MAX_ITEMS_PER_PALLET
        self.max_item_per_place = MAX_ITEMS_PER_PLACE
        self.is_picking = False
        logger.info("Server initialized")

    def reset_item_picked(self, pick_area):
        self.item_picked[pick_area] = 0
        self.pick_area_empty[pick_area] = False

    def update_item_picked(self, pick_area, pick_number):
        self.item_picked[pick_area] += pick_number
        if self.item_picked[pick_area] == self.max_item_per_pallet:
            self.pick_area_empty[pick_area] = True

    async def get(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await self._check_response(response)

    async def _check_response(self, response):
        if response.status != 200:
            raise Exception(
                f"Failed to get response from {response.url} with status code {response.status} and text {response.text}"
            )
        else:
            content_type = response.headers.get("Content-Type", "")
            data = None
            if "application/json" in content_type:
                # If the response is JSON, decode it
                data = await response.json()
                logger.info(f"Received JSON: {data}\n")
            elif "text/plain" in content_type:
                # If it's plain text, handle accordingly
                data = await response.text()
                logger.info(f"Received plain text: {data}\n")
            else:
                logger.info(f"Unexpected content type: {content_type}\n")
            return data

    async def post(self, url, data):
        logger.info(f"Sending to {url} with data: {data}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                return await self._check_response(response)

    async def put(self, url, data):
        logger.info(f"Sending to {url} with data: {data}")
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=data) as response:
                return await self._check_response(response)

    def setup_app(self):
        self.app = web.Application()
        self.app.router.add_post("/api", self.handle_api_call)
        self.setup_cors()

        for route in list(self.app.router.routes()):
            logger.info(f"Route: {route}")

    async def validate_recevied_data(self, data, example_data):
        # logger.info(f"Validating received data {data} against {example_data}")
        for key in example_data:
            if key not in data:
                raise ValueError(f"Key {key} not found in data")
            if not isinstance(data[key], type(example_data[key])):
                raise ValueError(f"Key {key} is not of type {type(example_data[key])}")

    async def index(self, request):
        return None


    async def handle_api_call(self, request):
        """
        Handle API calls.

        Args:
            request: The web request object.

        Returns:
            web.Response: A JSON response from the API call.
        """
        msg = await request.json()
        header = request.headers
        res = await self.json_rpc(msg, header)
        return web.Response(body=json.dumps(res))


    def setup_cors(self):
        """Configure CORS on all routes in the web application."""
        cors = aiohttp_cors.setup(
            self.app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                )
            },
        )

        # Configure CORS on all routes.
        for route in list(self.app.router.routes()):
            cors.add(route)


    async def json_rpc(self, msg, header):
        if isinstance(msg, dict):
            return await self.handle_request(msg, header)

    async def handle_request(self, msg, header):
        res = {
            "jsonrpc": "2.0",
        }
        res["id"] = msg["id"]
        method = msg.get("method")
        params = msg.get("params")
        call_res = None
        try:
            if method=="robot.grasp_until_empty":
                if header.get("X-RAISE-ERROR"):
                    raise JsonRpcError("ITEM_NOT_PICKABLE", {"itemsPicked": 1, "itemsPlaced": 0, "isTargetFull": False, "isPalletEmpty": False})
                await call_res= self.grasp_until_empty(params)

            elif method=="robot.check_ready":        
                await call_res = self.check_ready(params)
            res["result"] = call_res
        except JsonRpcError as e:
            description = ERROR_CODE_DESCRIPTION[e.code]
            res["error"] = {
                "code": e.code,
                "message": description["description"],
                "data": {
                    "status": "error",
                    "title": description["code"],
                    "description": description["description"],
                }
            }
            if isinstance(e.data, dict):
                res["error"]["data"].update(e.data)
        return res  
    
    async def check_ready(self, params):
        if self.is_picking:
            return {"success": False}
        else:
            return {"success": True}    
        
    
    async def grasp_until_empty(self, params):
        data = {
                    "itemsPicked": 0,
                    "itemsPlaced": 0,
                    "isTargetFull": False,
                    "isPalletEmpty": False,
                }
        if self.is_picking:
            raise JsonRpcError("ROBOT_IN_EXECUTION", data)
        
        if "palletId" not in params:
            raise JsonRpcError("INVALID_REQUEST_ARGUMENTS", data)
        
        pallet_id = params["palletId"]
        if "pickArea" not in params or "placeArea" not in params:
            raise JsonRpcError("INVALID_REQUEST_ARGUMENTS", data)
        
        pick_area = params["pickArea"]
        if pick_area not in self.pick_area_empty:
            raise JsonRpcError("INVALID_REQUEST_ARGUMENTS", data)
        
        pick_area_empty = self.pick_area_empty[pick_area]
        if pick_area_empty:
            self.reset_item_picked(pick_area)


        self.is_picking = True
        item_left_from_pallet = self.max_item_per_pallet - self.item_picked[pick_area]

        picks_items = random.randint(3, MAX_ITEMS_PER_PLACE)
        target_full = True
        if picks_items > item_left_from_pallet:
            picks_items = item_left_from_pallet
            target_full = False

        self.update_item_picked(pick_area, picks_items)
        data["itemsPicked"] = picks_items
        data["itemsPlaced"] = picks_items
        data["isTargetFull"] = target_full
        data["isPalletEmpty"] = self.pick_area_empty[pick_area]
        await asyncio.sleep(SLEEP_TIME_SECONDS*picks_items)
        self.is_picking = False
        return data
    
    def create_response(self, payload, success=True):
        return {"success": success, "payload": payload}
    
    def main(self):
        runner = aiohttp.web.AppRunner(self.app)
        self.loop.run_until_complete(runner.setup())
        ssl_context = None

        site = aiohttp.web.TCPSite(
            runner, host="0.0.0.0", port=self.port, ssl_context=ssl_context
        )
        self.loop.run_until_complete(site.start())
        logger.info(f"Server running on port {self.port}")
        self.loop.run_forever()


def main():
    server = Server()
    server.main()


if __name__ == "__main__":
    main()
