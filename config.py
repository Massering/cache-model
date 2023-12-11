from math import ceil, log2

ADDR_LEN = 20                                                  # 20 (бит) - длина адреса
MEM_SIZE = 2 ** ADDR_LEN                                       # 1048576 (байт) - размер памяти
CACHE_WAY = 4                                                  # 4 - ассоциативность
CACHE_TAG_LEN = 9                                              # 9 (бит) - длина тега адреса
CACHE_LINE_SIZE = 128                                          # 128 (байт) - размер кэш-линии
CACHE_OFFSET_LEN = ceil(log2(CACHE_LINE_SIZE))                 # 7 (бит) - длина смещения внутри кэш-линии
CACHE_IDX_LEN = ADDR_LEN - CACHE_TAG_LEN - CACHE_OFFSET_LEN    # 4 (бит) - длина индекса блока кэш-линий
CACHE_SETS_COUNT = 2 ** CACHE_IDX_LEN                          # 16 - кол-во блоков кэш-линий
CACHE_LINE_COUNT = CACHE_SETS_COUNT * CACHE_WAY                # 64 - кол-во кэш-линий
CACHE_SIZE = CACHE_LINE_SIZE * CACHE_LINE_COUNT                # 8192 (байт) - размер кэша, без учёта служ. информации

# Конфигурация кэша: look-through write-back
# Политика вытеснения кэша: LRU и bit-pLRU

# Шины:
# А1 и А2 = ADDR_LEN = 20 (бит)
# D1 и D2 = 16 (бит)
# по С1 и С2 команды поступают в разные стороны разные
# так что нам нужно взять логарифм из наибольшего числа команд в одну сторону
# C1 = ceil(log2(max(6, 1))) = 3 (бит)
# C2 = ceil(log2(max(2, 1))) = 1 (бит)
