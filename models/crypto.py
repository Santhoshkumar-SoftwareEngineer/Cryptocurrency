"""
Data models for Cryptocurrency Price Tracker.
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class CryptoCoin:
    """
    Represents a single cryptocurrency market snapshot.
    """
    rank: int
    name: str
    symbol: str
    price: Optional[float]
    change_24h: Optional[float]
    market_cap: Optional[float]
    volume_24h: Optional[float]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert the dataclass instance to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CryptoCoin":
        """Create a CryptoCoin instance from a dictionary."""
        return cls(
            rank=int(data["rank"]),
            name=str(data["name"]),
            symbol=str(data["symbol"]),
            price=float(data["price"]) if data.get("price") is not None and str(data["price"]).strip() != "" and str(data["price"]).lower() != "nan" else None,
            change_24h=float(data["change_24h"]) if data.get("change_24h") is not None and str(data["change_24h"]).strip() != "" and str(data["change_24h"]).lower() != "nan" else None,
            market_cap=float(data["market_cap"]) if data.get("market_cap") is not None and str(data["market_cap"]).strip() != "" and str(data["market_cap"]).lower() != "nan" else None,
            volume_24h=float(data["volume_24h"]) if data.get("volume_24h") is not None and str(data["volume_24h"]).strip() != "" and str(data["volume_24h"]).lower() != "nan" else None,
            timestamp=str(data["timestamp"]),
        )
