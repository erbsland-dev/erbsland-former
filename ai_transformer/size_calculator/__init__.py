#  Copyright © 2023-2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later


def register_extensions(manager):
    from .tokens import AiModelSizeCalculatorBase
    from ai_transformer.tools.model_manager import model_info_manager

    for model_info in model_info_manager.get_model_list():
        manager.add_extension_instance(AiModelSizeCalculatorBase(model_info))
