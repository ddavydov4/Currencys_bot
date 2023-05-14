import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
import os


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot_token = os.getenv('TELEGRAM_TOKEN_BOT')
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    name = State()
    rate = State()
    num = State()
    check = State()


dictionary = {}


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Доброго времени суток! Введите /save_currency,чтобы сохранить валюту, или /convert, чтобы ее конвертировать, а также /cancel, чтобы отменить все действия")


@dp.message_handler(commands=['save_currency'])
async def save_command(message: types.Message):
    await Form.name.set()
    await message.answer("Введите название валюты")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Действия отменены')


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message. answer('Введите курс "' + message.text + '" по отношению к российскому Рублю: ')
    await Form.rate.set()


@dp.message_handler(state=Form.rate)
async def process_course(message: types.Message, state: FSMContext):
    course = message.text
    name = await state.get_data()
    name_dictionary = name['name']
    dictionary[name_dictionary] = course
    await state.finish()


@dp.message_handler(commands=['convert'])
async def convert_command(message: types.Message):
    await Form.check.set()
    await message. answer("Введите название, вписанной ранее валюты")


@dp.message_handler(state=Form.check)
async def process_check(message: types.Message, state: FSMContext):
    await state.update_data(check_course=message.text)
    await message.answer("Введите сумму, которую вы хотите перевести в рубли(RUB)")
    await Form.num.set()


@dp.message_handler(state=Form.num)
async def process_convert(message: types.Message, state: FSMContext):
    num = message.text
    check_course = await state.get_data()
    name_dictionary = check_course['check_course']
    result = int(dictionary[name_dictionary]) * int(num)
    await message.reply(result)
    await state.finish()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)