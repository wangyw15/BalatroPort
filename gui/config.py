from qfluentwidgets import (
    OptionsConfigItem,
    OptionsValidator,
    QConfig,
)

from libs import love2d_helper


class Config(QConfig):
    outputType = OptionsConfigItem(
        "Patcher",
        "OutputType",
        love2d_helper.VALID_OUTPUT_TYPES[0],
        OptionsValidator(love2d_helper.VALID_OUTPUT_TYPES),
        restart=True,
    )
