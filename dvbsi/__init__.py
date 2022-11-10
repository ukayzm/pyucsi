__version__ = "0.3.0"

from .mpeg_section import *
from .mpeg_descriptor import *
from .dvb_section import *
from .dvb_table import *
from .dvb_descriptor import *
from .dvb_types import *
from .crc32 import *

SECTION_MAP = {
    STAG_PROGRAM_ASSOCIATION:                    PatSection,
    STAG_PROGRAM_MAP:                            PmtSection,
    STAG_NETWORK_INFORMATION_ACTUAL:             NitSection,
    STAG_NETWORK_INFORMATION_OTHER:              NitSection,
    STAG_SERVICE_DESCRIPTION_ACTUAL:             SdtSection,
    STAG_SERVICE_DESCRIPTION_OTHER:              SdtSection,
    STAG_BOUQUET_ASSOCIATION:                    BatSection,
    STAG_EVENT_INFORMATION_NOWNEXT_ACTUAL:       EitSection,
    STAG_EVENT_INFORMATION_NOWNEXT_OTHER:        EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL:      EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 1:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 2:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 3:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 4:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 5:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 6:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 7:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 8:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 9:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 10: EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 11: EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 12: EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 13: EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 14: EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_ACTUAL + 15: EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER:       EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 1:   EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 2:   EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 3:   EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 4:   EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 5:   EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 6:   EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 7:   EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 8:   EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 9:   EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 10:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 11:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 12:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 13:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 14:  EitSection,
    STAG_EVENT_INFORMATION_SCHEDULE_OTHER + 15:  EitSection,
    STAG_TIME_DATE:                              TdtSection,
    STAG_TIME_OFFSET:                            TotSection,
}

DESCRIPTOR_MAP = {
    DTAG_ISO_639_LANGUAGE:   Iso639LanguageDescriptor,
    DTAG_CA:                 CaDescriptor,
    DTAG_SERVICE_LIST:       ServiceListDescriptor,
    DTAG_SERVICE:            ServiceDescriptor,
    DTAG_SHORT_EVENT:        ShortEventDescriptor,
    DTAG_EXTENDED_EVENT:     ExtendedEventDescriptor,
    DTAG_STREAM_IDENTIFIER:  StreamIdentifierDescriptor,
    DTAG_SUBTITLING:         SubtitlingDescriptor,
    DTAG_MULTILINGUAL_SERVICE_NAME: MultilingualServiceNameDescriptor,
    DTAG_DATA_BROADCAST_ID:  DataBroadcastIdDescriptor,
    DTAG_DEFAULT_AUTHORITY:  DefaultAuthorityDescriptor,
    DTAG_COMPONENT:          ComponentDescriptor,
    DTAG_PRIVATE_DATA_SPECIFIER: PrivateDataSpecifierDescriptor,
    DTAG_CONTENT:            ContentDescriptor,
    DTAG_NETWORK_NAME:       NetworkNameDescriptor,
    DTAG_BOUQUET_NAME:       BouquetNameDescriptor,
    DTAG_PARENTAL_RATING:    ParentalRatingDescriptor,
    DTAG_DATA_BROADCAST:     DataBroadcastDescriptor,
    DTAG_SATELLITE_DELIVERY_SYSTEM: SatelliteDeliverySystemDescriptor,
    DTAG_TERRESTRIAL_DELIVERY_SYSTEM: TerrestrialDeliverySystemDescriptor,
    DTAG_CABLE_DELIVERY_SYSTEM: CableDeliverySystemDescriptor,
    DTAG_CONTENT_IDENTIFIER: ContentIdentifierDescriptor,
    DTAG_TELETEXT:           TeletextDescriptor,
    DTAG_LOCAL_TIME_OFFSET:  LocalTimeOffsetDescriptor,
}

