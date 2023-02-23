import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from aiogram import Dispatcher, filters, types
from fuzzywuzzy import process


@dataclass
class Config:
    bot_token: str = field(init=False)
    contries: list[str] = field(default_factory=list)
    brands: list[str] = field(default_factory=list)
    loglevel: int = logging.INFO

    def __post_init__(self):
        data: dict = json.loads(Path('config.json').read_text())
        self.bot_token = data['bot_token']  # reuired
        self.contries = data.get('contries', ['ru', 'us', 'es', 'ge', 'jp'])
        self.brands = data.get('brands', ['suzuki', 'DNAnexus', 'Tchibo', 'Repsol', 'Rambler'])
        self.loglevel = getattr(logging, data.get('loglevel', 'INFO').upper())


async def set_commands(dispatcher: Dispatcher):
    await dispatcher.bot.set_my_commands([
        types.BotCommand('start', 'Initialize flow'),
        # types.BotCommand('country', 'Initizalize country selection dialog'),
        types.BotCommand('brand', 'Initizalize brand selection dialog'),
        types.BotCommand('run', 'Execute request with given fields'),
        types.BotCommand('reset', 'Reset fileds')])


def command_filter(*routes: str) -> filters.Filter:
    return filters.RegexpCommandsFilter(regexp_commands=routes)


def fuzzy_sort(input: str, variants: list[str], limit=16) -> list[tuple[str, int]]:
    return process.extract(input, variants, limit=min(limit, len(variants)))


def make_keyboard(variants: list[str], cols: int = 4) -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    rows_data = [list(range(i, min(len(variants), i + cols))) for i in range(0, len(variants), cols)]
    for row in rows_data:
        kb.row(*[types.KeyboardButton(i + 1) for i in row])
    return kb
