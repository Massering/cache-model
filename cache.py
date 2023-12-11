from config import *
from counter import Counter
from memory import Memory

INVALID = 0b00
MODIFIED = 0b01
SHARED = 0b10


class Cache:
    counter: Counter

    def __init__(self, counter):
        self.counter = counter
        self.memory = Memory(counter)
        self.data = [CacheSet() for _ in range(CACHE_SETS_COUNT)]

    def C1_READ8(self, address):
        self.counter += 2    # в одну и другую стороны
        return self.get(address, 1)

    def C1_READ16(self, address):
        self.counter += 2    # в одну и другую стороны
        return self.get(address, 2)

    def C1_READ32(self, address):
        self.counter += 4    # в одну и другую стороны
        return self.get(address, 4)

    def get(self, address: int, k: int):
        tag, idx, offset = Cache.parse_address(address)
        cache_set = self.data[idx]

        ind = self.get_line_from_set(tag, cache_set)

        return cache_set[ind].data[offset:offset + k]

    def C1_WRITE8(self, address, data: bytes):
        self.counter += 2    # в одну и другую стороны
        return self.set(address, data, 1)

    def C1_WRITE16(self, address, data: bytes):
        self.counter += 2    # в одну и другую стороны
        return self.set(address, data, 2)

    def C1_WRITE32(self, address, data: bytes):
        self.counter += 4    # в одну и другую стороны
        return self.set(address, data, 4)

    def set(self, address: int, data: bytes, k: int):
        tag, idx, offset = Cache.parse_address(address)
        cache_set = self.data[idx]

        ind = self.get_line_from_set(tag, cache_set)

        cache_set[ind].data = (cache_set[ind].data[:offset] + data + cache_set[ind].data[offset + k:])
        cache_set[ind].flags.msi = MODIFIED

    def get_line_from_set(self, tag, cache_set):
        bad_line_ind = 0
        for ind in range(CACHE_WAY):
            cache_line: CacheLine = cache_set[ind]
            if cache_line.tag == tag:
                self.counter.hit()
                self.counter += 6
                break

            if self.line_worse(cache_set[bad_line_ind], cache_line):
                bad_line_ind = ind
        else:
            ind = bad_line_ind
            self.counter += 4
            self.counter.miss()
            if cache_set[bad_line_ind].flags[0] == MODIFIED:
                # <- Допустим в этот момент мы начинаем отправлять в память плохую строку
                self.memory.C2_WRITE_LINE(cache_set[bad_line_ind].tag, cache_set[bad_line_ind].data)
            cache_set[bad_line_ind] = CacheLine(tag, self.memory.C2_READ_LINE(tag), SHARED, 0)

        self.modify_set(cache_set, ind)

        return ind

    @staticmethod
    def parse_address(address):
        tag = address >> (CACHE_IDX_LEN + CACHE_OFFSET_LEN) & (2 ** CACHE_TAG_LEN - 1)
        idx = address >> CACHE_OFFSET_LEN & (2 ** CACHE_IDX_LEN - 1)
        offset = address & (2 ** CACHE_OFFSET_LEN - 1)
        return tag, idx, offset

    def line_worse(self, line, other_line):
        if Cache.is_invalid(line):
            return 0
        if Cache.is_invalid(other_line):
            return 1
        return self.__class__.LRU_worse(line, other_line)

    @staticmethod
    def is_invalid(line):
        return line.flags[0] == INVALID

    @staticmethod
    def LRU_worse(line, other_line):
        raise LookupError('abstract method')

    @staticmethod
    def modify_set(cache_set, ind):
        raise LookupError('abstract method')


class LRUCache(Cache):
    @staticmethod
    def LRU_worse(line, other_line):
        return other_line.flags.lru > line.flags.lru

    @staticmethod
    def modify_set(cache_set, ind):
        k = cache_set[ind].flags.lru
        for i in range(CACHE_WAY):
            if cache_set[i].flags.lru <= k:
                cache_set[i].flags.lru += 1
        cache_set[ind].flags.lru = 0


class PLRUCache(Cache):
    @staticmethod
    def LRU_worse(line, other_line):
        return other_line.flags.lru < line.flags.lru

    @staticmethod
    def modify_set(cache_set, ind):
        if cache_set[ind].flags.lru == 0 and [cache_set[i].flags.lru for i in range(CACHE_WAY)].count(0) == 1:
            for i in range(CACHE_WAY):
                cache_set[i].flags.lru = 0
        cache_set[ind].flags.lru = 1


class Flags:
    def __init__(self, msi, lru):
        self.msi = msi
        self.lru = lru

    def __getitem__(self, ind):
        return [self.msi, self.lru][ind]

    def __setitem__(self, ind, item):
        if ind == 0:
            self.msi = item
        else:
            self.lru = item


class CacheLine:
    flags: Flags
    tag: int
    data: bytes

    def __init__(self, tag=0b000_000_000, data=Memory.NULL, msi=INVALID, lru=0):
        self.flags = Flags(msi, lru)
        self.tag = tag
        self.data = data


class CacheSet:
    lines: [CacheLine] * CACHE_WAY

    def __init__(self):
        self.lines = [CacheLine() for _ in range(CACHE_WAY)]

    def __getitem__(self, ind):
        return self.lines[ind]

    def __setitem__(self, ind, item):
        self.lines[ind] = item
