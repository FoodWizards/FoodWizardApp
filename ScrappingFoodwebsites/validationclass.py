from pydantic import ( 
    BaseModel,
    field_validator,
    ValidationError,
    ValidationInfo,
)
import re
import validators


class ContentClass(BaseModel):
    ID: str
    RecipeName: str 
    PrepTimeInMinutes : int | None
    CookTimeInMinutes: int | None
    TotalTimeInMinutes: int | None
    Servings : int | None
    Cuisine: str | None
    Ingredients : str | None
    Instructions : str | None
    Tags: str | None
    YouTubeLink : str| None
    Course: str | None
    Diet : str | None


    @field_validator('RecipeName')
    @classmethod
    def year_must_be_valid(cls, v: str) -> str:
        if not v:
            raise ValueError('RecipeName is not valid')
        return v

    TotalTimeInMinutes: int | None
    @field_validator('PrepTimeInMinutes', 'CookTimeInMinutes', 'TotalTimeInMinutes', 'Servings')
    @classmethod
    def text_should_not_contain_html_or_quotes(cls, v: int, info: ValidationInfo) -> int:
        if type(v) != int:
            raise ValueError(f'{info.field_name} contains invalid data which is not int')
        return v
    
   