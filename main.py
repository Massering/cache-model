from cache import *

'''
C:

int8 a[64][32];         # 1 байт/элемент
int16 b[32][60];        # 2 байта/элемент
int32 c[64][60];        # 4 байта/элемент

void mmul()                            // такты
{                                      // 2
  int8 *pa = a;                        // 1
  int32 *pc = c;                       // 1
  for (int y = 0; y < 64; y++)         // 2
  {
    for (int x = 0; x < 60; x++)       // 2 * 64
    {
      int16 *pb = b;                   // 1 * 64 * 60
      int32 s = 0;                     // 1 * 64 * 60
      for (int k = 0; k < 32; k++)     // 2 * 64 * 60
      {
        s += pa[k] * pb[x];            // CALC
        pb += 60;                      // 1 * 64 * 60 * 32
      }                                // 3 * 64 * 60 * 32

      pc[x] = s;                       // CALC
    }                                  // 3 * 64 * 60

    pa += 32;                          // 1 * 64
    pc += 60;                          // 1 * 64
  }                                    // 3 * 64
}                                      // 4


Assembler:

a:
        .zero   8192
b:
        .zero   7680
c:
        .zero   15360
mmul:
        push    rbp                                
        mov     rbp, rsp                           
        mov     QWORD PTR [rbp-8], OFFSET FLAT:a   
        mov     QWORD PTR [rbp-16], OFFSET FLAT:c  
        mov     DWORD PTR [rbp-20], 0              
        jmp     .L2                                
.L7:
        mov     DWORD PTR [rbp-24], 0              
        jmp     .L3                                
.L6:
        mov     QWORD PTR [rbp-32], OFFSET FLAT:b  
        mov     DWORD PTR [rbp-36], 0   
        mov     DWORD PTR [rbp-40], 0   
        jmp     .L4                     
.L5:
        mov     eax, DWORD PTR [rbp-40] 
        cdqe                            
        lea     rdx, [0+rax*4]          
        mov     rax, QWORD PTR [rbp-8]  
        add     rax, rdx                
        mov     edx, DWORD PTR [rax]    
        mov     eax, DWORD PTR [rbp-24] 
        cdqe                            
        lea     rcx, [0+rax*4]          
        mov     rax, QWORD PTR [rbp-32] 
        add     rax, rcx                
        mov     eax, DWORD PTR [rax]    
        imul    eax, edx                
        add     DWORD PTR [rbp-36], eax 
        add     QWORD PTR [rbp-32], 240 
        add     DWORD PTR [rbp-40], 1   
.L4:
        cmp     DWORD PTR [rbp-40], 31  
        jle     .L5                     
        mov     eax, DWORD PTR [rbp-24]
        cdqe                           
        lea     rdx, [0+rax*4]         
        mov     rax, QWORD PTR [rbp-16]
        add     rdx, rax               
        mov     eax, DWORD PTR [rbp-36]
        mov     DWORD PTR [rdx], eax   
        add     DWORD PTR [rbp-24], 1  
.L3:
        cmp     DWORD PTR [rbp-24], 59 
        jle     .L6                    
        sub     QWORD PTR [rbp-8], -128
        add     QWORD PTR [rbp-16], 240
        add     DWORD PTR [rbp-20], 1  
.L2:
        cmp     DWORD PTR [rbp-20], 63 
        jle     .L7
        ret
'''

M, N, K = 64, 60, 32
a = 0x40000
b = 0x40000 + M * K
c = 0x40000 + M * K + K * N * 2


def mmul(cache: Cache, counter: Counter):
    counter += 2  # push, mov

    pa = a
    counter += 1  # mov
    pc = c
    counter += 1  # mov

    counter += 2  # mov, jmp
    for y in range(M):

        counter += 2  # mov, jmp
        for x in range(N):
            pb = b
            counter += 1  # mov

            s = 0
            counter += 1  # mov

            counter += 2  # mov, jmp
            for k in range(K):
                s = (s + int.from_bytes(cache.C1_READ8(pa + k * 1)) *
                     int.from_bytes(cache.C1_READ16(pb + x * 2))) % 2 ** 32
                # cache updates counter itself
                counter += 5  # imul

                pb += N * 2
                counter += 1  # add

                counter += 3  # add, cmp, jle

            cache.C1_WRITE32(pc + x * 4, s.to_bytes(4))
            # cache updates counter itself

            counter += 3  # add, cmp, jle

        pa += K
        counter += 1  # sub
        pc += N * 4
        counter += 1  # add

        counter += 3  # add, cmp, jle

    counter += 1  # ret


if __name__ == '__main__':
    counter = Counter()
    cache = LRUCache(counter)
    mmul(cache, counter)
    print('LRU:\thit perc. %3.4f%%\ttime: %d' % (counter.get_stat()))

    counter = Counter()
    cache = PLRUCache(counter)
    mmul(cache, counter)
    print('pLRU:\thit perc. %3.4f%%\ttime: %d' % (counter.get_stat()))
