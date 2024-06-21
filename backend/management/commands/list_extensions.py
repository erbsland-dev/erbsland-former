#  Copyright © 2024 Tobias Erbsland https://erbsland.dev/ and EducateIT GmbH https://educateit.ch/
#  According to the copyright terms specified in the file "COPYRIGHT.md".
#  SPDX-License-Identifier: GPL-3.0-or-later
import argparse

from django.core.management import BaseCommand

from backend.size_calculator.manager import size_calculator_manager
from backend.syntax_handler import syntax_manager
from backend.transformer.manager import transformer_manager


class Command(BaseCommand):
    help = f"""Lists all installed extensions that are configured for this app."""

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def handle(self, *args, **options):
        lines = ["Syntax Handlers:"]
        for extension in syntax_manager.extension_list:
            lines.append(f"  - {extension.name} ('{extension.verbose_name}')")
        lines.append("")
        lines.append("Size Calculators:")
        for extension_name in size_calculator_manager.extension_names:
            lines.append(
                f"  - {extension_name} ('{size_calculator_manager.verbose_name(extension_name)}') "
                f"Unit: {size_calculator_manager.get_unit_name(extension_name)}"
            )
        lines.append("")
        lines.append("Transformer:")
        for extension_name in transformer_manager.extension_names:
            lines.append(f"  - {extension_name} ('{transformer_manager.verbose_name(extension_name)}')")
        return "\n".join(lines)
