import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from states import Form
from utils import Config, fuzzy_sort, make_keyboard, set_commands

config = Config()
logging.basicConfig(level=config.loglevel)

bot = Bot(token=config.bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands='brand', state=Form.NotInitialized)
async def brand_dialog(message: types.Message):
    await Form.Brand.set()
    await message.answer(f'Please enter desired brand name')


@dp.message_handler(commands='run', state=Form.Ready)
async def execute(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        brand = data['brand']
        await message.answer(f'Execute query with params:\nbrand: {brand}')
    await Form.NotInitialized.set()


@dp.message_handler(state=[Form.Brand, Form.Ready], regexp='[^0-9]{1,2}')
async def brand_suggest(message: types.Message, state: FSMContext):
    brand = message.text
    expected = fuzzy_sort(brand, config.brands)
    best_matched, score = expected[0]
    async with state.proxy() as data:
        if score == 100:
            data['brand'] = best_matched
            await Form.Ready.set()
            await message.reply('Brand selected')
            return
        else:
            data['expected'] = expected
    await Form.Brand.set()
    await message.answer('Brand not found. Select one of the follwoing or retype:\n' +
                         '\n'.join(f'{i + 1}. {name}' for i, (name, _) in enumerate(expected)),
                         reply_markup=make_keyboard(expected))


@dp.message_handler(state=Form.Brand, regexp='[1-9][0-9]*')
async def brand_selection(message: types.Message, state: FSMContext):
    i = int(message.text)
    async with state.proxy() as data:
        expected = data['expected']
        if i > len(expected):
            await message.reply(f'Incorrent id `{i}` of brand. Expected number between `1` and `{len(expected)}`')
        else:
            data['brand'] = expected[i - 1][0]
            await Form.Ready.set()
            await message.answer(f'Brand {data["brand"]} selected', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['start', 'reset'])
async def start(message: types.Message):
    await Form.NotInitialized.set()
    lines = ['Current flow consists of following steps:', 'Type /brand command', 'Type brand name',
             'Select one of suggested brands if not totally matched', 'Type /run command']  # yapf:disable
    await message.answer('\n'.join(lines))


@dp.message_handler()
async def unknown(message: types.Message):
    await message.reply(f'Sorry, not implemented yet')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)