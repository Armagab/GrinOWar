from . import start, prompt, vote, suggest, admin, profile

def register_all_handlers(dp):
    start.register_start_handlers(dp)
    profile.register_profile_handlers(dp)
    vote.register_vote_handlers(dp)
    prompt.register_prompt_handlers(dp)
    suggest.register_suggest_handlers(dp)
    admin.register_admin_handlers(dp)