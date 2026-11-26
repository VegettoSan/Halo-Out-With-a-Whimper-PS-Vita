/* Authored adapter to cached SDL2 GXM shader programs (zlib license).
 * Only shader rodata is linked; no SDL renderer, runtime or vitaGL dependency.
 * Program binaries remain private build outputs. See SDL_SHADER_NOTICE.txt. */
extern const unsigned char gxm_shader_texture_v[],gxm_shader_texture_f[];
typedef struct {float x,y,u,v,color[4];} tint_vertex;
static SceGxmShaderPatcherId tint_vid,tint_fid;
static int tint_vregistered,tint_fregistered;
static SceGxmVertexProgram *tint_vp;
static SceGxmFragmentProgram *tint_fp[2];
static const SceGxmProgramParameter *tint_wvp;
static void tint_fini(void) {
    SceGxmShaderPatcher *p=vita2d_get_shader_patcher();
    for (int i=0;i<2;i++) if (tint_fp[i]) {checked(sceGxmShaderPatcherReleaseFragmentProgram(p,tint_fp[i]),40);tint_fp[i]=NULL;}
    if (tint_vp) {checked(sceGxmShaderPatcherReleaseVertexProgram(p,tint_vp),40);tint_vp=NULL;}
    if (tint_fregistered) {checked(sceGxmShaderPatcherUnregisterProgram(p,tint_fid),40);tint_fregistered=0;}
    if (tint_vregistered) {checked(sceGxmShaderPatcherUnregisterProgram(p,tint_vid),40);tint_vregistered=0;}
}
static int tint_init(void) {
    if (tint_fp[1]) return 0;
    const SceGxmProgram *vp=(const SceGxmProgram *)gxm_shader_texture_v,*fp=(const SceGxmProgram *)gxm_shader_texture_f;
    const char *names[]={"aPosition","aTexcoord","aColor"};SceGxmVertexAttribute attr[3]={0};
    tint_wvp=sceGxmProgramFindParameterByName(vp,"wvp");if (!tint_wvp) return -40;
    for (int i=0;i<3;i++) {const SceGxmProgramParameter *p=sceGxmProgramFindParameterByName(vp,names[i]);if (!p) return -41;
        attr[i].offset=i*8;attr[i].format=SCE_GXM_ATTRIBUTE_FORMAT_F32;attr[i].componentCount=i==2?4:2;attr[i].regIndex=sceGxmProgramParameterGetResourceIndex(p);}
    SceGxmShaderPatcher *p=vita2d_get_shader_patcher();int rc=checked(sceGxmShaderPatcherRegisterProgram(p,vp,&tint_vid),41);if (rc<0) return rc;tint_vregistered=1;
    rc=checked(sceGxmShaderPatcherRegisterProgram(p,fp,&tint_fid),41);if (rc<0) return rc;tint_fregistered=1;
    SceGxmVertexStream stream={0};stream.stride=sizeof(tint_vertex);stream.indexSource=SCE_GXM_INDEX_SOURCE_INDEX_16BIT;
    rc=checked(sceGxmShaderPatcherCreateVertexProgram(p,tint_vid,attr,3,&stream,1,&tint_vp),42);if (rc<0) return rc;
    for (int i=0;i<2;i++) {SceGxmBlendInfo blend={0};blend.colorMask=SCE_GXM_COLOR_MASK_ALL;blend.colorFunc=blend.alphaFunc=SCE_GXM_BLEND_FUNC_ADD;
        blend.colorSrc=blend.alphaSrc=SCE_GXM_BLEND_FACTOR_SRC_ALPHA;blend.colorDst=blend.alphaDst=i?SCE_GXM_BLEND_FACTOR_ONE:SCE_GXM_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA;
        rc=checked(sceGxmShaderPatcherCreateFragmentProgram(p,tint_fid,SCE_GXM_OUTPUT_REGISTER_FORMAT_UCHAR4,SCE_GXM_MULTISAMPLE_NONE,&blend,vp,&tint_fp[i]),43);if (rc<0) return rc;}
    return 0;
}
int howaw_draw_tinted(const vita2d_texture *t,const tint_vertex *v,unsigned int n,int add) {
    if (!t || !n || n>270 || n%3) return -42;
    int rc=tint_init();if (rc<0) return rc;
    void *vertices=vertex_alloc(n*sizeof(*v));if (!vertices) return -2;memcpy(vertices,v,n*sizeof(*v));
    SceGxmContext *c=vita2d_get_context();sceGxmSetVertexProgram(c,tint_vp);sceGxmSetFragmentProgram(c,tint_fp[add!=0]);
    const float matrix[16]={2.f/960,0,0,0, 0,-2.f/544,0,0, 0,0,-1,0, -1,1,0,1};void *uniform=NULL;
    rc=checked(sceGxmReserveVertexDefaultUniformBuffer(c,&uniform),44);if (rc<0) return rc;
    rc=checked(sceGxmSetUniformDataF(uniform,tint_wvp,0,16,matrix),44);if (rc<0) return rc;
    rc=checked(sceGxmSetFragmentTexture(c,0,&t->gxm_tex),45);if (rc<0) return rc;
    rc=checked(sceGxmSetVertexStream(c,0,vertices),46);if (rc<0) return rc;
    rc=checked(sceGxmDraw(c,SCE_GXM_PRIMITIVE_TRIANGLES,SCE_GXM_INDEX_FORMAT_U16,vita2d_get_linear_indices(),n),3);pool_measure();return rc;
}
