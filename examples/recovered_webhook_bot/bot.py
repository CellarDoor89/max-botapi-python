import asyncio
import html
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from maxapi import Bot, Dispatcher
from maxapi.enums.chat_type import ChatType
from maxapi.enums.message_link_type import MessageLinkType
from maxapi.enums.parse_mode import ParseMode
from maxapi.types import (
    BotStarted,
    CallbackButton,
    Command,
    CommandStart,
    InputMedia,
    LinkButton,
    MessageCallback,
    MessageCreated,
)
from maxapi.types.attachments.buttons.attachment_button import AttachmentButton
from maxapi.types.message import NewMessageLink
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from middlewares.accept_policy import POLICY_TEXT, POLICY_URL
from sections import (
    addresses,
    calendar,
    debts,
    ens_help,
    faq,
    feedback,
    ifns_details,
    mfc,
    payments,
    phones,
    white_check,
)

# Эти импорты используются в полном проекте. В восстановленном каркасе они
# намеренно оставлены, чтобы верх старого bot.py совпадал с вашей версией.
_ = (
    html,
    ChatType,
    MessageLinkType,
    ParseMode,
    BotStarted,
    CallbackButton,
    Command,
    CommandStart,
    InputMedia,
    LinkButton,
    MessageCallback,
    MessageCreated,
    AttachmentButton,
    NewMessageLink,
    InlineKeyboardBuilder,
    POLICY_TEXT,
    POLICY_URL,
    addresses,
    calendar,
    ifns_details,
    mfc,
    payments,
    phones,
)

logger = logging.getLogger('max_bot')
logger.setLevel(logging.INFO)

ACCEPT_PAYLOAD = 'accept_policy'
MENU_PAYLOAD = 'open_menu'
ADDRESSES_MENU_PAYLOAD = 'open_addresses'
IFNS_DETAILS_MENU_PAYLOAD = 'open_ifns_details'
ENS_HELP_MENU_PAYLOAD = 'open_ens_help'
MFC_MENU_PAYLOAD = 'open_mfc'
MFC_PAGE_PREFIX = 'mfc_page:'
MFC_ITEM_PREFIX = 'mfc_item:'
MENU_SECTION_PREFIX = 'menu_section:'
PAYMENTS_MENU_PAYLOAD = 'open_payments'
PAYMENTS_PAYER_PREFIX = 'payments_payer:'
PAYMENTS_ITEM_PREFIX = 'payments_item:'
CALENDAR_MENU_PAYLOAD = 'open_calendar'
CALENDAR_NEAR_PAYLOAD = 'calendar_near'
CALENDAR_ALL_PAYLOAD = 'calendar_all'
CALENDAR_QUARTER_PREFIX = 'calendar_quarter:'
CALENDAR_MONTH_PREFIX = 'calendar_month:'
CALENDAR_MONTH_ALL_PREFIX = 'calendar_month_all:'
CALENDAR_DAY_PREFIX = 'calendar_day:'
PHONES_MENU_PAYLOAD = 'open_phones'
PHONES_TOPIC_PREFIX = 'phones_topic:'
DEBT_MENU_PAYLOAD = debts.DEBT_MENU_PAYLOAD
DEBT_PAYER_PREFIX = debts.DEBT_PAYER_PREFIX
DEBT_ITEM_PREFIX = debts.DEBT_ITEM_PREFIX
DEBT_EXTRA_PREFIX = debts.DEBT_EXTRA_PREFIX
FEEDBACK_START_PAYLOAD = feedback.FEEDBACK_START_PAYLOAD
FEEDBACK_PHONE_PAYLOAD = feedback.FEEDBACK_PHONE_PAYLOAD
FEEDBACK_SEND_PAYLOAD = feedback.FEEDBACK_SEND_PAYLOAD
FEEDBACK_SUMMARY_PAYLOAD = feedback.FEEDBACK_SUMMARY_PAYLOAD
FEEDBACK_ADMIN_TAKE_PAYLOAD = feedback.FEEDBACK_ADMIN_TAKE_PAYLOAD
FEEDBACK_ADMIN_DONE_PAYLOAD = feedback.FEEDBACK_ADMIN_DONE_PAYLOAD
FEEDBACK_ADMIN_RESET_PAYLOAD = feedback.FEEDBACK_ADMIN_RESET_PAYLOAD
FEEDBACK_ADMIN_REROUTE_PAYLOAD = feedback.FEEDBACK_ADMIN_REROUTE_PAYLOAD
FEEDBACK_EDIT_MENU_PAYLOAD = feedback.FEEDBACK_EDIT_MENU_PAYLOAD
FEEDBACK_EDIT_NAME_PAYLOAD = feedback.FEEDBACK_EDIT_NAME_PAYLOAD
FEEDBACK_EDIT_INN_PAYLOAD = feedback.FEEDBACK_EDIT_INN_PAYLOAD
FEEDBACK_EDIT_PHONE_PAYLOAD = feedback.FEEDBACK_EDIT_PHONE_PAYLOAD
FEEDBACK_EDIT_QUESTION_PAYLOAD = feedback.FEEDBACK_EDIT_QUESTION_PAYLOAD
FEEDBACK_CONTACT_CALL_PAYLOAD = feedback.FEEDBACK_CONTACT_CALL_PAYLOAD
FEEDBACK_CONTACT_MAX_PAYLOAD = feedback.FEEDBACK_CONTACT_MAX_PAYLOAD
FEEDBACK_TOPIC_PREFIX = feedback.FEEDBACK_TOPIC_PREFIX
ADDRESS_PAYLOAD_PREFIX = 'address:'
WHITE_CHECK_INFO_PAYLOAD = white_check.WHITE_CHECK_INFO_PAYLOAD
WHITE_CHECK_SUBMIT_PAYLOAD = white_check.WHITE_CHECK_SUBMIT_PAYLOAD
WHITE_CHECK_MENU_PAYLOAD = white_check.WHITE_CHECK_MENU_PAYLOAD
WHITE_CHECK_CHECK_RECEIPT_PAYLOAD = white_check.WHITE_CHECK_CHECK_RECEIPT_PAYLOAD
WHITE_CHECK_CHECK_RECEIPT_APPS_PAYLOAD = white_check.WHITE_CHECK_CHECK_RECEIPT_APPS_PAYLOAD
WHITE_CHECK_MY_RECEIPTS_PAYLOAD = white_check.WHITE_CHECK_MY_RECEIPTS_PAYLOAD
WHITE_CHECK_MY_RECEIPTS_APPS_PAYLOAD = white_check.WHITE_CHECK_MY_RECEIPTS_APPS_PAYLOAD
WHITE_CHECK_CITY_PREFIX = white_check.WHITE_CHECK_CITY_PREFIX
WHITE_CHECK_OTHER_CITY = white_check.WHITE_CHECK_OTHER_CITY
WHITE_CHECK_ADMIN_TAKE_PAYLOAD = white_check.WHITE_CHECK_ADMIN_TAKE_PAYLOAD
WHITE_CHECK_ADMIN_DONE_PAYLOAD = white_check.WHITE_CHECK_ADMIN_DONE_PAYLOAD
WHITE_CHECK_ADMIN_RESET_PAYLOAD = white_check.WHITE_CHECK_ADMIN_RESET_PAYLOAD
WHITE_CHECK_ADMIN_VIOLATION_PAYLOAD = 'white_check_admin_violation'
WHITE_CHECK_ADMIN_NO_VIOLATION_PAYLOAD = 'white_check_admin_no_violation'
WHITE_CHECK_ADMIN_OTHER_PAYLOAD = 'white_check_admin_other'
WHITE_CHECK_ADMIN_OTHER_CONFIRM_PAYLOAD = 'white_check_admin_other_confirm'
WHITE_CHECK_ADMIN_OTHER_CANCEL_PAYLOAD = 'white_check_admin_other_cancel'
WHITE_CHECK_SUMMARY_PAYLOAD = white_check.WHITE_CHECK_SUMMARY_PAYLOAD
WHITE_CHECK_EDIT_MENU_PAYLOAD = white_check.WHITE_CHECK_EDIT_MENU_PAYLOAD
WHITE_CHECK_EDIT_CITY_PAYLOAD = white_check.WHITE_CHECK_EDIT_CITY_PAYLOAD
WHITE_CHECK_EDIT_DETAILS_PAYLOAD = white_check.WHITE_CHECK_EDIT_DETAILS_PAYLOAD
WHITE_CHECK_EDIT_ATTACHMENTS_PAYLOAD = white_check.WHITE_CHECK_EDIT_ATTACHMENTS_PAYLOAD
WHITE_CHECK_SEND_PAYLOAD = white_check.WHITE_CHECK_SEND_PAYLOAD
BROADCAST_CONFIRM_PAYLOAD = 'broadcast_confirm'
BROADCAST_CANCEL_PAYLOAD = 'broadcast_cancel'
FEEDBACK_RATE_PREFIX = 'feedback_rate:'
FEEDBACK_ASSIGN_PREFIX = 'feedback_assign:'
FEEDBACK_ASSIGN_PAGE_PREFIX = 'feedback_assign_page:'
POLICY_NOTICE = (
    'ВНИМАНИЕ \n\n'
    'Некоторые режимы чат-бота требуют ввода персональных данных. \n'
    'Эти данные могут быть переданы Федеральной налоговой службе (ФНС России), территориальным налоговым органам, '
    'на обработку, в том числе автоматизированную, своих персональных данных в соответствии с Федеральным законом '
    'от 27.07.2006 № 152-ФЗ «О персональных данных». \n'
    'Под обработкой персональных данных в указанном законе понимаются действия (операции) с персональными данными, '
    'включая сбор, запись, систематизацию, накопление, хранение, уточнение (обновление, изменение), извлечение, '
    'использование, передачу (распространение, предоставление, доступ), обезличивание, блокирование, удаление, '
    'уничтожение персональных данных. \n'
    'Даю свое согласие на обработку персональных данных и разрешаю проверку достоверности предоставленных мной '
    'персональных данных, в том числе с использованием услуг иного лица на основании заключаемого с этим лицом '
    'договора, в том числе государственного контракта, либо путем принятия соответствующего акта. \n'
    'Гарантирую, что представленная мной информация является полной, точной и достоверной, а также что при '
    'представлении информации не нарушаются действующее законодательство Российской Федерации, законные права и '
    'интересы третьих лиц. Вся представленная информация заполнена мною в отношении себя лично. \n'
    'Настоящее согласие действует в течение всего периода хранения персональных данных, если иное не предусмотрено '
    'законодательством Российской Федерации.\n'
)

DATA_DIR = Path(__file__).resolve().parent / 'data'
STORAGE_FILE = DATA_DIR / 'accepted_users.json'
FEEDBACK_STATE_FILE = DATA_DIR / 'feedback_state.json'
INSPECTORS_FILE = DATA_DIR / 'inspectors.json'
USAGE_STATS_FILE = DATA_DIR / 'usage_stats.json'
STAFF_CATALOG_FILE = DATA_DIR / 'staff_catalog.json'
STAFF_BINDINGS_FILE = DATA_DIR / 'staff_bindings.json'
LOG_DIR = Path(__file__).resolve().parent / 'logs'
ASSETS_DIR = Path(__file__).resolve().parent / 'assets'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILENAME = f"bot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
LOG_FILE_PATH = LOG_DIR / LOG_FILENAME

MAIN_MENU_TEXT = 'Главное меню. Выберите раздел:'
CALENDAR_INTRO_TEXT = (
    '"Календарь бухгалтера" рассчитан на юридических лиц, физических лиц, индивидуальных предпринимателей.\n'
    'В нем содержится важнейшая и широко применяемая информация о сроках уплаты и представления деклараций, '
    'отчетов и сведений по налогам, сборам и платежам, установленным федеральным законодательством, '
    'имеющим регулярный и однотипный характер.\n\n'
    'Сроки представления деклараций, сведений, отчетов, уплаты региональных и местных налогов и сборов, '
    'установленные региональными и местными законодательными органами либо установленные исключительно в '
    'отношении органов государственной власти или органов местного самоуправления, а также сроки представления '
    'форм статистической отчетности в "Календаре бухгалтера" не указываются.'
)

FEEDBACK_TOPICS = [
    'НДС',
    'Регистрация',
    'ПСН',
    'УСН',
    '3-НДФЛ',
    '2-НДФЛ',
    'Задолженность',
    'Прочее',
]
MFC_PAGE_SIZE = 8

MENU_SECTIONS = {
    'addresses': 'Подразделения ФНС ЯНАО',
    'ifns_details': 'Определение реквизитов ИФНС',
    'mfc': 'Подразделения МФЦ ЯНАО',
    'ens_help': ens_help.TITLE,
    'debt': 'Узнать свою задолженность',
    'payments': 'Уплата налогов и пошлин',
    'feedback': 'Обратная связь',
    'white_check': 'Проблемы с чеком',
    'phones': 'Телефоны для связи',
    'faq': faq.TITLE,
    'service': 'Служебное',
    'policy': 'Политика обработки данных',
}

SERVICE_MENU_PAYLOAD = 'service_menu'
SERVICE_DEPT_PREFIX = 'service_dept:'
SERVICE_EMP_PREFIX = 'service_emp:'
SERVICE_STAFF_PAGE_PREFIX = 'service_staff_page:'
STAFF_PAGE_SIZE = 6

ADMIN_STAFF_BY_ID: dict[int, str] = {}

ADDRESS_IMAGE_PATHS = {
    'Главный офис': ASSETS_DIR / 'fns-main-office.png',
    'ОП № 1 в г. Салехард': ASSETS_DIR / 'fns-office-1-salekhard.png',
    'ОП № 2 в г. Лабытнанги': ASSETS_DIR / 'fns-office-2-labytnangi.png',
    'ОП № 3 в г. Салехард': ASSETS_DIR / 'fns-office-3-salekhard.png',
    'ОП № 4 в г. Новый Уренгой': ASSETS_DIR / 'fns-office-4-new-urengoy.png',
    'ОП № 5 в г. Тарко-Сале': ASSETS_DIR / 'fns-office-5-tarko-sale.png',
    'ОП № 6 в г. Губкинский': ASSETS_DIR / 'fns-office-6-gubkinsky.png',
    'ОП № 7 в г. Надым': ASSETS_DIR / 'fns-office-7-nadym.png',
    'ОП № 8 в г. Ноябрьск': ASSETS_DIR / 'fns-office-8-noyabrsk.png',
    'ОП № 9 в г. Муравленко': ASSETS_DIR / 'fns-office-9-muravlenko.png',
}
REPORT_TIMEZONE = ZoneInfo('Asia/Yekaterinburg')
REPORT_HOUR_LOCAL = 9
WHITE_CHECK_INFO_IMAGE_PATH = ASSETS_DIR / 'white-check-info.png'


class AcceptanceStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = {'users': {}}
        self._ensure_storage()
        self._load()

    def _ensure_storage(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save()

    def _load(self) -> None:
        with self.path.open('r', encoding='utf-8') as handle:
            self.data = json.load(handle)

    def _save(self) -> None:
        with self.path.open('w', encoding='utf-8') as handle:
            json.dump(self.data, handle, ensure_ascii=False, indent=2)

    def _ensure_user(self, user_id: int) -> dict:
        users = self.data.setdefault('users', {})
        key = str(user_id)
        if key not in users:
            users[key] = {
                'accepted': False,
                'accepted_at': None,
                'last_interaction_at': None,
                'interaction_count': 0,
            }
        return users[key]

    def record_interaction(self, user_id: int) -> None:
        user = self._ensure_user(user_id)
        user['last_interaction_at'] = self._now()
        user['interaction_count'] += 1
        self._save()

    def is_accepted(self, user_id: int) -> bool:
        user = self._ensure_user(user_id)
        return bool(user['accepted'])

    def accept(self, user_id: int) -> None:
        user = self._ensure_user(user_id)
        user['accepted'] = True
        user['accepted_at'] = self._now()
        self._save()

    def all_user_ids(self) -> list[int]:
        users = self.data.get('users', {})
        result: list[int] = []
        for key in users.keys():
            try:
                result.append(int(key))
            except (TypeError, ValueError):
                continue
        return result

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()


store = AcceptanceStore(STORAGE_FILE)

BOT_TOKEN = os.environ['MAX_BOT_TOKEN']
ADMIN_USER_ID = int(os.getenv('MAX_ADMIN_USER_ID', '16439444'))
ADMIN_CHAT_ID = int(os.getenv('MAX_ADMIN_CHAT_ID', '-70804898799764'))
WHITE_CHECK_CHAT_ID = int(os.getenv('MAX_WHITE_CHECK_CHAT_ID', '-70809030254740'))
WEBHOOK_URL = os.getenv('MAX_WEBHOOK_URL')
WEBHOOK_HOST = os.getenv('MAX_WEBHOOK_HOST', '0.0.0.0')
WEBHOOK_PORT = int(os.getenv('MAX_WEBHOOK_PORT', '8080'))

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dataclass
class FeedbackSession:
    step: str
    topic: str | None = None
    name: str | None = None
    inn: str | None = None
    question: str | None = None
    question_attachments: list = field(default_factory=list)
    phone: str | None = None
    contact_method: str | None = None
    content_message_id: str | None = None


feedback_sessions: dict[int, FeedbackSession] = {}
feedback_admin_messages: dict[str, str] = {}


@dataclass
class FeedbackTicket:
    user_id: int
    topic: str
    created_at: datetime
    question_preview: str = ''
    status: str = 'new'
    assigned_to: str = 'Администратор'
    taken_at: datetime | None = None
    closed_at: datetime | None = None
    rating: int | None = None
    reminded: bool = False
    manager_user_id: int | None = None
    manager_message_id: str | None = None
    executor_user_id: int | None = None
    executor_message_id: str | None = None


feedback_tickets: dict[str, FeedbackTicket] = {}
feedback_ticket_by_message: dict[str, str] = {}
feedback_stats_daily: dict[str, dict[str, int]] = {}
last_daily_report_date: date | None = None
feedback_stats_requests: dict[int, str] = {}


@dataclass
class WhiteCheckSession:
    step: str
    city: str | None = None
    details: str | None = None
    attachments: list = field(default_factory=list)
    content_message_id: str | None = None


@dataclass
class WhiteCheckTicket:
    user_id: int
    assigned_to: str | None = None
    processed_by: str | None = None


white_check_sessions: dict[int, WhiteCheckSession] = {}
white_check_admin_messages: dict[str, str] = {}
white_check_tickets: dict[str, WhiteCheckTicket] = {}
white_check_other_comment_drafts: dict[int, dict[str, str]] = {}
broadcast_drafts: dict[int, str] = {}
usage_stats_requests: dict[int, str] = {}
usage_stats: dict[str, dict] = {'daily': {}}
staff_catalog: dict[str, list[str]] = {}
staff_bindings: dict[str, dict[str, str | int]] = {}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        if record.exc_info:
            payload['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)



def setup_json_logging() -> None:
    """Подключает JSON-лог в файл и обычный лог в консоль."""

    if logger.handlers:
        return

    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
    file_handler.setFormatter(JsonFormatter())
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def load_json(path: Path, default):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        save_json(path, default)
        return default.copy() if isinstance(default, dict) else default

    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def load_runtime_state() -> None:
    """Загружает JSON-состояние, которое раньше жило во внутренней части bot.py."""

    global usage_stats, staff_catalog, staff_bindings

    usage_stats = load_json(USAGE_STATS_FILE, {'daily': {}})
    staff_catalog = load_json(STAFF_CATALOG_FILE, {})
    staff_bindings = load_json(STAFF_BINDINGS_FILE, {})


def user_id_from_event(event: MessageCreated | MessageCallback) -> int:
    if isinstance(event, MessageCallback):
        return event.callback.user.user_id
    return event.message.sender.user_id


def chat_id_from_event(event: MessageCreated | MessageCallback) -> int | None:
    return event.message.recipient.chat_id


def today_key() -> str:
    return datetime.now(REPORT_TIMEZONE).date().isoformat()


def record_usage(user_id: int, action: str) -> None:
    day = today_key()
    daily = usage_stats.setdefault('daily', {})
    stat = daily.setdefault(day, {'users': [], 'actions': {}})

    users = stat.setdefault('users', [])
    if user_id not in users:
        users.append(user_id)

    actions = stat.setdefault('actions', {})
    actions[action] = actions.get(action, 0) + 1
    save_json(USAGE_STATS_FILE, usage_stats)


def button(text: str, payload: str) -> CallbackButton:
    return CallbackButton(text=text, payload=payload)


def link_button(text: str, url: str) -> LinkButton:
    return LinkButton(text=text, url=url)


def keyboard_from_rows(rows: list[list[CallbackButton | LinkButton]]) -> AttachmentButton:
    builder = InlineKeyboardBuilder()
    for row in rows:
        builder.row(*row)
    return builder.as_markup()


def main_menu_keyboard() -> AttachmentButton:
    return keyboard_from_rows([
        [button('Подразделения ФНС ЯНАО', ADDRESSES_MENU_PAYLOAD)],
        [button('Реквизиты ИФНС', IFNS_DETAILS_MENU_PAYLOAD)],
        [button('Подразделения МФЦ ЯНАО', MFC_MENU_PAYLOAD)],
        [button(ens_help.TITLE, ENS_HELP_MENU_PAYLOAD)],
        [button('Задолженность', DEBT_MENU_PAYLOAD)],
        [button('Уплата налогов и пошлин', PAYMENTS_MENU_PAYLOAD)],
        [button('Обратная связь', FEEDBACK_START_PAYLOAD)],
        [button('Проблемы с чеком', WHITE_CHECK_MENU_PAYLOAD)],
        [button('Телефоны для связи', PHONES_MENU_PAYLOAD)],
        [button(faq.TITLE, f'{MENU_SECTION_PREFIX}faq')],
        [button('Политика обработки данных', f'{MENU_SECTION_PREFIX}policy')],
    ])


def back_to_menu_keyboard() -> AttachmentButton:
    return keyboard_from_rows([[button('⬅️ Главное меню', MENU_PAYLOAD)]])


def policy_keyboard() -> AttachmentButton:
    rows: list[list[CallbackButton | LinkButton]] = [
        [button('✅ Даю согласие', ACCEPT_PAYLOAD)],
        [button('⬅️ Главное меню', MENU_PAYLOAD)],
    ]
    if POLICY_URL:
        rows.insert(1, [link_button('Открыть политику', POLICY_URL)])
    return keyboard_from_rows(rows)


def section_keyboard(section: str) -> AttachmentButton:
    return keyboard_from_rows([
        [button('Открыть раздел', f'{MENU_SECTION_PREFIX}{section}')],
        [button('⬅️ Главное меню', MENU_PAYLOAD)],
    ])


def section_text(payload: str) -> tuple[str, str]:
    mapping = {
        ADDRESSES_MENU_PAYLOAD: ('addresses', 'Подразделения ФНС ЯНАО'),
        IFNS_DETAILS_MENU_PAYLOAD: ('ifns_details', 'Определение реквизитов ИФНС'),
        ENS_HELP_MENU_PAYLOAD: ('ens_help', ens_help.TITLE),
        MFC_MENU_PAYLOAD: ('mfc', 'Подразделения МФЦ ЯНАО'),
        DEBT_MENU_PAYLOAD: ('debt', 'Узнать свою задолженность'),
        PAYMENTS_MENU_PAYLOAD: ('payments', 'Уплата налогов и пошлин'),
        PHONES_MENU_PAYLOAD: ('phones', 'Телефоны для связи'),
        WHITE_CHECK_MENU_PAYLOAD: ('white_check', 'Проблемы с чеком'),
        FEEDBACK_START_PAYLOAD: ('feedback', 'Обратная связь'),
    }
    section, title = mapping.get(payload, (payload.removeprefix(MENU_SECTION_PREFIX), 'Раздел'))

    details = {
        'addresses': 'Здесь можно разместить адреса подразделений ФНС ЯНАО и кнопки по офисам.',
        'ifns_details': 'Здесь можно восстановить сценарий определения реквизитов ИФНС.',
        'ens_help': 'Здесь можно восстановить подсказки по Единому налоговому счёту.',
        'mfc': 'Здесь можно восстановить список подразделений МФЦ с постраничной навигацией.',
        'debt': 'Здесь можно восстановить сценарий проверки задолженности.',
        'payments': 'Здесь можно восстановить раздел уплаты налогов и пошлин.',
        'feedback': 'Здесь можно восстановить сценарий обратной связи и создания обращения.',
        'white_check': 'Здесь можно восстановить сценарий сообщения о проблеме с чеком.',
        'phones': 'Здесь можно восстановить телефоны для связи по темам.',
        'faq': 'Здесь можно восстановить частые вопросы и ответы.',
        'policy': POLICY_NOTICE,
    }
    return section, f'{title}\n\n{details.get(section, "Раздел восстановлен как точка входа для дальнейшего наполнения.")}'


async def send_main_menu(event: MessageCreated | MessageCallback, text: str = MAIN_MENU_TEXT) -> None:
    user_id = user_id_from_event(event)
    store.record_interaction(user_id)
    record_usage(user_id, 'main_menu')
    await event.message.answer(text=text, attachments=[main_menu_keyboard()])


async def send_policy(event: MessageCreated | MessageCallback) -> None:
    user_id = user_id_from_event(event)
    store.record_interaction(user_id)
    record_usage(user_id, 'policy')
    await event.message.answer(text=POLICY_NOTICE, attachments=[policy_keyboard()])


async def send_section(event: MessageCreated | MessageCallback, payload: str) -> None:
    user_id = user_id_from_event(event)
    store.record_interaction(user_id)
    record_usage(user_id, payload)
    section, text = section_text(payload)
    await event.message.answer(text=text, attachments=[section_keyboard(section)])


@dp.bot_started()
async def handle_bot_started(event: BotStarted):
    if event.chat_id is not None:
        await event.bot.send_message(
            chat_id=event.chat_id,
            text='Здравствуйте! Перед началом работы подтвердите согласие на обработку персональных данных.',
            attachments=[policy_keyboard()],
        )


@dp.message_created(CommandStart())
async def handle_start(event: MessageCreated):
    user_id = event.message.sender.user_id
    store.record_interaction(user_id)
    record_usage(user_id, 'start')

    if store.is_accepted(user_id):
        await send_main_menu(event, 'Здравствуйте! Главное меню уже доступно.')
        return

    await send_policy(event)


@dp.message_created(Command('menu'))
async def handle_menu_command(event: MessageCreated):
    await send_main_menu(event)


@dp.message_created(Command('help'))
async def handle_help_command(event: MessageCreated):
    await event.message.answer(
        text=(
            'Доступные команды:\n'
            '/start — начать работу с ботом\n'
            '/menu — открыть главное меню\n'
            '/help — показать эту подсказку'
        ),
        attachments=[back_to_menu_keyboard()],
    )


@dp.message_callback()
async def handle_callback(event: MessageCallback):
    payload = event.callback.payload or ''
    user_id = event.callback.user.user_id
    store.record_interaction(user_id)

    if payload == ACCEPT_PAYLOAD:
        store.accept(user_id)
        record_usage(user_id, 'accept_policy')
        await event.answer(notification='Согласие сохранено')
        await send_main_menu(event, 'Спасибо! Теперь можно выбрать раздел.')
        return

    if payload == MENU_PAYLOAD:
        await event.answer(notification='Открываю меню')
        await send_main_menu(event)
        return

    if payload in {
        ADDRESSES_MENU_PAYLOAD,
        IFNS_DETAILS_MENU_PAYLOAD,
        ENS_HELP_MENU_PAYLOAD,
        MFC_MENU_PAYLOAD,
        DEBT_MENU_PAYLOAD,
        PAYMENTS_MENU_PAYLOAD,
        PHONES_MENU_PAYLOAD,
        WHITE_CHECK_MENU_PAYLOAD,
        FEEDBACK_START_PAYLOAD,
    }:
        await event.answer(notification='Открываю раздел')
        await send_section(event, payload)
        return

    if payload.startswith(MENU_SECTION_PREFIX):
        await event.answer(notification='Открываю раздел')
        await send_section(event, payload)
        return

    await event.answer(notification='Раздел пока не восстановлен')
    await event.message.answer(
        text='Этот сценарий ещё нужно дозаполнить из старого проекта.',
        attachments=[back_to_menu_keyboard()],
    )


@dp.message_created()
async def handle_text_message(event: MessageCreated):
    user_id = event.message.sender.user_id
    store.record_interaction(user_id)
    record_usage(user_id, 'message')

    if not store.is_accepted(user_id):
        await send_policy(event)
        return

    text = (event.message.body.text or '').strip().lower()
    if text in {'меню', 'menu', 'главное меню'}:
        await send_main_menu(event)
        return

    await event.message.answer(
        text='Я восстановлен и работаю через Webhook. Выберите нужный раздел в меню.',
        attachments=[main_menu_keyboard()],
    )


async def main():
    setup_json_logging()
    load_runtime_state()

    if WEBHOOK_URL:
        await bot.subscribe_webhook(WEBHOOK_URL)

    await dp.handle_webhook(
        bot=bot,
        host=WEBHOOK_HOST,
        port=WEBHOOK_PORT,
        log_level='critical',
    )


if __name__ == '__main__':
    asyncio.run(main())
