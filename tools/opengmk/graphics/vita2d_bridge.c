/* Small checked ABI over the installed libvita2d. No game data or shaders. */
#include <vita2d.h>
#include <psp2/display.h>
#include <psp2/kernel/sysmem.h>
#include <string.h>
#include <stdint.h>
#include <stdatomic.h>

static atomic_int first_error, error_api;
static atomic_uint draw_calls;
static int checked(int rc, int api) {
    if (rc < 0 && !first_error) { first_error=rc; error_api=api; }
    return rc;
}
int howaw_gxm_error(void) { return first_error; }
int howaw_gxm_error_api(void) { return error_api; }
unsigned int howaw_gxm_draw_calls(void) { return draw_calls; }

/* Linker wrappers retain errors hidden by libvita2d's void drawing APIs. */
int __real_sceGxmInitialize(const SceGxmInitializeParams *p);
int __wrap_sceGxmInitialize(const SceGxmInitializeParams *p) { return checked(__real_sceGxmInitialize(p),1); }
int __real_sceGxmBeginScene(SceGxmContext *c,unsigned int f,const SceGxmRenderTarget *r,const SceGxmValidRegion *v,SceGxmSyncObject *vs,SceGxmSyncObject *fs,const SceGxmColorSurface *cs,const SceGxmDepthStencilSurface *ds);
int __wrap_sceGxmBeginScene(SceGxmContext *c,unsigned int f,const SceGxmRenderTarget *r,const SceGxmValidRegion *v,SceGxmSyncObject *vs,SceGxmSyncObject *fs,const SceGxmColorSurface *cs,const SceGxmDepthStencilSurface *ds) { return checked(__real_sceGxmBeginScene(c,f,r,v,vs,fs,cs,ds),2); }
int __real_sceGxmDraw(SceGxmContext *c,SceGxmPrimitiveType p,SceGxmIndexFormat f,const void *i,unsigned int n);
int __wrap_sceGxmDraw(SceGxmContext *c,SceGxmPrimitiveType p,SceGxmIndexFormat f,const void *i,unsigned int n) { ++draw_calls; return checked(__real_sceGxmDraw(c,p,f,i,n),3); }
int __real_sceGxmEndScene(SceGxmContext *c,const SceGxmNotification *v,const SceGxmNotification *f);
int __wrap_sceGxmEndScene(SceGxmContext *c,const SceGxmNotification *v,const SceGxmNotification *f) { return checked(__real_sceGxmEndScene(c,v,f),4); }
int __real_sceGxmDisplayQueueAddEntry(SceGxmSyncObject *o,SceGxmSyncObject *n,const void *d);
int __wrap_sceGxmDisplayQueueAddEntry(SceGxmSyncObject *o,SceGxmSyncObject *n,const void *d) { return checked(__real_sceGxmDisplayQueueAddEntry(o,n,d),5); }
int __real_sceDisplaySetFrameBuf(const SceDisplayFrameBuf *p,int sync);
int __wrap_sceDisplaySetFrameBuf(const SceDisplayFrameBuf *p,int sync) { return checked(__real_sceDisplaySetFrameBuf(p,sync),6); }
int __real_sceGxmTextureInitLinear(SceGxmTexture *t,const void *d,SceGxmTextureFormat f,unsigned int w,unsigned int h,unsigned int m);
int __wrap_sceGxmTextureInitLinear(SceGxmTexture *t,const void *d,SceGxmTextureFormat f,unsigned int w,unsigned int h,unsigned int m) { return checked(__real_sceGxmTextureInitLinear(t,d,f,w,h,m),7); }

int howaw_graphics_init(void) {
    first_error=error_api=0; draw_calls=0;
    int rc=vita2d_init_advanced(256*1024);
    if (first_error) return first_error;
    if (rc!=1 || !vita2d_get_context() || !vita2d_get_shader_patcher() || !vita2d_get_linear_indices()) return -1;
    return 0;
}
void *howaw_texture_create(unsigned int w,unsigned int h,unsigned int *stride,unsigned int *mapped) {
    vita2d_texture *t=vita2d_create_empty_texture(w,h);
    if (!t) return NULL;
    if (first_error) { vita2d_free_texture(t); return NULL; }
    void *data=vita2d_texture_get_datap(t);
    if (!data) { vita2d_free_texture(t); return NULL; }
    *stride=vita2d_texture_get_stride(t);
    SceKernelMemBlockInfo info={0};info.size=sizeof(info);
    int rc=sceKernelGetMemBlockInfoByAddr(data,&info);
    if (rc<0) { checked(rc,8); vita2d_free_texture(t); return NULL; }
    *mapped=info.mappedSize;
    vita2d_texture_set_filters(t,SCE_GXM_TEXTURE_FILTER_POINT,SCE_GXM_TEXTURE_FILTER_POINT);
    return t;
}
int howaw_draw_batch(const vita2d_texture *t,const vita2d_texture_vertex *v,unsigned int n,unsigned int tint) {
    if (!n || n>1536 || n%3 || !t) return -1;
    void *gpu=vita2d_pool_memalign(n*sizeof(*v),16);
    if (!gpu) return -2;
    memcpy(gpu,v,n*sizeof(*v));
    vita2d_draw_array_textured(t,SCE_GXM_PRIMITIVE_TRIANGLES,gpu,n,tint);
    return first_error;
}
int howaw_finish_frame(void) {
    vita2d_end_drawing();vita2d_wait_rendering_done();
    if (first_error) return first_error;
    vita2d_swap_buffers();
    checked(sceGxmDisplayQueueFinish(),9);
    return first_error;
}
