/* SDK structures stay on the C side; Rust receives a small stable ABI. */
#include <psp2/ctrl.h>
#include <psp2/touch.h>
#include <stdint.h>
static SceTouchPanelInfo panel;
int howaw_input_init(void) {
    int rc=sceCtrlSetSamplingMode(SCE_CTRL_MODE_ANALOG);
    if (rc<0) return rc;
    rc=sceTouchGetPanelInfo(SCE_TOUCH_PORT_FRONT,&panel);if (rc<0) return rc;
    if (panel.maxDispX<=panel.minDispX || panel.maxDispY<=panel.minDispY) return -1;
    rc=sceTouchSetSamplingState(SCE_TOUCH_PORT_FRONT,SCE_TOUCH_SAMPLING_STATE_START);if (rc<0) return rc;
    SceTouchData first={0};rc=sceTouchRead(SCE_TOUCH_PORT_FRONT,&first,1);
    return rc==1?0:(rc<0?rc:-5);
}
int howaw_input_sample(uint32_t out[10]) {
    SceCtrlData pad={0};SceTouchData touch={0};
    int rc=sceCtrlPeekBufferPositive(0,&pad,1);if (rc!=1) return rc<0?rc:-2;
    if (pad.buttons&SCE_CTRL_INTERCEPTED) return -3;
    rc=sceTouchPeek(SCE_TOUCH_PORT_FRONT,&touch,1);if (rc!=1) return rc<0?rc:-4;
    out[0]=pad.buttons;out[1]=pad.lx;out[2]=pad.ly;out[3]=pad.rx;out[4]=pad.ry;
    out[5]=touch.reportNum;
    if (touch.reportNum) {
        out[6]=(uint32_t)(int32_t)touch.report[0].x;out[7]=(uint32_t)(int32_t)touch.report[0].y;
    }
    out[8]=((uint32_t)(uint16_t)panel.minDispX<<16)|(uint16_t)panel.maxDispX;
    out[9]=((uint32_t)(uint16_t)panel.minDispY<<16)|(uint16_t)panel.maxDispY;
    return 0;
}
