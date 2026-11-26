//! Initial RendererTrait implementation. Unsupported operations stop explicitly.
use super::*;
#[path="geometry.rs"] pub mod geometry;
#[path="native.rs"] mod native;
#[path="residency.rs"] mod residency;
use std::ffi::c_void;
use geometry::Vertex;
static FILL_DISPLAY:std::sync::atomic::AtomicBool=std::sync::atomic::AtomicBool::new(false);
static RAM_UPLOAD:std::sync::atomic::AtomicBool=std::sync::atomic::AtomicBool::new(false);
pub fn set_display_fill(fill:bool) {FILL_DISPLAY.store(fill,std::sync::atomic::Ordering::Relaxed);}
pub fn display_fill()->bool {FILL_DISPLAY.load(std::sync::atomic::Ordering::Relaxed)}
pub fn take_ram_upload()->bool {RAM_UPLOAD.swap(false,std::sync::atomic::Ordering::Relaxed)}

struct Entry {rect:AtlasRect,pixels:Option<Box<[u8]>>}
struct Page {w:i32,h:i32,texture:*mut c_void,mapped:usize,main_ram:bool}
pub struct Vita2d {
    entries:Vec<Entry>, pages:Vec<Page>, device:Option<native::Device>,
    vertices:Vec<Vertex>, key:Option<(usize,u32)>, in_scene:bool,
    draws:u64, sprites:u64, uploads:u64, frames:u64, released:usize,
    view_scale:f64, view_y_scale:f64, view_offset:[f64;2], colors:Vec<geometry::ColorVertex>, add:bool, rectangles:u64, logical:[u32;2],
}
impl Vita2d {
    pub fn from_atlases(atl:atlas::AtlasBuilder)->Self {
        let (packers,textures)=atl.into_inner();
        let pages=packers.iter().map(|p|{let (w,h)=p.size();Page{w,h,texture:std::ptr::null_mut(),mapped:0,main_ram:false}}).collect();
        let this=Self {entries:textures.into_iter().map(|(rect,pixels)|Entry{rect,pixels:Some(pixels)}).collect(),pages,
            device:None,vertices:Vec::with_capacity(1536),key:None,in_scene:false,draws:0,sprites:0,uploads:0,frames:0,released:0,view_scale:1.,view_y_scale:1.,view_offset:[0.,0.],colors:Vec::with_capacity(1536),add:false,rectangles:0,logical:[960,544]};
        this.metrics("prepared");this
    }
    pub fn metrics(&self,stage:&str) {
        let pending:usize=self.entries.iter().filter_map(|e|e.pixels.as_ref()).map(|p|p.len()).sum();
        let mapped:usize=self.pages.iter().map(|p|p.mapped).sum();
        let main:usize=self.pages.iter().filter(|p|p.main_ram).map(|p|p.mapped).sum();
        crate::diagnostic!("[atlas-pools] stage={} cdram_bytes={} main_ram_gpu_bytes={} total_bytes={}",stage,mapped-main,main,mapped);
        crate::diagnostic!("[graphics-memory] stage={} entries={} pages={} cpu_pending_bytes={} cpu_released_bytes={} gpu_texture_mapped_bytes={} page_uploads={} sprite_submissions={} rectangle_submissions={} queued_texture_vertices={} queued_color_vertices={} batch_draws={} frames={}",
            stage,self.entries.len(),self.pages.len(),pending,self.released,mapped,self.uploads,self.sprites,self.rectangles,self.vertices.len(),self.colors.len(),self.draws,self.frames);
    }
    pub fn resource(&self,id:AtlasRef)->Result<(),String> {
        let e=self.entries.get(usize::try_from(id.0).map_err(|_|"invalid texture id")?).ok_or("texture id absent")?;
        let p=e.pixels.as_ref().ok_or("CPU pixels already released")?;
        let alpha=p.chunks_exact(4).filter(|p|p[3]<255).count();
        crate::diagnostic!("[authentic-resource] atlas_ref={} page={} width={} height={} bgra_bytes={} nonopaque_pixels={} bgra_sha256={}",id.0,e.rect.atlas_id,e.rect.w,e.rect.h,p.len(),alpha,crate::probe_sha256::digest(p));
        Ok(())
    }
    fn resident(&mut self,page:usize)->Result<(),String> {
        if !self.pages[page].texture.is_null(){return Ok(());}
        crate::diagnostic!("[atlas-residency-request] page={} resident={:?}",page,self.pages.iter().enumerate().filter(|(_,p)|!p.texture.is_null()).map(|(i,_)|i).collect::<Vec<_>>());
        if self.device.is_none(){self.device=Some(native::Device::new()?);crate::diagnostics::native_memory("gxm_initialized");}
        // Keep all CPU payloads until allocation and validation succeed; never upload a page twice.
        let p=&self.pages[page];
        let cdram:usize=self.pages.iter().filter(|p|!p.main_ram).map(|p|p.mapped).sum();
        let main:usize=self.pages.iter().filter(|p|p.main_ram).map(|p|p.mapped).sum();
        let bytes=(p.w as usize*4+31)/32*32*p.h as usize;
        let main_ram=residency::main_ram_for(cdram,main,bytes)?;
        for e in self.entries.iter().filter(|e|e.rect.atlas_id as usize==page) {
            let r=e.rect;
            if r.x<0 || r.y<0 || r.w<=0 || r.h<=0 || r.x+r.w>p.w || r.y+r.h>p.h || e.pixels.as_ref().map(|x|x.len())!=Some(r.w as usize*r.h as usize*4) {
                return Err("invalid atlas bounds or BGRA payload".into());
            }
        }
        let device=self.device.as_ref().unwrap();
        let start=std::time::Instant::now();
        let (texture,stride,mapped)=device.texture(p.w as u32,p.h as u32,main_ram)?;
        if stride<p.w as usize*4 || mapped<stride*p.h as usize {device.free(texture);return Err("GPU stride/allocation bounds invalid".into());}
        if !residency::fits(cdram,main,mapped,main_ram) {device.free(texture);return Err("actual mapped atlas allocation exceeds pool budget".into());}
        for e in self.entries.iter().filter(|e|e.rect.atlas_id as usize==page) {
            let r=e.rect;device.upload(texture,e.pixels.as_ref().unwrap(),[r.x as _,r.y as _,r.w as _,r.h as _],stride);
        }
        for e in self.entries.iter_mut().filter(|e|e.rect.atlas_id as usize==page) {
            self.released+=e.pixels.take().unwrap().len();
        }
        self.pages[page].texture=texture;self.pages[page].mapped=mapped;self.pages[page].main_ram=main_ram;self.uploads+=1;
        if main_ram {RAM_UPLOAD.store(true,std::sync::atomic::Ordering::Relaxed);}
        crate::diagnostic!("[atlas-upload] page={} pool={} mapped_bytes={} elapsed_us={} duplicate_copy=false",page,if main_ram{"main_uncached"}else{"cdram"},mapped,start.elapsed().as_micros());
        self.metrics("page_uploaded");crate::heap_meter::snapshot("page_uploaded");crate::diagnostics::native_memory("page_uploaded");Ok(())
    }
    fn flush(&mut self)->Result<(),String> {
        if self.vertices.is_empty() && self.colors.is_empty(){return Ok(());}
        if !self.in_scene{return Err("draw batch outside scene".into());}
        if !self.colors.is_empty() {
            self.device.as_ref().unwrap().colors(&self.colors)?;self.colors.clear();self.draws+=1;
            return Ok(());
        }
        let (page,col)=self.key.unwrap();
        self.device.as_ref().unwrap().draw(self.pages[page].texture,&self.vertices,col)?;
        self.draws+=1;self.vertices.clear();Ok(())
    }
    fn checked(result:Result<(),String>) {if let Err(e)=result{crate::diagnostic!("GRAPHICS_FAIL {}",e);panic!("GRAPHICS_FAIL {}",e);}}
    fn queue_sprite(&mut self,v:&mut [Vertex],key:(usize,u32)) {
        if self.key!=Some(key) || self.vertices.len()+v.len()>1536 {Self::checked(self.flush());self.key=Some(key);}
        for v in v.iter_mut() {v.x=(v.x as f64*self.view_scale+self.view_offset[0]) as f32;v.y=(v.y as f64*self.view_y_scale+self.view_offset[1]) as f32;}
        self.vertices.extend_from_slice(v);
    }
}
impl Drop for Vita2d {
    fn drop(&mut self) {
        if let Some(d)=self.device.as_ref(){
            if self.in_scene {crate::diagnostic!("[graphics-cleanup] end unpresented scene result={:?}",d.end_without_present());}
            d.wait();for p in &self.pages {if !p.texture.is_null(){d.free(p.texture);}}
        }
    }
}

impl RendererTrait for Vita2d {
    fn as_any(&self)->&dyn Any {self}
    fn max_texture_size(&self)->u32 {2048}
    // Same guard as upstream OpenGL: the original 2D menu has no depth clear.
    // Enabling 3D remains unavailable until its matrices/states are implemented.
    fn clear_zbuf(&mut self) {crate::diagnostic!("[graphics-depth] clear_zbuf using_3d=false gpu_clear=false (original 2D contract)");}
    fn get_3d(&self)->bool {false}
    fn set_3d(&mut self,enabled:bool) {if enabled {crate::host::unavailable(crate::host::Service::Graphics,"set_3d");}}
    fn get_depth(&self)->f32 {0.}
    fn set_depth(&mut self,depth:f32) {let _=depth; /* upstream forces zero outside 3D */}
    fn get_depth_test(&self)->bool {false}
    fn set_depth_test(&mut self,enabled:bool) {let _=enabled; /* upstream masks with using_3d */}
    fn get_rect(&self,id:AtlasRef)->Option<&AtlasRect> {usize::try_from(id.0).ok().and_then(|i|self.entries.get(i)).map(|e|&e.rect)}
    fn get_blend_mode(&self)->(BlendType,BlendType) {(BlendType::SrcAlpha,if self.add{BlendType::One}else{BlendType::InvSrcAlpha})}
    fn set_blend_mode(&mut self,src:BlendType,dst:BlendType) {
        if src!=BlendType::SrcAlpha || !matches!(dst,BlendType::One|BlendType::InvSrcAlpha) {crate::host::unavailable(crate::host::Service::Graphics,"blend_factors");}
        Self::checked(self.flush());let add=dst==BlendType::One;
        if let Some(d)=&self.device {Self::checked(d.blend(add));}
        self.add=add;crate::diagnostic!("[graphics-blend] src={:?} dst={:?}",src,dst);
    }
    fn draw_rectangle(&mut self,x1:f64,y1:f64,x2:f64,y2:f64,colour:i32,alpha:f64) {self.draw_rectangle_gradient(x1,y1,x2,y2,colour,colour,colour,colour,alpha,false);}
    fn draw_rectangle_outline(&mut self,x1:f64,y1:f64,x2:f64,y2:f64,colour:i32,alpha:f64) {self.draw_rectangle_gradient(x1,y1,x2,y2,colour,colour,colour,colour,alpha,true);}
    fn draw_rectangle_gradient(&mut self,x1:f64,y1:f64,x2:f64,y2:f64,c1:i32,c2:i32,c3:i32,c4:i32,alpha:f64,outline:bool) {
        if ![x1,y1,x2,y2,alpha].iter().all(|v|v.is_finite()) {panic!("GRAPHICS_FAIL nonfinite rectangle");}
        if !self.in_scene {panic!("GRAPHICS_FAIL rectangle outside scene");}
        if outline {
            Self::checked(self.flush());let mut v=geometry::rectangle_outline(x1,y1,x2,y2,[c1,c2,c3,c4],alpha);
            for v in &mut v {v.x=(f64::from(v.x)*self.view_scale+self.view_offset[0]) as f32;v.y=(f64::from(v.y)*self.view_y_scale+self.view_offset[1]) as f32;}
            Self::checked(self.device.as_ref().unwrap().lines(&v));self.draws+=1;self.rectangles+=1;
            {static ONCE:std::sync::atomic::AtomicBool=std::sync::atomic::AtomicBool::new(false);if !ONCE.swap(true,std::sync::atomic::Ordering::Relaxed) {crate::diagnostic!("[graphics-outline] closed=true vertices=8 native_line_width=1; scaled raster parity unverified");}}
            return;
        }
        if !self.vertices.is_empty() || self.colors.len()+6>1536 {Self::checked(self.flush());}
        let mut v=geometry::rectangle(x1,y1,x2,y2,[c1,c2,c3,c4],alpha);
        for v in &mut v {v.x=(f64::from(v.x)*self.view_scale+self.view_offset[0]) as f32;v.y=(f64::from(v.y)*self.view_y_scale+self.view_offset[1]) as f32;}
        self.colors.extend_from_slice(&v);self.rectangles+=1;
        if self.rectangles<=3 {crate::diagnostic!("[graphics-rectangle] submission={} gradient={} alpha={}",self.rectangles,c1!=c2 || c1!=c3 || c1!=c4,alpha);}
    }
    fn draw_sprite_general(&mut self,texture:AtlasRef,part_x:f64,part_y:f64,part_w:f64,part_h:f64,
        x:f64,y:f64,xscale:f64,yscale:f64,angle:f64,col1:i32,col2:i32,col3:i32,col4:i32,alpha:f64,use_origin:bool) {
        if col1!=col2 || col1!=col3 || col1!=col4 {crate::host::unavailable(crate::host::Service::Graphics,"per_vertex_tint");}
        let Some(r)=self.get_rect(texture).copied() else{return;};
        if ![part_x,part_y,part_w,part_h,x,y,xscale,yscale,angle,alpha].iter().all(|x|x.is_finite()) {panic!("GRAPHICS_FAIL nonfinite sprite");}
        if !self.in_scene {panic!("GRAPHICS_FAIL draw_sprite without clear_view/begin");}
        if !self.colors.is_empty() {Self::checked(self.flush());}
        let page=r.atlas_id as usize;Self::checked(self.resident(page));
        let key=(page,geometry::tint(col1,alpha));
        let origin=if use_origin{[r.origin_x as f64,r.origin_y as f64]}else{[0.,0.]};
        let p=&self.pages[page];
        let atlas=[r.x as f64,r.y as f64,p.w as f64,p.h as f64];let part=[part_x,part_y,part_w,part_h];
        if part_x<0. || part_y<0. || part_w<0. || part_h<0. || part_x+part_w>r.w as f64 || part_y+part_h>r.h as f64 {
            let (mut v,n)=geometry::clamped_quads(origin,part,[x,y],[xscale,yscale],angle,atlas,[r.w as f64,r.h as f64]);
            {static COUNT:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);if COUNT.fetch_add(1,std::sync::atomic::Ordering::Relaxed)<3 {crate::diagnostic!("[graphics-sprite-clamp] atlas_ref={} sprite={}x{} part={:?} vertices={} edge_pixels=true",texture.0,r.w,r.h,part,n);}}
            self.queue_sprite(&mut v[..n],key);
        } else {let mut v=geometry::quad(origin,part,[x,y],[xscale,yscale],angle,atlas);self.queue_sprite(&mut v,key);}
        self.sprites+=1;
        if self.sprites<=3 {crate::diagnostic!("[graphics-sprite] submission={} atlas_ref={} page={} alpha={}",self.sprites,texture.0,page,alpha);}
    }
    fn set_view(&mut self,src_x:i32,src_y:i32,src_w:i32,src_h:i32,src_angle:f64,port_x:i32,port_y:i32,port_w:i32,port_h:i32) {
        // First original menu: one full-frame axis-aligned view. Other views stay explicit.
        if port_x!=0 || port_y!=0 || src_angle!=0. || src_w!=port_w || src_h!=port_h || src_w<=0 || src_h<=0 {
            crate::diagnostic!("[unsupported-view] source={},{},{},{} angle={} port={},{},{},{}",src_x,src_y,src_w,src_h,src_angle,port_x,port_y,port_w,port_h);
            crate::host::unavailable(crate::host::Service::Graphics,"subview_or_rotated_view");
        }
        Self::checked(self.flush());
        let port=geometry::display_port(src_w as u32,src_h as u32,display_fill());
        // Normalize into libvita2d's fixed shader coordinate domain, then use
        // a real GXM viewport. Clip-space clipping now bounds tiled backgrounds
        // to the original view without extra stencil draws or atlas copies.
        let shader=geometry::shader_view(src_w as u32,src_h as u32);
        self.view_scale=shader[0];self.view_y_scale=shader[1];self.view_offset=[-f64::from(src_x)*shader[0],-f64::from(src_y)*shader[1]];self.logical=[src_w as u32,src_h as u32];
        Self::checked(self.device.as_ref().expect("view requires active device").viewport(port[0] as f32,port[1] as f32,port[2] as f32,port[3] as f32));
        crate::diagnostic!("[graphics-view] source={},{},{}x{} physical_port={:?} fill={}",src_x,src_y,src_w,src_h,port,display_fill());
    }
    fn clear_view(&mut self,colour:Colour,alpha:f64) {
        if self.in_scene {
            Self::checked(self.flush());Self::checked(self.device.as_ref().unwrap().clear(geometry::tint(colour.as_decimal() as i32,alpha)));
            crate::diagnostic!("[graphics-clear] existing_scene=true color_and_depth=true viewport_preserved=true");return;
        }
        if self.device.is_none(){self.device=Some(native::Device::new().unwrap_or_else(|e|panic!("GRAPHICS_FAIL {}",e)));crate::diagnostics::native_memory("gxm_initialized");}
        Self::checked(self.device.as_ref().unwrap().begin(geometry::tint(colour.as_decimal() as i32,alpha)));self.in_scene=true;
        Self::checked(self.device.as_ref().unwrap().blend(self.add));
    }
    fn flush_queue(&mut self) {Self::checked(self.flush());}
    fn present(&mut self,window_width:u32,window_height:u32,scaling:Scaling) {
        // Vita's physical display is fixed. The original logical full-frame view
        // is already aspect-mapped by set_view; accept its unchanged 1x policy.
        if [window_width,window_height]!=self.logical || !matches!(scaling,Scaling::Fixed(1.)|Scaling::Full|Scaling::Aspect(_)) {
            crate::host::unavailable(crate::host::Service::Graphics,"presentation_scaling");
        }
        Self::checked(self.flush());
        if !self.in_scene {panic!("GRAPHICS_FAIL present outside scene");}
        Self::checked(self.device.as_ref().unwrap().present());self.in_scene=false;self.frames+=1;
    }
    // REQUIRED_UNSUPPORTED
}

impl Renderer {
    pub fn graphics_resource(&self,id:AtlasRef)->Result<(),String> {self.0.as_any().downcast_ref::<Vita2d>().ok_or("wrong renderer")?.resource(id)}
    pub fn graphics_metrics(&self,stage:&str) {self.0.as_any().downcast_ref::<Vita2d>().expect("Vita2d renderer").metrics(stage);}
}
pub fn readback(clear:u32)->Result<(),String> {native::readback(clear)}
pub fn inspect_original_frame()->Result<(),String> {native::inspect_original_frame()}
