from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProductResult:
    product_name: str
    store_name: str
    price: Optional[float]
    currency: str
    in_stock: bool
    rating: Optional[float]
    review_count: Optional[int]
    image_url: Optional[str]
    product_url: Optional[str]


class BaseProvider(ABC):
    """Abstract base class for all product data providers."""

    @abstractmethod
    def search(self, query: str) -> List[ProductResult]:
        """Search for products matching the query and return a list of results."""
        raise NotImplementedError
