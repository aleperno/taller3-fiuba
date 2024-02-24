from pydantic import BaseModel, Json, validator, root_validator, Field, EmailStr, Extra
from typing import Optional, Any, Union, List
from enum import Enum
import re
import copy

from ..utils import file_manipulation as fm

TEMPLATE = {
    'file_name': 'aaa',
    'file_b64': 'bbb',
    'privacy': 'public',
    'convert_latex': False,
    'compress': False,
}

MAIL_REGEX = "^[a-zA-Z0-9_.-]+@([a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]+$"


class PrivacyEnum(str, Enum):
    private = 'private'
    public = 'public'
    restricted = 'restricted'


class UploadRequestSchema(BaseModel):
    shared_emails: Optional[List[EmailStr]] = []
    colours: Optional[int] = Field(ge=1, le=999, default=None)
    page_count: Optional[int] = 0
    white_background: Optional[bool] = False
    file_name: str = Field(..., min_length=1)
    file_b64: str
    compress: bool
    privacy: PrivacyEnum
    convert_latex: bool

    class Config:
        use_enum_values = True
        extra = Extra.forbid

    @validator('file_b64')
    def validate_is_pdf_file(cls, v, values):
        page_count = fm.validate_pdf_bytes(v)
        if not page_count:
            raise ValueError("Invalid PDF file")

        values['page_count'] = page_count

        return v

    @validator('shared_emails')
    def validate_valid_emails(cls, value):
        if any(not re.match(MAIL_REGEX, mail) for mail in value):
            raise ValueError("Found invalid email. Please check")
        return value

    @root_validator(pre=True)
    def aux(cls, values):
        #print(f"root validator: {values}")
        # Individual values were NOT validated yet
        # Validate properties based on 'privacy'
        if (values['privacy'] == 'restricted' and not values.get('shared_emails', [])):
            raise ValueError("Must define at least one shared emails with restricted privacy policy")
        if (values['privacy'] != 'restricted' and values.get('shared_emails')):
            raise ValueError("Shared Emails must only be defined with restricted privacy policy")
        # Validate properties based on 'compress'
        if (values['compress'] and any(prop not in values for prop in ('white_background', 'colours'))):
            raise ValueError("If compression is selected, also must be defined white_background and colours")
        return values
