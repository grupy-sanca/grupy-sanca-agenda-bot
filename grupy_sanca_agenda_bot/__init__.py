from grupy_sanca_agenda_bot.constants import EventExtractorEnum
from grupy_sanca_agenda_bot.settings import settings

if settings.EVENT_EXTRACTOR == EventExtractorEnum.open_event:
    from grupy_sanca_agenda_bot.events import OpenEventExtractor as EventExtractor
elif settings.EVENT_EXTRACTOR == EventExtractorEnum.meetup:
    from grupy_sanca_agenda_bot.events import MeetupEventExtractor as EventExtractor

event_extractor = EventExtractor(settings.URL)
