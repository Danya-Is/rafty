class Config:
    max_timeout: int

    def __init__(self):
        # максимально возможный таймаут в секундах
        self.max_timeout = 1
        self.event_loop_sleep_time = 0.05
