"""
Graph Database Schema Definition
Auto-generated from GrahpRag Database Inspection
"""

NODE_SCHEMA = {
    "FILE": [
        "hash",
        "language",
        "name",
        "package",
        "path",
        "project",
        "status"
    ],
    "TYPE": [
        "fullName",
        "name",
        "type"     
    ],
    "METHOD": [
        "args",
        "endpoint",
        "hash",
        "http_method",
        "last_scan_id",
        "name",
        "signature",
        "source",
        "status"
    ],
    "ExternalCall": [
        "name"
    ],
    "PARAMETER": [
        "name",
        "type",
        "methodSignature"
    ],
    "FIELD": [
        "name",
        "type",
        "classFullName"
    ],
    "RETURN_VALUE": [
        "type",
        "methodSignature"
    ]
}

RELATIONSHIP_SCHEMA = [
    # Format: StartLabel -> RelationshipType -> EndLabel
    "FILE -> CONTAINS -> TYPE",
    "TYPE -> CONTAINS -> METHOD",
    "TYPE -> HAS_FIELD -> FIELD",
    "METHOD -> HAS_RETURN -> RETURN_VALUE",
    "RETURN_VALUE -> OF_TYPE -> TYPE",
    "METHOD -> CALLS -> ExternalCall",
    "METHOD -> CALLS -> METHOD",
    "METHOD -> HAS_PARAMETER -> PARAMETER",
    "PARAMETER -> OF_TYPE -> TYPE"
]

class NodeLabel:
    """Dynamic Enum-like access for Node Labels"""
    FILE = "FILE"
    TYPE = "TYPE"
    METHOD = "METHOD"
    EXTERNAL_CALL = "ExternalCall"
    PARAMETER = "PARAMETER"
    FIELD = "FIELD"
    RETURN_VALUE = "RETURN_VALUE"

class EdgeType:
    """Dynamic Enum-like access for Edge Types"""
    CONTAINS = "CONTAINS"
    CALLS = "CALLS"
    HAS_PARAMETER = "HAS_PARAMETER"
    HAS_FIELD = "HAS_FIELD"
    HAS_RETURN = "HAS_RETURN"
    OF_TYPE = "OF_TYPE"
    RETURNS = "RETURNS"
