from typing import List, Literal
from pydantic import BaseModel, Field

Degree = Literal[1, 2, 3]

class Filter(BaseModel):
    degree: List[Degree] = Field(
        default_factory=lambda: [1, 2],
        description=(
            "Which network distances to include: 1 = people you know directly, "
            "2 = their connections, 3 = one step further out. "
            "Pick one or more numbers; default is 1 and 2."
        ),
    )

    connection_of: str | None = Field(
        None,
        description=(
            "Optional. When set, prefer people who are connected to this LinkedIn member. "
            "Use the name as it usually appears on their profile."
        ),
    )

    followers_of: str | None = Field(
        None,
        description=(
            "Optional. When set, prefer people who follow this LinkedIn member. "
            "Useful for audiences around a person or brand page."
        ),
    )
