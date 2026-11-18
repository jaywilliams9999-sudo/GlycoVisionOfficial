from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

MIN_AGE, MAX_AGE = 18, 120  # both models were trained on adults only


def age_on(dob: date, today: date) -> int:
    """Whole years, minus one if this year's birthday hasn't come yet."""
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


class PatientCreate(BaseModel):
    identifier: str = Field(min_length=1, max_length=64)  # the MRN
    date_of_birth: date

    @field_validator("identifier", mode="before")
    @classmethod
    def strip_identifier(cls, v):
        # runs before min_length, so "   " becomes "" and is rejected
        return v.strip() if isinstance(v, str) else v

    @field_validator("date_of_birth")
    @classmethod
    def adult_birth_date(cls, dob: date) -> date:
        today = date.today()
        if dob > today:
            raise ValueError("Date of birth can't be in the future.")
        age = age_on(dob, today)
        if age < MIN_AGE:
            raise ValueError(f"These models are for patients {MIN_AGE} and older.")
        if age > MAX_AGE:
            raise ValueError("Check the date of birth.")
        return dob


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    identifier: str
    date_of_birth: date
    created_at: datetime