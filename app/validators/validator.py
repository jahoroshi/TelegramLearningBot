from typing import Dict

from pydantic import BaseModel
from pydantic import ValidationError
import inspect



class StartConfigValidator(BaseModel):
    slug: str
    study_mode: str
    urls: Dict[str, str]
    buttons_to_show: Dict[str, bool]

    class Config:
        extra = 'allow'


class CardDataValidator(BaseModel):
    front_side: str
    back_side: str
    mappings_id: int
    ratings_count: dict

    class Config:
        extra = 'allow'

def card_data_isvalid(data):
    try:
        if isinstance(data, dict):
            CardDataValidator(**data)
        else:
            return False
    except ValidationError as e:
        caller_function_name = inspect.stack()[1].function
        print(f'Card data validation error in {caller_function_name}: {type(e)}')
        return False
    else:
        return True
