#app/features/customer/castprof/schemas/image_schema.py

from pydantic import BaseModel

class ImageData(BaseModel):
    url: str
    order_index: int
