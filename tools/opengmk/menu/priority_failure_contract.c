/* Execute ONLY the hash-checked, fully reviewed GM8 priority procedure slice.
 * No original EXE startup or game data executes. x86 MSVC, bounded own child.
 * Integer-only conversion fixture covers the game's 0/1/2 arguments, not general
 * proprietary real coercion. Imported setters genuinely fail on NULL handles.
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#pragma comment(lib,"bcrypt.lib")
static unsigned int pcalls,tcalls,perr,terr;
static DWORD seen_class;static int seen_thread;
static HANDLE WINAPI absent_handle(void) {return NULL;}
static BOOL WINAPI fail_process(HANDLE p,DWORD c) {
    ++pcalls;seen_class=c;BOOL ok=SetPriorityClass(p,c);perr=GetLastError();assert(!ok);return ok;
}
static BOOL WINAPI fail_thread(HANDLE t,int p) {
    ++tcalls;seen_thread=p;BOOL ok=SetThreadPriority(t,p);terr=GetLastError();assert(!ok);return ok;
}
__declspec(naked) static int integer_conversion(void) {
    __asm {sub esp,4}
    __asm {fistp dword ptr [esp]}
    __asm {pop eax}
    __asm {ret}
}
int main(int argc,char **argv) {
    assert(argc==2);
    unsigned char bytes[246],hash[32];FILE *f=NULL;assert(!fopen_s(&f,argv[1],"rb"));
    assert(fread(bytes,1,sizeof(bytes),f)==sizeof(bytes));assert(fgetc(f)==EOF);fclose(f);
    const unsigned char expected[32]={0x0b,0x30,0xb3,0x3d,0x33,0x50,0x70,0x51,0x61,0xee,0x62,0x22,0x31,0x19,0x35,0xc1,0x70,0xa0,0x30,0x0c,0x57,0x41,0xf9,0x45,0x21,0xe1,0xb1,0x1d,0x10,0x05,0x30,0x02};
    BCRYPT_ALG_HANDLE alg;assert(BCryptOpenAlgorithmProvider(&alg,BCRYPT_SHA256_ALGORITHM,NULL,0)>=0);
    assert(BCryptHash(alg,NULL,0,bytes,sizeof(bytes),hash,sizeof(hash))>=0);BCryptCloseAlgorithmProvider(alg,0);
    assert(!memcmp(expected,hash,32));
    unsigned char *code=VirtualAlloc(NULL,4096,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);assert(code);memcpy(code,bytes,sizeof(bytes));
    const unsigned int sites[]={0xb,0x12,0x4a,0x50,0x58,0x64,0x6a,0x72,0x7b,0x81,0x89,0x92,0x98,0xa0,0xac,0xb2,0xba,0xc6,0xcc,0xd4,0xdd,0xe3,0xeb};
    for(unsigned int i=0;i<sizeof(sites)/sizeof(*sites);++i) {
        unsigned int at=sites[i];assert(code[at]==0xe8);
        uint32_t old=0x56a5d8+at+5+*(int32_t *)(code+at+1);void *target=NULL;
        switch(old) {
            case 0x403498:target=integer_conversion;break;
            case 0x407fb0:case 0x407fa0:target=absent_handle;break;
            case 0x408180:target=fail_process;break;
            case 0x408190:target=fail_thread;break;
            default:assert(0);
        }
        *(int32_t *)(code+at+1)=(int32_t)((unsigned char *)target-code-at-5);
    }
    // Relocate the already reviewed absolute switch table and its seven targets.
    assert(*(uint32_t *)(code+0x28)==0x56a604);
    *(uint32_t *)(code+0x28)=(uint32_t)(code+0x2c);
    for(unsigned int i=0;i<7;++i) {
        uint32_t *p=(uint32_t *)(code+0x2c+4*i);assert(*p>=0x56a620 && *p<=0x56a6b3);
        *p=(uint32_t)(code+(*p-0x56a5d8));
    }
    DWORD old;assert(VirtualProtect(code,4096,PAGE_EXECUTE_READ,&old));assert(FlushInstructionCache(GetCurrentProcess(),code,sizeof(bytes)));
    typedef void (__stdcall *Procedure)(int,void *,void *);
    DWORD classes[]={0x20,0x20,0x80};int priorities[]={0,1,2};
    for(int n=0;n<3;++n) {
        struct {uint32_t kind,padding;double value;} arg={0,0,(double)n};
        unsigned char result[24],saved[24];memset(result,0xa5,sizeof(result));memcpy(saved,result,sizeof(result));
        pcalls=tcalls=0;((Procedure)code)(1,result,&arg);
        assert(pcalls==1 && tcalls==1 && perr==ERROR_INVALID_HANDLE && terr==ERROR_INVALID_HANDLE);
        assert(seen_class==classes[n] && seen_thread==priorities[n]);assert(!memcmp(saved,result,sizeof(result)));
        printf("PASS priority=%d process_calls=%u thread_calls=%u process_error=%u thread_error=%u result_slot_untouched=1\n",n,pcalls,tcalls,perr,terr);
    }
    assert(VirtualFree(code,0,MEM_RELEASE));return 0;
}
