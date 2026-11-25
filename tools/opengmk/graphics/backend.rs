//! Initial RendererTrait implementation. Unsupported operations stop explicitly.
use super::*;
#[path="geometry.rs"] pub mod geometry;
#[path="native.rs"] mod native;
use std::ffi::c_void;
use geometry::Vertex;

struct Entry {rect:AtlasRect,pixels:Option<Box<[u8]>>}
struct Page {w:i32,h:i32,texture:*mut c_void,mapped:usize}
pub struct Vita2d {
    entries:Vec<Entry>, pages:Vec<Page>, device:Option<native::Device>,
    vertices:Vec<Vertex>, key:Option<(usize,u32)>, in_scene:bool,
    draws:u64, sprites:u64, uploads:u64, frames:u64, released:usize,
    view_scale:f64, view_offset:[f64;2],
}
impl Vita2d {
    pub fn from_atlases(atl:atlas::AtlasBuilder)->Self {
        let (packers,textures)=atl.into_inner();
        let pages=packers.iter().map(|p|{let (w,h)=p.size();Page{w,h,texture:std::ptr::null_mut(),mapped:0}}).collect();
        let this=Self {entries:textures.into_iter().map(|(rect,pixels)|Entry{rect,pixels:Some(pixels)}).collect(),pages,
            device:None,vertices:Vec::with_capacity(1536),key:None,in_scene:false,draws:0,sprites:0,uploads:0,frames:0,released:0,view_scale:1.,view_offset:[0.,0.]};
        this.metrics("prepared");this
    }
    pub fn metrics(&self,stage:&str) {
        let pending:usize=self.entries.iter().filter_map(|e|e.pixels.as_ref()).map(|p|p.len()).sum();
        let mapped:usize=self.pages.iter().map(|p|p.mapped).sum();
        crate::diagnostic!("[graphics-memory] stage={} entries={} pages={} cpu_pending_bytes={} cpu_released_bytes={} gpu_texture_mapped_bytes={} page_uploads={} sprite_submissions={} batch_draws={} frames={}",
            stage,self.entries.len(),self.pages.len(),pending,self.released,mapped,self.uploads,self.sprites,self.draws,self.frames);
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
        if self.device.is_none(){self.device=Some(native::Device::new()?);crate::diagnostics::native_memory("gxm_initialized");}
        // Keep all CPU payloads until allocation and validation succeed; never upload a page twice.
        let p=&self.pages[page];
        for e in self.entries.iter().filter(|e|e.rect.atlas_id as usize==page) {
            let r=e.rect;
            if r.x<0 || r.y<0 || r.w<=0 || r.h<=0 || r.x+r.w>p.w || r.y+r.h>p.h || e.pixels.as_ref().map(|x|x.len())!=Some(r.w as usize*r.h as usize*4) {
                return Err("invalid atlas bounds or BGRA payload".into());
            }
        }
        let device=self.device.as_ref().unwrap();
        let (texture,stride,mapped)=device.texture(p.w as u32,p.h as u32)?;
        if stride<p.w as usize*4 || mapped<stride*p.h as usize {device.free(texture);return Err("GPU stride/allocation bounds invalid".into());}
        for e in self.entries.iter().filter(|e|e.rect.atlas_id as usize==page) {
            let r=e.rect;device.upload(texture,e.pixels.as_ref().unwrap(),[r.x as _,r.y as _,r.w as _,r.h as _],stride);
        }
        for e in self.entries.iter_mut().filter(|e|e.rect.atlas_id as usize==page) {
            self.released+=e.pixels.take().unwrap().len();
        }
        self.pages[page].texture=texture;self.pages[page].mapped=mapped;self.uploads+=1;
        self.metrics("page_uploaded");crate::heap_meter::snapshot("page_uploaded");crate::diagnostics::native_memory("page_uploaded");Ok(())
    }
    fn flush(&mut self)->Result<(),String> {
        if self.vertices.is_empty(){return Ok(());}
        if !self.in_scene{return Err("draw batch outside scene".into());}
        let (page,col)=self.key.unwrap();
        self.device.as_ref().unwrap().draw(self.pages[page].texture,&self.vertices,col)?;
        self.draws+=1;self.vertices.clear();Ok(())
    }
    fn checked(result:Result<(),String>) {if let Err(e)=result{crate::diagnostic!("GRAPHICS_FAIL {}",e);panic!("GRAPHICS_FAIL {}",e);}}
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
    fn get_rect(&self,id:AtlasRef)->Option<&AtlasRect> {usize::try_from(id.0).ok().and_then(|i|self.entries.get(i)).map(|e|&e.rect)}
    fn draw_sprite_general(&mut self,texture:AtlasRef,part_x:f64,part_y:f64,part_w:f64,part_h:f64,
        x:f64,y:f64,xscale:f64,yscale:f64,angle:f64,col1:i32,col2:i32,col3:i32,col4:i32,alpha:f64,use_origin:bool) {
        if col1!=col2 || col1!=col3 || col1!=col4 {crate::host::unavailable(crate::host::Service::Graphics,"per_vertex_tint");}
        let Some(r)=self.get_rect(texture).copied() else{return;};
        if ![part_x,part_y,part_w,part_h,x,y,xscale,yscale,angle,alpha].iter().all(|x|x.is_finite()) || part_x<0. || part_y<0. || part_w<0. || part_h<0. || part_x+part_w>r.w as f64 || part_y+part_h>r.h as f64 {
            crate::host::unavailable(crate::host::Service::Graphics,"sprite_crop_out_of_bounds");
        }
        if !self.in_scene {panic!("GRAPHICS_FAIL draw_sprite without clear_view/begin");}
        let page=r.atlas_id as usize;Self::checked(self.resident(page));
        let key=(page,geometry::tint(col1,alpha));
        if self.key!=Some(key) || self.vertices.len()+6>1536 {Self::checked(self.flush());self.key=Some(key);}
        let origin=if use_origin{[r.origin_x as f64,r.origin_y as f64]}else{[0.,0.]};
        let p=&self.pages[page];
        let mut quad=geometry::quad(origin,[part_x,part_y,part_w,part_h],[x,y],[xscale,yscale],angle,[r.x as f64,r.y as f64,p.w as f64,p.h as f64]);
        for v in &mut quad {v.x=(v.x as f64*self.view_scale+self.view_offset[0]) as f32;v.y=(v.y as f64*self.view_scale+self.view_offset[1]) as f32;}
        self.vertices.extend_from_slice(&quad);self.sprites+=1;
    }
    fn set_view(&mut self,src_x:i32,src_y:i32,src_w:i32,src_h:i32,src_angle:f64,port_x:i32,port_y:i32,port_w:i32,port_h:i32) {
        // First original menu: one full-frame axis-aligned view. Other views stay explicit.
        if src_x!=0 || src_y!=0 || port_x!=0 || port_y!=0 || src_angle!=0. || src_w!=port_w || src_h!=port_h || src_w<=0 || src_h<=0 {
            crate::host::unavailable(crate::host::Service::Graphics,"subview_or_rotated_view");
        }
        Self::checked(self.flush());
        let (scale,offset)=geometry::aspect_view(src_w as u32,src_h as u32);
        self.view_scale=scale;self.view_offset=offset;
        crate::diagnostic!("[graphics-view] logical={}x{} physical=960x544 scale={} offset={},{}; no GPU success implied",src_w,src_h,scale,offset[0],offset[1]);
    }
    fn clear_view(&mut self,colour:Colour,alpha:f64) {
        if self.in_scene {crate::host::unavailable(crate::host::Service::Graphics,"clear_inside_scene");}
        if self.device.is_none(){self.device=Some(native::Device::new().unwrap_or_else(|e|panic!("GRAPHICS_FAIL {}",e)));crate::diagnostics::native_memory("gxm_initialized");}
        Self::checked(self.device.as_ref().unwrap().begin(geometry::tint(colour.as_decimal() as i32,alpha)));self.in_scene=true;
    }
    fn flush_queue(&mut self) {Self::checked(self.flush());}
    fn present(&mut self,window_width:u32,window_height:u32,scaling:Scaling) {
        if window_width!=960 || window_height!=544 || !matches!(scaling,Scaling::Fixed(n) if n==1.) {
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
