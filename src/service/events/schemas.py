from datetime import date

from src.service.schemas import BaseQuery, TeamOptionalQuery


class EventsQuery(BaseQuery, TeamOptionalQuery):
    start_date: date
    end_date: date
