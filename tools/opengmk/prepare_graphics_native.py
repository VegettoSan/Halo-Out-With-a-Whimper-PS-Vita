#!/usr/bin/env python3
"""Build the E020 bridge and copy required SDK archives into NEW ignored output.

Windows rustc must see native archives while using the WSL linker. Toolchains
are read only; no installation, shader compiler, vitaGL or game data is used.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
from vita_wsl_link import translate

LIBS=['vita2d','SceGxm_stub','SceDisplay_stub','SceCommonDialog_stub','SceAppMgr_stub','SceSysmodule_stub']
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--sdk',default='/usr/local/vitasdk-hardfp');p.add_argument('--distro',default='Ubuntu');p.add_argument('--input',action='store_true');p.add_argument('--audio',action='store_true');a=p.parse_args()
    root=Path(__file__).resolve().parents[2];out=a.output.resolve()
    if not out.is_relative_to(root/'build') or out.exists():p.error('NEW ignored build/ output required')
    out.mkdir(parents=True);commands=[]
    def run(*args):
        cmd=['wsl','-d',a.distro,'--exec',*args];commands.append(cmd)
        return subprocess.check_output(cmd,stderr=subprocess.STDOUT,text=True)
    source=Path(__file__).with_name('graphics')/'vita2d_bridge.c'
    version=run(a.sdk+'/bin/arm-vita-eabi-gcc','--version').splitlines()[0]
    run(a.sdk+'/bin/arm-vita-eabi-gcc','-mfloat-abi=hard','-std=c11','-O2','-Wall','-Wextra','-Werror','-c',translate(str(source.resolve())),'-o',translate(str(out/'vita2d_bridge.o')))
    objects=[out/'vita2d_bridge.o'];libs=LIBS.copy()
    # Reuse only the two cached, zlib-licensed SDL GXM programs. Never link SDL
    # code or import game resources; keep extracted binary material ignored.
    cmd=['wsl','-d',a.distro,'--exec',a.sdk+'/bin/arm-vita-eabi-ar','p',a.sdk+'/arm-vita-eabi/lib/libSDL2.a','SDL_render_vita_gxm_tools.c.obj'];commands.append(cmd)
    (out/'sdl_shader_source.o').write_bytes(subprocess.check_output(cmd))
    run(a.sdk+'/bin/arm-vita-eabi-objcopy','--only-section=.rodata','--globalize-symbol=gxm_shader_texture_v','--globalize-symbol=gxm_shader_texture_f',translate(str(out/'sdl_shader_source.o')),translate(str(out/'sdl_shader_rodata.o')))
    objects.append(out/'sdl_shader_rodata.o')
    if a.input:
        input_source=Path(__file__).with_name('input')/'vita_input.c'
        run(a.sdk+'/bin/arm-vita-eabi-gcc','-mfloat-abi=hard','-std=c11','-O2','-Wall','-Wextra','-Werror','-c',translate(str(input_source.resolve())),'-o',translate(str(out/'vita_input.o')))
        objects.append(out/'vita_input.o');libs+=['SceCtrl_stub','SceTouch_stub']
    run(a.sdk+'/bin/arm-vita-eabi-ar','rcs',translate(str(out/'libhowaw_graphics.a')),*[translate(str(p)) for p in objects])
    if a.audio:libs+=['SceAudio_stub']
    for lib in libs:
        run('cp',a.sdk+'/arm-vita-eabi/lib/lib'+lib+'.a',translate(str(out/('lib'+lib+'.a'))))
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.a')}
    manifest={'utc':datetime.now(timezone.utc).isoformat(),'gcc':version,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'archives_sha256':hashes,'commands':commands,'result':'PASS compile/archive; device execution UNTESTED'}
    manifest.update(tint_source_sha256=hashlib.sha256(source.with_name('vertex_tint.c').read_bytes()).hexdigest(),sdl_shader_rodata_sha256=hashlib.sha256((out/'sdl_shader_rodata.o').read_bytes()).hexdigest())
    (out/'native-build.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('PASS hard-float C bridge (-Werror), required SDK archives copied; set HOWAW_GRAPHICS_LIB_DIR to output')
if __name__=='__main__':main()
