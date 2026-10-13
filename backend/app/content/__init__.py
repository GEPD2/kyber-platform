"""All levels, in order. The keys are the mode names the API and frontend use."""
from app.content import easy, hard, insane, lab, medium, veryeasy, veryhard

LEVELS: dict[str, list[dict]] = {
    "veryeasy": veryeasy.QUESTIONS,
    "easy": easy.QUESTIONS,
    "medium": medium.QUESTIONS,
    "hard": hard.QUESTIONS,
    "veryhard": veryhard.QUESTIONS,
    "insane": insane.QUESTIONS,
    "lab": lab.QUESTIONS,
}

# Public, answer-free data sent once per mode (the Lab's virtual project files).
LEVEL_EXTRAS: dict[str, dict] = {
    "lab": {"files": lab.FILES, "cwd": "~/mlkem-esp32", "prompt_user": "student@lab"},
}
