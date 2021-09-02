from dataclasses import dataclass
from typing import List


@dataclass
class Recipient:
    amount: str
    address: str


@dataclass
class Wallet:
    public_key: str
    keys: List[str]
    encrypted_private_key: str = ""
