//! The host returns an explicit error; it never impersonates a native GPU.
use super::geometry::{Vertex,ColorVertex};
use std::ffi::c_void;
pub struct Device;

#[cfg(target_os="vita")]
mod ffi {
    use super::*;
    extern "C" {
        pub fn howaw_graphics_init()->i32;
        pub fn howaw_depth_contract(result:*mut u32)->i32;
        pub fn howaw_depth_fini();
        pub fn howaw_viewport(x:f32,y:f32,w:f32,h:f32);
        pub fn howaw_gxm_error()->i32;
        pub fn howaw_gxm_error_api()->i32;
        pub fn howaw_gxm_draw_calls()->u32;
        pub fn howaw_texture_create(w:u32,h:u32,stride:*mut u32,mapped:*mut u32)->*mut c_void;
        pub fn howaw_draw_batch(t:*mut c_void,v:*const Vertex,n:u32,col:u32)->i32;
        pub fn howaw_draw_colors(v:*const ColorVertex,n:u32)->i32;
        pub fn vita2d_set_blend_mode_add(add:i32);
        pub fn howaw_finish_frame()->i32;
        pub fn vita2d_texture_get_datap(t:*mut c_void)->*mut u8;
        pub fn vita2d_free_texture(t:*mut c_void);
        pub fn vita2d_start_drawing();
        pub fn vita2d_end_drawing();
        pub fn vita2d_set_clear_color(col:u32);
        pub fn vita2d_clear_screen();
        pub fn vita2d_wait_rendering_done();
        pub fn vita2d_fini()->i32;
        pub fn vita2d_get_current_fb()->*const u8;
    }
}
fn unavailable()->String {"SERVICE_UNAVAILABLE/Graphics: requires physical Vita GXM".into()}
impl Device {
    pub fn new()->Result<Self,String> {
        #[cfg(target_os="vita")] unsafe {
            let rc=ffi::howaw_graphics_init();
            crate::diagnostic!("[graphics-init] libvita2d/GXM rc={} pool_bytes=262144 msaa=none",rc);
            if rc!=0 {return Err(format!("graphics init error={rc}"));}
            let device=Self;let mut result=[0u32;5];let start=std::time::Instant::now();
            let rc=ffi::howaw_depth_contract(result.as_mut_ptr());
            crate::diagnostic!("[depth-contract] rc={} pixels=1024 near_reject={} color_unchanged={} depth_words_changed={} far_accept={} gxm_draws={} elapsed_us={} presented=false",rc,result[0],result[1],result[2],result[3],result[4],start.elapsed().as_micros());
            if rc!=0 {return Err(format!("depth contract failed rc={rc} result={result:?}"));}
            device.check()?;Ok(device)
        }
        #[cfg(not(target_os="vita"))] {Err(unavailable())}
    }
    pub fn check(&self)->Result<(),String> {
        #[cfg(target_os="vita")] unsafe {
            let rc=ffi::howaw_gxm_error();
            if rc!=0 {Err(format!("GXM error={} api={}",rc,ffi::howaw_gxm_error_api()))}else{Ok(())}
        }
        #[cfg(not(target_os="vita"))] {Err(unavailable())}
    }
    pub fn texture(&self,w:u32,h:u32)->Result<(*mut c_void,usize,usize),String> {
        #[cfg(target_os="vita")] unsafe {
            let (mut stride,mut mapped)=(0,0);
            let p=ffi::howaw_texture_create(w,h,&mut stride,&mut mapped);
            self.check()?;
            if p.is_null() {return Err("GPU texture allocation failed".into());}
            Ok((p,stride as usize,mapped as usize))
        }
        #[cfg(not(target_os="vita"))] {let _=(w,h);Err(unavailable())}
    }
    /// Write to the mapped allocation without an intermediate atlas-sized buffer.
    pub fn upload(&self,p:*mut c_void,src:&[u8],xywh:[usize;4],stride:usize) {
        #[cfg(target_os="vita")] unsafe {
            let [x,y,w,h]=xywh;
            let dest=ffi::vita2d_texture_get_datap(p).add(y*stride+x*4);
            let dst=std::slice::from_raw_parts_mut(dest,(h-1)*stride+w*4);
            super::geometry::copy_bgra(src,dst,w,h,stride);
        }
        #[cfg(not(target_os="vita"))] {let _=(p,src,xywh,stride);panic!("{}",unavailable());}
    }
    pub fn begin(&self,colour:u32)->Result<(),String> {
        #[cfg(target_os="vita")] unsafe {ffi::vita2d_start_drawing();self.check()?;ffi::howaw_viewport(0.,0.,960.,544.);ffi::vita2d_set_clear_color(colour);ffi::vita2d_clear_screen();self.check()}
        #[cfg(not(target_os="vita"))] {let _=colour;Err(unavailable())}
    }
    pub fn draw(&self,p:*mut c_void,v:&[Vertex],col:u32)->Result<(),String> {
        #[cfg(target_os="vita")] unsafe {
            let rc=ffi::howaw_draw_batch(p,v.as_ptr(),v.len() as u32,col);
            if rc!=0 {return Err(format!("draw batch error={rc}"));}self.check()
        }
        #[cfg(not(target_os="vita"))] {let _=(p,v,col);Err(unavailable())}
    }
    pub fn present(&self)->Result<(),String> {
        #[cfg(target_os="vita")] unsafe {
            let rc=ffi::howaw_finish_frame();
            if rc!=0 {return Err(format!("finish/present error={rc}"));}self.check()
        }
        #[cfg(not(target_os="vita"))] {Err(unavailable())}
    }
    pub fn colors(&self,v:&[ColorVertex])->Result<(),String> {
        #[cfg(target_os="vita")] unsafe {let rc=ffi::howaw_draw_colors(v.as_ptr(),v.len() as u32);if rc!=0 {return Err(format!("color batch error={rc}"));}self.check()}
        #[cfg(not(target_os="vita"))] {let _=v;Err(unavailable())}
    }
    pub fn blend(&self,add:bool)->Result<(),String> {
        #[cfg(target_os="vita")] unsafe {ffi::vita2d_set_blend_mode_add(i32::from(add));self.check()}
        #[cfg(not(target_os="vita"))] {let _=add;Err(unavailable())}
    }
    pub fn viewport(&self,x:f32,y:f32,w:f32,h:f32)->Result<(),String> {
        #[cfg(target_os="vita")] unsafe {ffi::howaw_viewport(x,y,w,h);self.check()}
        #[cfg(not(target_os="vita"))] {let _=(x,y,w,h);Err(unavailable())}
    }
    pub fn wait(&self) {#[cfg(target_os="vita")] unsafe {ffi::vita2d_wait_rendering_done();}}
    pub fn end_without_present(&self)->Result<(),String> {
        #[cfg(target_os="vita")] unsafe {ffi::vita2d_end_drawing();self.check()}
        #[cfg(not(target_os="vita"))] {Err(unavailable())}
    }
    pub fn free(&self,p:*mut c_void) {#[cfg(target_os="vita")] unsafe {ffi::vita2d_free_texture(p);} #[cfg(not(target_os="vita"))] {let _=p;}}
}
impl Drop for Device {fn drop(&mut self) {#[cfg(target_os="vita")] unsafe {ffi::vita2d_wait_rendering_done();ffi::howaw_depth_fini();ffi::vita2d_fini();}}}

pub fn readback(clear:u32)->Result<(),String> {
    capture(clear,true)
}
/// Frame zero may legitimately be black (the original fade). Record actual
/// pixels without promoting an empty image into evidence of a visible menu.
pub fn inspect_original_frame()->Result<(),String> {capture(0xff000000,false)}
fn capture(clear:u32,require_change:bool)->Result<(),String> {
    #[cfg(target_os="vita")] unsafe {
        let p=ffi::vita2d_get_current_fb();
        if p.is_null(){return Err("framebuffer pointer unavailable".into());}
        let bytes=std::slice::from_raw_parts(p,960*544*4);
        let changed=bytes.chunks_exact(4).filter(|p|u32::from_le_bytes([p[0],p[1],p[2],p[3]])&0xffffff!=clear&0xffffff).count();
        crate::diagnostic!("[gpu-readback] rgba_bytes={} changed_rgb_pixels={} sha256={} gxm_draw_calls={}; display observation separate",bytes.len(),changed,crate::probe_sha256::digest(bytes),ffi::howaw_gxm_draw_calls());
        if changed==0 && require_change {return Err("GPU readback contains only clear colour".into());} Ok(())
    }
    #[cfg(not(target_os="vita"))] {let _=(clear,require_change);Err(unavailable())}
}
