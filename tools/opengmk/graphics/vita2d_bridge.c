/* Small checked ABI over the installed libvita2d. No game data or shaders. */
#include <vita2d.h>
#include <psp2/display.h>
#include <psp2/kernel/sysmem.h>
#include <string.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdlib.h>

/* Reuse the installed library's clear GXP, with an independently owned patch.
 * Color-mask NONE is essential: vita2d_clear_screen would overwrite color. */
extern const SceGxmProgram clear_v_gxp_start, clear_f_gxp_start;
static SceGxmShaderPatcherId depth_vid, depth_fid;
static int depth_vregistered, depth_fregistered;
static SceGxmVertexProgram *depth_vp;
static SceGxmFragmentProgram *depth_fp, *probe_fp;
static const SceGxmProgramParameter *depth_color;

static atomic_int first_error, error_api;
static atomic_uint draw_calls;
static int checked(int rc, int api) {
    if (rc < 0 && !first_error) { first_error=rc; error_api=api; }
    return rc;
}
int howaw_gxm_error(void) { return first_error; }
int howaw_gxm_error_api(void) { return error_api; }
unsigned int howaw_gxm_draw_calls(void) { return draw_calls; }

void howaw_depth_fini(void) {
    SceGxmShaderPatcher *p=vita2d_get_shader_patcher();
    if (probe_fp) checked(sceGxmShaderPatcherReleaseFragmentProgram(p,probe_fp),20);
    if (depth_fp) checked(sceGxmShaderPatcherReleaseFragmentProgram(p,depth_fp),20);
    if (depth_vp) checked(sceGxmShaderPatcherReleaseVertexProgram(p,depth_vp),20);
    if (depth_fregistered) checked(sceGxmShaderPatcherUnregisterProgram(p,depth_fid),20);
    if (depth_vregistered) checked(sceGxmShaderPatcherUnregisterProgram(p,depth_vid),20);
    probe_fp=depth_fp=NULL; depth_vp=NULL; depth_vregistered=depth_fregistered=0;
}
static int depth_init(void) {
    if (depth_fp) return 0;
    SceGxmShaderPatcher *p=vita2d_get_shader_patcher();
    const SceGxmProgramParameter *pos=sceGxmProgramFindParameterByName(&clear_v_gxp_start,"aPosition");
    depth_color=sceGxmProgramFindParameterByName(&clear_f_gxp_start,"uClearColor");
    if (!pos || !depth_color) return -21;
    if (checked(sceGxmShaderPatcherRegisterProgram(p,&clear_v_gxp_start,&depth_vid),21)<0) return first_error;
    depth_vregistered=1;
    if (checked(sceGxmShaderPatcherRegisterProgram(p,&clear_f_gxp_start,&depth_fid),21)<0) return first_error;
    depth_fregistered=1;
    SceGxmVertexAttribute attr={0};
    attr.format=SCE_GXM_ATTRIBUTE_FORMAT_F32;attr.componentCount=2;
    attr.regIndex=sceGxmProgramParameterGetResourceIndex(pos);
    SceGxmVertexStream stream={0};stream.stride=sizeof(vita2d_clear_vertex);stream.indexSource=SCE_GXM_INDEX_SOURCE_INDEX_16BIT;
    if (checked(sceGxmShaderPatcherCreateVertexProgram(p,depth_vid,&attr,1,&stream,1,&depth_vp),22)<0) return first_error;
    SceGxmBlendInfo blend={0};blend.colorMask=SCE_GXM_COLOR_MASK_NONE;
    blend.colorFunc=blend.alphaFunc=SCE_GXM_BLEND_FUNC_NONE;
    if (checked(sceGxmShaderPatcherCreateFragmentProgram(p,depth_fid,SCE_GXM_OUTPUT_REGISTER_FORMAT_UCHAR4,SCE_GXM_MULTISAMPLE_NONE,&blend,&clear_v_gxp_start,&depth_fp),23)<0) return first_error;
    blend.colorMask=SCE_GXM_COLOR_MASK_ALL;
    return checked(sceGxmShaderPatcherCreateFragmentProgram(p,depth_fid,SCE_GXM_OUTPUT_REGISTER_FORMAT_UCHAR4,SCE_GXM_MULTISAMPLE_NONE,&blend,&clear_v_gxp_start,&probe_fp),23);
}
static void depth_state(SceGxmDepthFunc func,SceGxmDepthWriteMode write) {
    SceGxmContext *c=vita2d_get_context();
    sceGxmSetFrontDepthFunc(c,func);sceGxmSetBackDepthFunc(c,func);
    sceGxmSetFrontDepthWriteEnable(c,write);sceGxmSetBackDepthWriteEnable(c,write);
}
static int depth_triangle(int color,const float rgba[4]) {
    SceGxmContext *c=vita2d_get_context();void *uniform=NULL;
    vita2d_clear_vertex *v=vita2d_pool_memalign(3*sizeof(*v),16);
    if (!v) return -24;
    v[0]=(vita2d_clear_vertex){-1,-1};v[1]=(vita2d_clear_vertex){3,-1};v[2]=(vita2d_clear_vertex){-1,3};
    sceGxmSetVertexProgram(c,depth_vp);sceGxmSetFragmentProgram(c,color?probe_fp:depth_fp);
    if (checked(sceGxmReserveFragmentDefaultUniformBuffer(c,&uniform),24)<0) return first_error;
    if (checked(sceGxmSetUniformDataF(uniform,depth_color,0,4,rgba),25)<0) return first_error;
    if (checked(sceGxmSetVertexStream(c,0,v),26)<0) return first_error;
    return checked(sceGxmDraw(c,SCE_GXM_PRIMITIVE_TRIANGLES,SCE_GXM_INDEX_FORMAT_U16,vita2d_get_linear_indices(),3),3);
}
/* Caller flushes queued draws, owns the scene/viewport and restores depth state.
 * The reused clear vertex shader emits clip-space z=w=1 (far depth). */
int howaw_clear_depth(void) {
    int rc=depth_init();if (rc<0) return rc;
    const float ignored[4]={0,0,0,0};
    depth_state(SCE_GXM_DEPTH_FUNC_ALWAYS,SCE_GXM_DEPTH_WRITE_ENABLED);
    rc=depth_triangle(0,ignored);
    depth_state(SCE_GXM_DEPTH_FUNC_ALWAYS,SCE_GXM_DEPTH_WRITE_DISABLED);
    return rc;
}
/* Offscreen, never presented. Verify raw depth changes, ALL color bytes survive,
 * and a far fragment rejected before the clear is accepted afterwards. */
int howaw_depth_contract(unsigned int result[5]) {
    int rc=depth_init();if (rc<0) return rc;
    vita2d_texture *t=vita2d_create_empty_texture_rendertarget(32,32,SCE_GXM_TEXTURE_FORMAT_A8B8G8R8);
    if (!t) return -27;
    void *depth=NULL;uint32_t saved_depth[1024],saved_color[1024];
    rc=checked(sceKernelGetMemBlockBase(t->depth_UID,&depth),27);
    if (rc<0 || !depth || !t->gxm_rtgt || vita2d_texture_get_stride(t)!=128) {vita2d_free_texture(t);return -27;}
    uint32_t *pixels=vita2d_texture_get_datap(t);SceGxmContext *c=vita2d_get_context();
    const float seed[4]={1,0,0,1},far[4]={0,1,0,1};
    sceGxmDepthStencilSurfaceSetForceStoreMode(&t->gxm_sfd,SCE_GXM_DEPTH_STENCIL_FORCE_STORE_ENABLED);
    for (unsigned int phase=0;phase<3 && rc==0;phase++) {
        vita2d_pool_reset();
        sceGxmDepthStencilSurfaceSetForceLoadMode(&t->gxm_sfd,phase?SCE_GXM_DEPTH_STENCIL_FORCE_LOAD_ENABLED:SCE_GXM_DEPTH_STENCIL_FORCE_LOAD_DISABLED);
        vita2d_start_drawing_advanced(t,0);
        sceGxmSetViewport(c,16,16,16,-16,0.25f,0);
        if (phase==0) {
            depth_state(SCE_GXM_DEPTH_FUNC_ALWAYS,SCE_GXM_DEPTH_WRITE_ENABLED);rc=depth_triangle(1,seed);
            sceGxmSetViewport(c,16,16,16,-16,0.75f,0);
            depth_state(SCE_GXM_DEPTH_FUNC_LESS,SCE_GXM_DEPTH_WRITE_ENABLED);
            if (!rc) rc=depth_triangle(1,far);
        } else if (phase==1) {
            sceGxmSetViewport(c,16,16,16,-16,0.5f,0.5f);rc=howaw_clear_depth();
        } else {
            sceGxmSetViewport(c,16,16,16,-16,0.75f,0);
            depth_state(SCE_GXM_DEPTH_FUNC_LESS,SCE_GXM_DEPTH_WRITE_ENABLED);rc=depth_triangle(1,far);
        }
        vita2d_end_drawing();vita2d_wait_rendering_done();
        if (!rc) rc=first_error;
        if (!rc && phase==0) {
            memcpy(saved_depth,depth,sizeof(saved_depth));memcpy(saved_color,pixels,sizeof(saved_color));
            for (unsigned int i=0;i<1024;i++) result[0]+=pixels[i]==0xff0000ff;
        } else if (!rc && phase==1) {
            for (unsigned int i=0;i<1024;i++) {result[1]+=pixels[i]==saved_color[i];result[2]+=((uint32_t *)depth)[i]!=saved_depth[i];}
        } else if (!rc) {
            for (unsigned int i=0;i<1024;i++) result[3]+=pixels[i]==0xff00ff00;
        }
    }
    result[4]=draw_calls;
    depth_state(SCE_GXM_DEPTH_FUNC_ALWAYS,SCE_GXM_DEPTH_WRITE_DISABLED);
    sceGxmSetViewport(c,480,480,272,-272,0.5f,0.5f);
    vita2d_free_texture(t);
    if (rc) return rc;
    return result[0]==1024 && result[1]==1024 && result[2]==1024 && result[3]==1024?0:-28;
}

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
/* libvita2d's additive preset uses ONE/ONE. GM8 bm_add requires SRC_ALPHA/ONE.
 * Adapt only that exact preset at creation; normal and depth patches unchanged. */
int __real_sceGxmShaderPatcherCreateFragmentProgram(SceGxmShaderPatcher *p,SceGxmShaderPatcherId id,SceGxmOutputRegisterFormat out,SceGxmMultisampleMode msaa,const SceGxmBlendInfo *blend,const SceGxmProgram *vp,SceGxmFragmentProgram **fp);
int __wrap_sceGxmShaderPatcherCreateFragmentProgram(SceGxmShaderPatcher *p,SceGxmShaderPatcherId id,SceGxmOutputRegisterFormat out,SceGxmMultisampleMode msaa,const SceGxmBlendInfo *blend,const SceGxmProgram *vp,SceGxmFragmentProgram **fp) {
    SceGxmBlendInfo adjusted;
    if (blend && blend->colorMask==SCE_GXM_COLOR_MASK_ALL && blend->colorFunc==SCE_GXM_BLEND_FUNC_ADD && blend->alphaFunc==SCE_GXM_BLEND_FUNC_ADD && blend->colorSrc==SCE_GXM_BLEND_FACTOR_ONE && blend->colorDst==SCE_GXM_BLEND_FACTOR_ONE && blend->alphaSrc==SCE_GXM_BLEND_FACTOR_ONE && blend->alphaDst==SCE_GXM_BLEND_FACTOR_ONE) {
        adjusted=*blend;adjusted.colorSrc=adjusted.alphaSrc=SCE_GXM_BLEND_FACTOR_SRC_ALPHA;blend=&adjusted;
    }
    return checked(__real_sceGxmShaderPatcherCreateFragmentProgram(p,id,out,msaa,blend,vp,fp),29);
}

int howaw_graphics_init(void) {
    first_error=error_api=0; draw_calls=0;
    int rc=vita2d_init_advanced(256*1024);
    if (first_error) return first_error;
    if (rc!=1 || !vita2d_get_context() || !vita2d_get_shader_patcher() || !vita2d_get_linear_indices()) return -1;
    return 0;
}
void howaw_viewport(float x,float y,float w,float h) {
    sceGxmSetViewport(vita2d_get_context(),x+w/2,w/2,y+h/2,-h/2,0.5f,0.5f);
}
int howaw_clear_color_depth(unsigned int color) {
    depth_state(SCE_GXM_DEPTH_FUNC_ALWAYS,SCE_GXM_DEPTH_WRITE_ENABLED);
    vita2d_set_clear_color(color);vita2d_clear_screen();
    depth_state(SCE_GXM_DEPTH_FUNC_ALWAYS,SCE_GXM_DEPTH_WRITE_DISABLED);
    return first_error;
}
/* New E026 contract: overwrite color/depth inside an already-open scene;
 * a far fragment must then pass the depth test in a second loaded scene. */
int howaw_color_clear_contract(unsigned int result[2]) {
    int rc=depth_init();if (rc<0) return rc;
    vita2d_texture *t=vita2d_create_empty_texture_rendertarget(32,32,SCE_GXM_TEXTURE_FORMAT_A8B8G8R8);
    if (!t) return -30;
    SceGxmContext *c=vita2d_get_context();const float red[4]={1,0,0,1},blue[4]={0,0,1,1};
    sceGxmDepthStencilSurfaceSetForceStoreMode(&t->gxm_sfd,SCE_GXM_DEPTH_STENCIL_FORCE_STORE_ENABLED);
    for (unsigned int phase=0;phase<2 && rc==0;phase++) {
        vita2d_pool_reset();sceGxmDepthStencilSurfaceSetForceLoadMode(&t->gxm_sfd,phase?SCE_GXM_DEPTH_STENCIL_FORCE_LOAD_ENABLED:SCE_GXM_DEPTH_STENCIL_FORCE_LOAD_DISABLED);
        vita2d_start_drawing_advanced(t,0);
        if (!phase) {
            sceGxmSetViewport(c,16,16,16,-16,0.25f,0);
            depth_state(SCE_GXM_DEPTH_FUNC_ALWAYS,SCE_GXM_DEPTH_WRITE_ENABLED);rc=depth_triangle(1,red);
            sceGxmSetViewport(c,16,16,16,-16,0.5f,0.5f);
            if (!rc) rc=howaw_clear_color_depth(0xff00ff00);
        } else {
            sceGxmSetViewport(c,16,16,16,-16,0.75f,0);
            depth_state(SCE_GXM_DEPTH_FUNC_LESS,SCE_GXM_DEPTH_WRITE_ENABLED);rc=depth_triangle(1,blue);
        }
        vita2d_end_drawing();vita2d_wait_rendering_done();if (!rc) rc=first_error;
        uint32_t *pixels=vita2d_texture_get_datap(t);
        if (!rc) for (unsigned int i=0;i<1024;i++) result[phase]+=pixels[i]==(phase?0xffff0000:0xff00ff00);
    }
    depth_state(SCE_GXM_DEPTH_FUNC_ALWAYS,SCE_GXM_DEPTH_WRITE_DISABLED);sceGxmSetViewport(c,480,480,272,-272,0.5f,0.5f);
    vita2d_free_texture(t);if (rc) return rc;
    return result[0]==1024 && result[1]==1024?0:-31;
}
void *howaw_texture_create(unsigned int w,unsigned int h,int main_ram,unsigned int *stride,unsigned int *mapped) {
    /* Own only allocation: reuse public vita2d texture layout/drawing/free.
     * Its generic allocator may fall back to another pool; these budgets must
     * instead reflect the pool actually requested, with explicit map errors. */
    if (first_error || !w || !h || w>2048 || h>2048) return NULL;
    unsigned int row=((w+7)&~7)*4,bytes=row*h,alignment=main_ram?4096:262144;
    unsigned int size=(bytes+alignment-1)&~(alignment-1);
    SceKernelFreeMemorySizeInfo free_info={0};free_info.size=sizeof(free_info);
    if (checked(sceKernelGetFreeMemorySize(&free_info),30)<0) return NULL;
    unsigned int available=main_ram?free_info.size_user:free_info.size_cdram;
    if (available<size+(main_ram?16:8)*1024*1024) {checked(-32,30);return NULL;}
    vita2d_texture *t=calloc(1,sizeof(*t));if (!t) return NULL;
    SceKernelMemBlockType type=main_ram?SCE_KERNEL_MEMBLOCK_TYPE_USER_RW_UNCACHE:SCE_KERNEL_MEMBLOCK_TYPE_USER_CDRAM_RW;
    int rc=sceKernelAllocMemBlock("howaw_atlas",type,size,NULL);
    if (rc<0) {checked(rc,31);free(t);return NULL;}
    t->data_UID=rc;void *data=NULL;int is_mapped=0;
    rc=checked(sceKernelGetMemBlockBase(t->data_UID,&data),32);
    if (rc>=0) {rc=checked(sceGxmMapMemory(data,size,SCE_GXM_MEMORY_ATTRIB_READ),33);is_mapped=rc>=0;}
    if (rc>=0) {
        memset(data,0,bytes);
        rc=checked(sceGxmTextureInitLinear(&t->gxm_tex,data,SCE_GXM_TEXTURE_FORMAT_A8B8G8R8,w,h,0),7);
    }
    SceKernelMemBlockInfo info={0};info.size=sizeof(info);
    if (rc>=0) rc=checked(sceKernelGetMemBlockInfoByAddr(data,&info),8);
    if (rc>=0 && (info.type!=type || info.mappedBase!=data || info.mappedSize!=size)) rc=checked(-33,8);
    if (rc<0) {
        if (is_mapped) checked(sceGxmUnmapMemory(data),34);
        checked(sceKernelFreeMemBlock(t->data_UID),35);free(t);return NULL;
    }
    *stride=row;*mapped=info.mappedSize;
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
int howaw_draw_colors(const vita2d_color_vertex *v,unsigned int n) {
    if (!n || n>1536 || n%3) return -1;
    void *gpu=vita2d_pool_memalign(n*sizeof(*v),16);if (!gpu) return -2;
    memcpy(gpu,v,n*sizeof(*v));vita2d_draw_array(SCE_GXM_PRIMITIVE_TRIANGLES,gpu,n);return first_error;
}
int howaw_draw_lines(const vita2d_color_vertex *v,unsigned int n) {
    if (!n || n>1536 || n%2) return -1;
    void *gpu=vita2d_pool_memalign(n*sizeof(*v),16);if (!gpu) return -2;
    memcpy(gpu,v,n*sizeof(*v));SceGxmContext *c=vita2d_get_context();
    sceGxmSetFrontPointLineWidth(c,1);sceGxmSetBackPointLineWidth(c,1);
    vita2d_draw_array(SCE_GXM_PRIMITIVE_LINES,gpu,n);return first_error;
}
int howaw_finish_frame(void) {
    vita2d_end_drawing();vita2d_wait_rendering_done();
    if (first_error) return first_error;
    vita2d_swap_buffers();
    checked(sceGxmDisplayQueueFinish(),9);
    return first_error;
}
