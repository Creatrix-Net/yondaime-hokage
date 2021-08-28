from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .. import Session
    from ..types import SessionKey


sessions: Dict['SessionKey', Dict] = dict()
