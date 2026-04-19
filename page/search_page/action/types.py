from typing import List, Literal
from pydantic import BaseModel, Field

Degree = Literal[1, 2, 3]

class Filter(BaseModel):
    degree: List[Degree] = Field(
        default_factory=lambda: [1, 2],
        description="Connection degrees to include in LinkedIn search. "
                    "1 = first-degree (direct connections), "
                    "2 = second-degree (connections of your connections), "
                    "3 = third-degree (extended network). "
                    "Provide one or more values to control reach."
    )
    
    connection_of: str | None = Field(
        None,
        description="Full name of a LinkedIn user. "
                    "Restricts results to people who are connected to this person. "
                    "Use exact or close-match name as shown on LinkedIn."
    )
    
    followers_of: str | None = Field(
        None,
        description="Full name of a LinkedIn user. "
                    "Restricts results to people who follow this person. "
                    "Useful for targeting audience of a specific influencer or company leader."
    )