from enum import StrEnum, auto


class PeriodEnum(StrEnum):
    mensal = auto()
    semanal = auto()
    hoje = auto()
    agenda = auto()


class EventExtractorEnum(StrEnum):
    open_event = auto()
    meetup = auto()
