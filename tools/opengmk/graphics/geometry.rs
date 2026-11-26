//! CPU geometry shared by the real backend and bounded contract tests.
#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct Vertex { pub x:f32, pub y:f32, pub z:f32, pub u:f32, pub v:f32 }
#[repr(C)]
#[derive(Clone,Copy,Debug,Default)]
pub struct ColorVertex {pub x:f32,pub y:f32,pub z:f32,pub color:u32}

pub fn rectangle(x1:f64,y1:f64,x2:f64,y2:f64,colors:[i32;4],alpha:f64)->[ColorVertex;6] {
    let (left,right)=(x1.min(x2),x1.max(x2));let (top,bottom)=(y1.min(y2),y1.max(y2));
    let right=if right==right.floor(){right+0.01}else{right};
    let bottom=if bottom==bottom.floor(){bottom+0.01}else{bottom};
    let v=[(left,top),(right,top),(right,bottom),(left,bottom)].map(|(x,y)|ColorVertex{x:x as f32,y:y as f32,z:0.5,color:0});
    let v=std::array::from_fn::<_,4,_>(|i|ColorVertex{color:tint(colors[i],alpha),..v[i]});
    [v[0],v[1],v[2],v[0],v[2],v[3]]
}

pub fn aspect_view(w:u32,h:u32)->(f64,[f64;2]) {
    assert!(w>0 && h>0);
    let scale=(960.0/w as f64).min(544.0/h as f64);
    (scale,[(960.-w as f64*scale)/2.,(544.-h as f64*scale)/2.])
}
pub fn shader_view(w:u32,h:u32)->[f64;2] {assert!(w>0 && h>0);[960./w as f64,544./h as f64]}
pub fn display_port(w:u32,h:u32,fill:bool)->[f64;4] {
    if fill {[0.,0.,960.,544.]}else{let(s,o)=aspect_view(w,h);[o[0],o[1],w as f64*s,h as f64*s]}
}

pub fn tint(col:i32, alpha:f64)->u32 {
    (col as u32 & 0xffffff) | (((alpha.clamp(0.0,1.0)*255.0) as u32)<<24)
}

/// OpenGMK's GM8 convention: negative screen-space angle and -0.5 pixel offset.
pub fn quad(origin:[f64;2], part:[f64;4], position:[f64;2], scale:[f64;2],
            angle:f64, atlas:[f64;4])->[Vertex;6] {
    let [px,py,pw,ph]=part;
    let [ax,ay,aw,ah]=atlas;
    let (sin,cos)=(-angle.to_radians()).sin_cos();
    let left=-pw*scale[0]*origin[0]-0.5;
    let top=-ph*scale[1]*origin[1]-0.5;
    let corners=[(left,top,px,py),(left+pw*scale[0],top,px+pw,py),
        (left+pw*scale[0],top+ph*scale[1],px+pw,py+ph),(left,top+ph*scale[1],px,py+ph)];
    let v=corners.map(|(x,y,u,v)| Vertex {x:(position[0]+x*cos-y*sin) as f32,
        y:(position[1]+y*cos+x*sin) as f32,z:0.5,u:((ax+u)/aw) as f32,v:((ay+v)/ah) as f32});
    [v[0],v[1],v[2],v[0],v[2],v[3]]
}

/// Copy directly into mapped GPU memory. Source OpenGMK pixels are BGRA.
pub fn copy_bgra(src:&[u8], dst:&mut [u8], width:usize, height:usize, stride:usize) {
    assert_eq!(src.len(),width*height*4);
    assert!(stride>=width*4 && dst.len()>=(height-1)*stride+width*4);
    for (s,d) in src.chunks_exact(width*4).zip(dst.chunks_mut(stride)) {
        for (s,d) in s.chunks_exact(4).zip(d.chunks_exact_mut(4)) { d.copy_from_slice(&[s[2],s[1],s[0],s[3]]); }
    }
}

#[cfg(test)] mod tests {
    use super::*;
    #[test] fn fill_and_camera_translation_preserve_logical_coordinates() {
        assert_eq!(display_port(640,325,true),[0.,0.,960.,544.]);
        assert_eq!(display_port(640,325,false),[0.,28.25,960.,487.5]);
        let shader=shader_view(640,325);let camera=[120.,45.];let world=[240.,85.];
        let normalized=[(world[0]-camera[0])*shader[0]/960.,(world[1]-camera[1])*shader[1]/544.];
        assert!((normalized[0]-120./640.).abs()<1e-10 && (normalized[1]-40./325.).abs()<1e-10);
    }
    #[test] fn viewport_shader_domain_preserves_mapping_and_clip_bounds() {
        let (scale,offset)=aspect_view(640,325);let shader=shader_view(640,325);
        for (x,y) in [(0.,0.),(640.,325.),(123.,57.)] {
            let screen_x=(x*shader[0]/960.)*(640.*scale)+offset[0];
            let screen_y=(y*shader[1]/544.)*(325.*scale)+offset[1];
            assert!((screen_x-(x*scale+offset[0])).abs()<1e-10);
            assert!((screen_y-(y*scale+offset[1])).abs()<1e-10);
        }
        assert_eq!(640.*shader[0],960.);assert_eq!(325.*shader[1],544.);
        assert!(-1.*shader[1]<0. && 326.*shader[1]>544.);
    }
    #[test] fn gradient_rectangle_sort_and_fan() {
        let v=rectangle(20.,30.,10.,5.,[1,2,3,4],0.5);
        assert_eq!((v[0].x,v[0].y,v[0].color),(10.,5.,0x7f000001));
        assert_eq!((v[2].x,v[2].y,v[2].color),(20.01,30.01,0x7f000003));
        assert_eq!((v[3].color,v[4].color,v[5].color),(v[0].color,v[2].color,0x7f000004));
    }
    #[test] fn original_menu_view_fits_display() {
        let (scale,offset)=aspect_view(640,325);
        assert_eq!(scale,1.5);assert_eq!(offset,[0.,28.25]);
        assert_eq!(aspect_view(960,544),(1.,[0.,0.]));
    }
    #[test] fn crop_origin_rotation_and_mirror() {
        let v=quad([0.5,0.5],[2.,3.,10.,20.],[100.,100.],[-2.,1.],90.,[32.,64.,256.,256.]);
        assert!((v[0].x-89.5).abs()<0.001 && (v[0].y-90.5).abs()<0.001);
        assert!((v[1].y-110.5).abs()<0.001);
        assert_eq!((v[0].u,v[0].v),(34./256.,67./256.));
        assert_eq!((v[2].u,v[2].v),(44./256.,87./256.));
    }
    #[test] fn bgra_stride_alpha_and_padding() {
        let mut d=[0x7f;24];
        copy_bgra(&[1,2,3,4,5,6,7,0,8,9,10,255,11,12,13,128],&mut d,2,2,12);
        assert_eq!(&d[..8],&[3,2,1,4,7,6,5,0]);
        assert_eq!(&d[12..20],&[10,9,8,255,13,12,11,128]);
        assert_eq!(&d[8..12],&[0x7f;4]);
        assert_eq!(&d[20..],&[0x7f;4]);
        assert_eq!(tint(0x123456,0.5),0x7f123456);
    }
}
