from dataclasses import dataclass, asdict


@dataclass
class Product:
    card_link: str
    article: int
    name: str
    price: float | str
    description: str
    image_links: str
    specifications: str
    seller_name: str
    seller_link: str
    sizes: str
    quantity: int | str
    rating: float | str
    rating_count: int | str

    def to_dict(self):
        return asdict(self)
