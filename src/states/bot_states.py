from aiogram.dispatcher.filters.state import StatesGroup, State

class PromptStates(StatesGroup):
    confirm_replacement = State()
    waiting_for_joke = State()

class VoteStates(StatesGroup):
    showing_page = State()
    waiting_for_vote = State()

class ResultsStates(StatesGroup):
    showing_results = State()

class SuggestPromptStates(StatesGroup):
    waiting_for_prompt = State()
    confirm_replacement = State()