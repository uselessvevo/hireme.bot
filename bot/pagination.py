from aiogram import types
from aiogram.fsm.context import FSMContext


async def pagination_keyboard_factory(
    callback_instance,
    callback_data,
    fsm_state: FSMContext
) -> list[list[types.InlineKeyboardButton], list[types.InlineKeyboardButton]]:
    """
    Pagination keyboard factory method

    Args:
        callback_instance (CallbackData): any `CallbackData` instance
        callback_data (CallbackData): any `CallbackData` data
        fsm_state (FSMContext):

    State args:
        pages_total (int): Calculated total quantity of pages into `FSMState`
            For example: round(len(query_record_result) / 100 * 10)
        current_offset (int): Offset size for OFFSET SQL operator

    Returns:
        list of arrow and page buttons
    """
    #                                        v --- pressed
    # Pagination must be like this: [1 2 3 4 5 ... max] -> [3 4 5 6 7 ... max]
    state_data = await fsm_state.get_data()
    page_amount = state_data.get("pages_total")
    current_offset = int(state_data.get("current_offset", 0))

    page_buttons: list[types.InlineKeyboardButton] = []
    arrow_buttons: list[types.InlineKeyboardButton] = [
        types.InlineKeyboardButton(
            text="←",
            callback_data=callback_instance(
                action="previous",
                offset=10,
                user_id=callback_data.user_id
            ).pack()
        ),
        types.InlineKeyboardButton(
            text="→",
            callback_data=callback_instance(
                action="next",
                offset=10,
                user_id=callback_data.user_id
            ).pack()
        )
    ]

    # Tuning range start and stop positions

    start_page_slice = 0 if current_offset <= 10 else current_offset // 10 - 2

    # Why do we divide `current_offset` by 10 and adding 1?
    # Because, for example, if we have 100 records in our table,
    # and we want to get the latest from it,
    # we need to type `OFFSET 90`, not `OFFSET 100`
    # So, in `change_offset` method we're subtracting 10
    # from `current_offset` when it equals to `pages_total`
    stop_page_slice = 5
    if (current_offset // 10) + 1 == page_amount:
        stop_page_slice = page_amount
    elif current_offset > 10:
        stop_page_slice = current_offset // 10 + 3

    for page in range(start_page_slice, stop_page_slice):
        page_buttons.append(
            types.InlineKeyboardButton(
                text=str(page + 1),
                callback_data=callback_instance(
                    action="manually",
                    offset=page * 10,
                    user_id=callback_data.user_id,
                ).pack()
            )
        )

    page_buttons.append(
        types.InlineKeyboardButton(
            text=str(page_amount),
            callback_data=callback_instance(
                action="manually",
                offset=page_amount * 10,
                user_id=callback_data.user_id,
            ).pack()
        )
    )
    page_buttons.insert(
        -1,
        types.InlineKeyboardButton(
            text="...",
            callback_data="__UNHANDLED__"
        )
    )

    return [page_buttons, arrow_buttons]


async def change_current_offset(
    action: str,
    new_offset: int,
    current_offset: int,
    page_amount: int
) -> int:
    """
    Change current offset method

    Args:
        action (str): next, previous, manually
        new_offset (int): new offset
        current_offset (int): current offset
        page_amount (int): total pages quantity
    """
    if action in ("next", "previous", "manually"):
        # Checking action type
        if action == "next":
            current_offset = new_offset
        elif action == "previous":
            current_offset = new_offset - 10
        elif action == "manually":
            current_offset = new_offset

        if current_offset < 0:
            current_offset = 0
        if current_offset == page_amount * 10:
            current_offset = page_amount * 10 - 10

        return current_offset
