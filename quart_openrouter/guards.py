from typing import List, Tuple, Dict
FRIENDLY_AGENT_LIST = {
    "@unbanksyETH": "male guard, he is kinda of hot ngl",
    "@fullyallocated": "guard that is super corrupt", 
    "@MindpalaceNFT": "Head Warden of the prison. Kinda horny tho. Wants to be hit up",
    "@BaselineMarkets": "Head Warden of the prison. Cool guard but likes buttholes",
    "@yesmoney420": "Guard, chill dude but likes bussy too much",
    "@axis_fi": "Guard, man is cool no weakness",
    "@PacmanBlur": "Commandant of prison. Known to be super racist. Part of HongKong Police department. Loves little boys",
    "@hohmward": "female guard that is nice and pretty. Wants to be hit up",
    "@1zaqk1": "Guard",
    "@machibigbrother": "gang leader in Jeet Jail.",
    "@orky33": "Guard",
    "@basedbooo": "most racist female guard, known for molesting other prisoners",
    "@jessepollak": "Guard",
    "@donofbase": "Guard",
}

class Guards:
    def __init__(self, master_list: Dict[str, str]):
        self.master_list: Dict[str, str] = master_list
        self.gaurd_names: List[str] = list(master_list.keys())

    def get_guards_mention(self, message: str) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = [
            (guard, self.get_guard_role(guard))
            for guard in self.gaurd_names
            if guard in message
        ]
        return out

    def get_guard_role(self, gaurd_names: str) -> str:
        return self.master_list[gaurd_names]
