from __future__ import annotations


class Badge:
    """A class to handle all the badge commands"""

    def __init__(
        self,
        badge_name: str,
        code: str,
        image: str = None,
        watermark: str = None,
        file_name: str = None,
        is_inverted: bool = False,
    ):
        super().__init__()
        self.badge_name = badge_name
        self.code = code
        self.file_name = file_name
        self.is_inverted = is_inverted
        self.image = image
        self.watermark = watermark

    def to_json(self) -> dict:
        """Converts the class to :class:`json`

        :return: Data in the json format
        :rtype: dict
        """
        return {
            "badge_name": self.badge_name,
            "code": self.code,
            "image": self.image,
            "watermark": self.watermark,
            "file_name": self.file_name,
            "is_inverted": self.is_inverted,
        }

    @classmethod
    async def from_json(cls, data: dict):
        """generates badge from `json` or :class:`dict`

        :param data: The data in :class:`dict` form
        :type data: dict
        :return: The :class:`~Badge` with the data provided
        :rtype: Badge
        """
        badge_name = data["badge_name"]
        code = data["code"]
        is_inverted = data["is_inverted"]
        if "file_name" in data:
            file_name = data["file_name"]
        else:
            file_name = None

        if "image" in data:
            image = data["image"]
        else:
            image = None
        if "watermark" in data:
            watermark = data["watermark"]
        else:
            watermark = None
        return cls(badge_name, code, image, watermark, file_name, is_inverted)
