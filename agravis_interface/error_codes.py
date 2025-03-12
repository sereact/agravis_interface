ERROR_CODE_DESCRIPTION = {
    -32000: {
        "code": "E_STOP_TRIGGERED",
        "description": "Emergency stop was activated. Operation halted for safety reasons.",
        "severity": "Critical",
        "resolution": "Inspect the reason for the emergency stop activation. If all clear, release the emergency stop. Resume the system by dragging the resume button."
    },
    -32001: {
        "code": "SAFETY_GUARD_VIOLATION",
        "description": "A safety guard was breached. The robot is in safe stop.",
        "severity": "Critical",
        "resolution": "Inspect the doors and the safety system. Ensure the doors are closed and the cell is empty. If all clear, the system will ask for visual confirmation. Follow the instructions on the screen."
    },
    -32002: {
        "code": "FENCE_SAFETY_GUARD_FAILURE",
        "description": "The fence safety guard system has failed or is not connected. The robot is in safe stop.",
        "severity": "Critical",
        "resolution": "Inspect the doors and the safety system. Ensure the doors are closed and the cell is empty. If all clear, the system will ask for visual confirmation. Follow the instructions on the screen."
    },
    -32003: {
        "code": "SOFTWARE_ERROR",
        "description": "A software fault occurred, possibly due to a bug or unexpected condition.",
        "severity": "Critical",
        "resolution": "Call the second line of support. For 2nd line: Contact Sereact's support team."
    },
    -32004: {
        "code": "DUPLICATE_ID",
        "description": "Station got duplicated requests.",
        "severity": "Operational",
        "resolution": "No action needed. This is an operational warning."
    },
    -32005: {
        "code": "ROBOT_FAILURE",
        "description": "The robot is not responding or is disconnected from the control system.",
        "severity": "Critical",
        "resolution": "Call the second line of support. For 2nd line: Call Sereact's support team."
    },
    -32006: {
        "code": "HARDWARE_FAILURE",
        "description": "Failure of <components>.",
        "severity": "Critical",
        "resolution": "Call the 2nd line of support. For 2nd line: Contact Sereact's support team."
    },
    -32007: {
        "code": "GRIPPER_FAILURE",
        "description": "Gripper malfunctioned, possibly due to misalignment or mechanical issue.",
        "severity": "Operational",
        "resolution": "Call the second line of support. For 2nd line: Contact Sereact's support team."
    },
    -32008: {
        "code": "PLACE_FAILURE_UNSAFE",
        "description": "The robot failed to place the object at the designated location.",
        "severity": "Critical",
        "resolution": "Human Intervention. Check the Placing Position."
    },
    -32009: {
        "code": "CAMERA_FAILURE",
        "description": "The camera system is not functioning, possibly affecting object recognition or positioning.",
        "severity": "Operational",
        "resolution": "Call 2nd line of support. For 2nd line: Check the cables. If the issue persists, contact Sereact's support team."
    },
    -32010: {
        "code": "SOURCE_BIN_EMPTY",
        "description": "The bin from which the robot was supposed to pick an item is empty.",
        "severity": "Operational",
        "resolution": "No action needed. This is an operational warning."
    },
    -32011: {
        "code": "TARGET_BIN_FULL",
        "description": "The bin where the robot was supposed to place an item is full.",
        "severity": "Operational",
        "resolution": "No action needed. This is an operational warning."
    },
    -32012: {
        "code": "ITEM_DROPPED_SAFE",
        "description": "The robot dropped the item during the pick or place operation.",
        "severity": "Operational",
        "resolution": "No action needed. This is an operational warning."
    },
    -32013: {
        "code": "ITEM_DROPPED_UNSAFE",
        "description": "The robot dropped the item during the pick or place operation.",
        "severity": "Critical",
        "resolution": "Human Intervention. Clear the area."
    },
    -32014: {
        "code": "INCOMPATIBLE_ITEM",
        "description": "Station received incompatible items that cannot be picked with the current configuration.",
        "severity": "Operational",
        "resolution": "No action needed. This is an operational warning."
    },
    -32015: {
        "code": "MISSALIGNED_COMPONENTS",
        "description": "The Station is missing <key component> to operate.",
        "severity": "Critical",
        "resolution": "Human Intervention. Please make sure <component> is available."
    },
    -32016: {
        "code": "MAINTENANCE_MODE_ACTIVE",
        "description": "The system is in maintenance mode.",
        "severity": "Maintenance",
        "resolution": "For 2nd line: Please turn the key-switch to exit the maintenance mode."
    },
    -32017: {
        "code": "FIRE_ALARM_TRIGGERED",
        "description": "Fire alarm triggered.",
        "severity": "Critical",
        "resolution": "Follow standard evacuation procedures."
    },
    -32018: {
        "code": "AIR_PRESSURE_IS_LOW",
        "description": "Air pressure is low.",
        "severity": "Critical",
        "resolution": "Call the 2nd line of support. For 2nd line: Check the air pressure at the compressor."
    },
    -32019: {
        "code": "WMS_COMMUNICATION",
        "description": "Error with the WMS communication.",
        "severity": "Critical",
        "resolution": "Call the 2nd line of support. For 2nd line: Try to press the confirm button. If the issue is not resolved, contact Sereact's support team."
    },
    -32020: {
        "code": "ROBOT_IN_EXECUTION",
        "description": "The robot is currently executing a task.",
        "severity": "Operational",
        "resolution": "No action needed. This is an operational warning."
    },
    -32021: {
        "code": "ITEM_NOT_PICKABLE",
        "description": "The item is not pickable.",
        "severity": "Operational",
        "resolution": "No action needed. This is an operational warning."
    },
    -32021: {
        "code": "NOT_SUPPORT_REQUEST",
        "description": "The request is not supported.",
        "severity": "Operational",
        "resolution": "Please send the correct request."
    },
    -32022: {
        "code": "INVALID_REQUEST_ARGUMENTS",
        "description": "The request arguments are invalid.",
        "severity": "Operational",
        "resolution": "Please send the correct request."
    }
}

ERROR_CODE_MAP = {value["code"]: key for key, value in ERROR_CODE_DESCRIPTION.items()}

class JsonRpcError(Exception):
    def __init__(self, code, data=None):
        if isinstance(code, str):
            code = ERROR_CODE_MAP[code]
        self.code = code
        self.data = data
    
    def description(self):
        return ERROR_CODE_DESCRIPTION[self.code]

    