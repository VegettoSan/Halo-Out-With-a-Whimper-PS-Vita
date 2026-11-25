#!/usr/bin/env python3
"""Use existing WSL VitaSDK ar for cc-rs; paths translated without a shell."""
import os,subprocess,sys
from vita_wsl_link import translate
if __name__=='__main__':
    sdk=os.environ.get('VITA_WSL_SDK','/usr/local/vitasdk-hardfp')
    raise SystemExit(subprocess.call(['wsl','-d',os.environ.get('VITA_WSL_DISTRO','Ubuntu'),'--exec',sdk+'/bin/arm-vita-eabi-ar',*map(translate,sys.argv[1:])]))
