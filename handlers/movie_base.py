import os
from aiogram import Bot
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services import MovieBaseService
from services.logger import get_logger
from config import config


router = Router()
logger = get_logger(__name__)


# Состояния FSM для управления фильмами
class MovieStates(StatesGroup):
    browsing = State()
    confirming_deletion = State()

# Количество фильмов на странице
MOVIES_PER_PAGE = config.movies_on_list


@router.message(Command("movies"))
async def torrent_help_handler(message: Message, state: FSMContext, movie_service: MovieBaseService, bot: Bot):
    """Обработчик команды /movies - присылает все фильмы"""
    if message.from_user.id not in config.allowed_users:
        return
    
    movies = movie_service.get_all_movies()
    if not movies:
        await message.answer("Фильмы не найдены!")
        return

    # Сохраняем фильмы и настройки пагинации в FSM
    await state.update_data(
        movies=movies,
        current_page=0,
        total_pages=(len(movies) + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE,
        message_id=None
    )
    
    # Показываем первую страницу
    await show_movies_page(message.chat.id, state, bot)
    await state.set_state(MovieStates.browsing)


# Функция для отображения страницы с фильмами
async def show_movies_page(chat_id, state: FSMContext, bot: Bot):
    data = await state.get_data()
    movies = data['movies']
    current_page = data['current_page']
    total_pages = data['total_pages']
    message_id = data.get('message_id')
    
    # Вычисляем индексы для текущей страницы
    start_idx = current_page * MOVIES_PER_PAGE
    end_idx = min(start_idx + MOVIES_PER_PAGE, len(movies))
    
    # Создаем кнопки для фильмов текущей страницы
    movie_buttons = []
    for i in range(start_idx, end_idx):
        filename, path = movies[i]
        movie_buttons.append([InlineKeyboardButton(
            text=filename,
            callback_data=f"select_{i}"
        )])
    
    # Создаем кнопки навигации
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"page_{current_page - 1}"
        ))
    
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"page_{current_page + 1}"
        ))
    
    # Добавляем кнопки навигации в отдельный ряд
    if nav_buttons:
        movie_buttons.append(nav_buttons)
    
    # Добавляем кнопку отмены
    movie_buttons.append([InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel"
    )])
    
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=movie_buttons)
    
    # Текст сообщения
    text = f"Страница {current_page + 1} из {total_pages}\nВыберите фильм:"
    
    # Отправляем или редактируем сообщение
    if message_id:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=keyboard
        )
    else:
        msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard
        )
        await state.update_data(message_id=msg.message_id)

# Обработчик пагинации
@router.callback_query(F.data.startswith('page_'), MovieStates.browsing)
async def process_page(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    page = int(callback_query.data.split('_')[1])
    await state.update_data(current_page=page)
    await show_movies_page(callback_query.message.chat.id, state, bot)
    await callback_query.answer()

# Обработчик выбора фильма
@router.callback_query(F.data.startswith('select_'), MovieStates.browsing)
async def process_selection(callback_query: CallbackQuery, state: FSMContext):
    movie_idx = int(callback_query.data.split('_')[1])
    
    data = await state.get_data()
    movies = data['movies']
    selected_movie = movies[movie_idx]
    
    await state.update_data(
        selected_movie=selected_movie,
        selected_idx=movie_idx
    )
    
    # Переходим в состояние подтверждения удаления
    await state.set_state(MovieStates.confirming_deletion)
    
    # Создаем клавиатуру для подтверждения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Да, удалить",
                callback_data="confirm_delete"
            ),
            InlineKeyboardButton(
                text="❌ Нет, отменить",
                callback_data="cancel_delete"
            )
        ]
    ])
    
    # Редактируем сообщение
    await callback_query.message.edit_text(
        text=f"Вы уверены, что хотите удалить файл:\n{selected_movie[0]}?",
        reply_markup=keyboard
    )
    
    await callback_query.answer()

# Обработчик подтверждения удаления
@router.callback_query(F.data == 'confirm_delete', MovieStates.confirming_deletion)
async def process_confirm_delete(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_movie = data['selected_movie']
    movie_idx = data['selected_idx']
    movies = data['movies']
    
    # Удаляем файл
    try:
        os.remove(selected_movie[1])
        
        # Удаляем фильм из списка
        movies.pop(movie_idx)
        
        # Пересчитываем общее количество страниц
        total_movies = len(movies)
        total_pages = (total_movies + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE
        
        # Если текущая страница стала невалидной, переходим на предыдущую
        current_page = data['current_page']
        if current_page >= total_pages and total_pages > 0:
            current_page = total_pages - 1
        
        # Обновляем данные
        await state.update_data(
            movies=movies,
            current_page=current_page,
            total_pages=total_pages
        )
        
        # Возвращаемся в состояние просмотра
        await state.set_state(MovieStates.browsing)
        
        # Обновляем список фильмов
        if total_movies > 0:
            await show_movies_page(callback_query.message.chat.id, state, callback_query.bot)
            await callback_query.answer("Файл успешно удален!")
        else:
            # Если фильмов не осталось
            await callback_query.message.delete()
            await callback_query.message.answer("Файл удален. Больше фильмов не осталось.")
            await state.clear()
            
    except Exception as e:
        await callback_query.answer(f"Ошибка при удаления файла: {str(e)}", show_alert=True)
        await state.set_state(MovieStates.browsing)
        await show_movies_page(callback_query.message.chat.id, state, callback_query.bot)


# Обработчик отмены удаления
@router.callback_query(F.data == 'cancel_delete', MovieStates.confirming_deletion)
async def process_cancel_delete(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    # Возвращаемся к просмотру фильмов
    await state.set_state(MovieStates.browsing)
    await show_movies_page(callback_query.message.chat.id, state, bot)
    await callback_query.answer("Удаление отменено")

# Обработчик отмены всего
@router.callback_query(F.data == 'cancel', MovieStates.browsing)
@router.callback_query(F.data == 'cancel', MovieStates.confirming_deletion)
async def process_cancel(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await state.clear()
    await callback_query.answer("Операция отменена")