from config import *


class Memory:
    NULL = b'\x00' * CACHE_LINE_SIZE

    def __init__(self, counter):
        self.counter = counter
        line = ''.join(chr(i) for i in range(CACHE_LINE_SIZE)).encode(encoding="utf-8")
        self.memory = [line] * (MEM_SIZE // CACHE_LINE_SIZE)

    def C2_READ_LINE(self, tag: int):
        # принятие кэш-линии за CACHE_LINE_SIZE / 2
        self.counter += ceil(CACHE_LINE_SIZE / 2)
        return self.get(tag)

    def get(self, tag: int):
        self.counter += 100
        return self.memory[tag]

    def C2_WRITE_LINE(self, tag: int, data: bytes):
        # отправка кэш-линии за CACHE_LINE_SIZE / 2
        self.counter += ceil(CACHE_LINE_SIZE / 2)
        # принятие ответа за 1
        self.counter += 1
        return self.set(tag, data)

    def set(self, tag: int, data: bytes):
        self.counter += 100
        self.memory[tag] = data
        return b'\x01'
