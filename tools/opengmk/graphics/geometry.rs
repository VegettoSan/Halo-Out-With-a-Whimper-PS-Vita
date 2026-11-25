//! CPU geometry shared by the real backend and bounded contract tests.
#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct Vertex { pub x:f32, pub y:f32, pub z:f32, pub u:f32, pub v:f32 }

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
