//! CPU geometry shared by the real backend and bounded contract tests.
#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct Vertex { pub x:f32, pub y:f32, pub z:f32, pub u:f32, pub v:f32 }
#[repr(C)]
#[derive(Clone,Copy,Debug,Default)]
pub struct ColorVertex {pub x:f32,pub y:f32,pub z:f32,pub color:u32}
pub fn line(x1:f64,y1:f64,x2:f64,y2:f64,width:Option<f64>,c1:i32,c2:i32,alpha:f64)->Vec<ColorVertex> {
    let point=|x:f64,y:f64,c|ColorVertex{x:x as f32,y:y as f32,z:0.5,color:tint(c,alpha)};
    if let Some(w)=width {let len=(x2-x1).hypot(y2-y1);if len==0. {return vec![];}
        let dx=(y2-y1)*w/2./len;let dy=(x2-x1)*w/2./len;
        let v=[point(x1-dx,y1+dy,c1),point(x1+dx,y1-dy,c1),point(x2+dx,y2-dy,c2),point(x2-dx,y2+dy,c2)];
        vec![v[0],v[1],v[2],v[0],v[2],v[3]]
    } else {vec![point(x1,y1,c1),point(x2,y2,c2)]}
}
pub fn ellipse(x:f64,y:f64,rx:f64,ry:f64,c1:i32,c2:i32,alpha:f64,outline:bool,precision:i32)->Vec<ColorVertex> {
    let edge=|i:i32|{let a=f64::from(i)*std::f64::consts::TAU/f64::from(precision);ColorVertex{x:(x+rx*a.cos()) as f32,y:(y+ry*a.sin()) as f32,z:0.5,color:tint(c2,alpha)}};
    let center=ColorVertex{x:x as f32,y:y as f32,z:0.5,color:tint(c1,alpha)};let mut out=Vec::with_capacity(precision as usize*3);
    for i in 0..precision {if !outline {out.push(center);}out.extend([edge(i),edge(i+1)]);}out
}

pub fn rectangle(x1:f64,y1:f64,x2:f64,y2:f64,colors:[i32;4],alpha:f64)->[ColorVertex;6] {
    let (left,right)=(x1.min(x2),x1.max(x2));let (top,bottom)=(y1.min(y2),y1.max(y2));
    let right=if right==right.floor(){right+0.01}else{right};
    let bottom=if bottom==bottom.floor(){bottom+0.01}else{bottom};
    let v=[(left,top),(right,top),(right,bottom),(left,bottom)].map(|(x,y)|ColorVertex{x:x as f32,y:y as f32,z:0.5,color:0});
    let v=std::array::from_fn::<_,4,_>(|i|ColorVertex{color:tint(colors[i],alpha),..v[i]});
    [v[0],v[1],v[2],v[0],v[2],v[3]]
}
pub fn rectangle_outline(x1:f64,y1:f64,x2:f64,y2:f64,colors:[i32;4],alpha:f64)->[ColorVertex;8] {
    let v=rectangle(x1,y1,x2,y2,colors,alpha);
    [v[0],v[1],v[1],v[2],v[2],v[5],v[5],v[0]]
}

pub fn aspect_view(w:u32,h:u32)->(f64,[f64;2]) {
    assert!(w>0 && h>0);
    let scale=(960.0/w as f64).min(544.0/h as f64);
    (scale,[(960.-w as f64*scale)/2.,(544.-h as f64*scale)/2.])
}
pub fn shader_view(w:u32,h:u32)->[f64;2] {assert!(w>0 && h>0);[960./w as f64,544./h as f64]}
/// Conservative clip rejection only; keep boundary/straddling/rotated quads.
pub fn outside_view(v:&[Vertex],scale:[f64;2],offset:[f64;2])->bool {
    let x=|v:&Vertex|f64::from(v.x)*scale[0]+offset[0];let y=|v:&Vertex|f64::from(v.y)*scale[1]+offset[1];
    !v.is_empty() && (v.iter().all(|v|x(v)< -1.) || v.iter().all(|v|x(v)>961.) || v.iter().all(|v|y(v)< -1.) || v.iter().all(|v|y(v)>545.))
}
pub fn outside_axis_sprite(origin:[f64;2],size:[f64;2],pos:[f64;2],scale:[f64;2],view:[f64;2],offset:[f64;2])->bool {
    let w=size[0]*scale[0];let h=size[1]*scale[1];let l=-w*origin[0]-0.5;let t=-h*origin[1]-0.5;
    let x=[pos[0]+l,pos[0]+(l+w)].map(|v|f64::from(v as f32)*view[0]+offset[0]);let y=[pos[1]+t,pos[1]+(t+h)].map(|v|f64::from(v as f32)*view[1]+offset[1]);
    x.iter().all(|v|*v< -1.) || x.iter().all(|v|*v>961.) || y.iter().all(|v|*v< -1.) || y.iter().all(|v|*v>545.)
}
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
    let (sin,cos)=if angle==0. {(-angle,1.)}else{(-angle.to_radians()).sin_cos()};
    let left=-pw*scale[0]*origin[0]-0.5;
    let top=-ph*scale[1]*origin[1]-0.5;
    let corners=[(left,top,px,py),(left+pw*scale[0],top,px+pw,py),
        (left+pw*scale[0],top+ph*scale[1],px+pw,py+ph),(left,top+ph*scale[1],px,py+ph)];
    let v=corners.map(|(x,y,u,v)| Vertex {x:(position[0]+x*cos-y*sin) as f32,
        y:(position[1]+y*cos+x*sin) as f32,z:0.5,u:((ax+u)/aw) as f32,v:((ay+v)/ah) as f32});
    [v[0],v[1],v[2],v[0],v[2],v[3]]
}

/// Match the original non-repeating shader's per-sprite edge clamp. Splitting
/// at the clamp boundaries preserves the interior UV slope, including reversed
/// source extents; merely clamping four corner UVs would stretch the image.
pub fn clamped_quads(origin:[f64;2],part:[f64;4],position:[f64;2],scale:[f64;2],angle:f64,atlas:[f64;4],sprite:[f64;2])->([Vertex;54],usize) {
    fn cuts(start:f64,length:f64,size:f64)->([f64;4],usize) {
        let mut t=[0.,1.,0.,0.];let mut n=2;
        if length!=0. {for edge in [0.5,size-0.5] {let v=(edge-start)/length;if v>0. && v<1. {t[n]=v;n+=1;}}}
        t[..n].sort_by(f64::total_cmp);(t,n)
    }
    let [px,py,pw,ph]=part;let [ax,ay,aw,ah]=atlas;
    let (xs,nx)=cuts(px,pw,sprite[0]);let(ys,ny)=cuts(py,ph,sprite[1]);
    let (sin,cos)=(-angle.to_radians()).sin_cos();let width=pw*scale[0];let height=ph*scale[1];
    let left=-width*origin[0]-0.5;let top=-height*origin[1]-0.5;
    let point=|tx:f64,ty:f64| {let x=left+width*tx;let y=top+height*ty;
        Vertex{x:(position[0]+x*cos-y*sin) as f32,y:(position[1]+y*cos+x*sin) as f32,z:0.5,
            u:((ax+(px+pw*tx).clamp(0.5,sprite[0]-0.5))/aw) as f32,
            v:((ay+(py+ph*ty).clamp(0.5,sprite[1]-0.5))/ah) as f32}};
    let mut out=[Vertex::default();54];let mut n=0;
    for y in ys[..ny].windows(2) {for x in xs[..nx].windows(2) {
        let v=[point(x[0],y[0]),point(x[1],y[0]),point(x[1],y[1]),point(x[0],y[1])];
        out[n..n+6].copy_from_slice(&[v[0],v[1],v[2],v[0],v[2],v[3]]);n+=6;
    }}(out,n)
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
    #[test] fn line_width_colors_degenerate_and_ellipse_topology() {
        let v=line(10.,10.,30.,10.,Some(20.),1,2,0.5);assert_eq!(v.len(),6);assert_eq!((v[0].x,v[0].y,v[0].color),(10.,20.,0x7f000001));assert_eq!((v[2].x,v[2].y,v[2].color),(30.,0.,0x7f000002));
        assert!(line(0.,0.,0.,0.,Some(10.),0,0,1.).is_empty());assert_eq!(line(0.,0.,1.,1.,None,0,1,1.).len(),2);
        let fill=ellipse(10.,20.,3.,4.,1,2,1.,false,24);assert_eq!(fill.len(),72);assert_eq!((fill[0].x,fill[0].y,fill[0].color),(10.,20.,0xff000001));
        let edge=ellipse(10.,20.,3.,4.,1,2,1.,true,24);assert_eq!(edge.len(),48);assert!((edge[0].x-edge[47].x).abs()<1e-5 && (edge[0].y-edge[47].y).abs()<1e-5);
    }
    #[test] fn clip_rejection_keeps_crossing_rotated_and_camera_visible_quads() {
        let q=|x,y,w,h,angle|quad([0.,0.],[0.,0.,w,h],[x,y],[1.,1.],angle,[0.,0.,2048.,2048.]);
        assert!(outside_view(&q(-100.,100.,10.,10.,0.),[1.,1.],[0.,0.]));
        assert!(outside_view(&q(100.,800.,10.,10.,45.),[1.,1.],[0.,0.]));
        assert!(!outside_view(&q(-50.,100.,200.,10.,0.),[1.,1.],[0.,0.]));
        assert!(!outside_view(&q(-10.,100.,200.,10.,-45.),[1.,1.],[0.,0.]));
        assert!(!outside_view(&q(1200.,100.,20.,20.,0.),[1.5,544./325.],[-1200.*1.5,0.]));
        assert!(!outside_view(&q(960.,544.,1.,1.,0.),[1.,1.],[0.,0.]));
    }
    #[test] fn outline_is_closed_and_retains_original_endpoints_and_colors() {
        let v=rectangle_outline(20.,30.,10.,5.,[1,2,3,4],0.5);
        assert_eq!((v[0].x,v[0].y,v[0].color),(10.,5.,0x7f000001));
        assert_eq!((v[3].x,v[3].y,v[3].color),(20.01,30.01,0x7f000003));
        assert_eq!((v[7].x,v[7].y,v[7].color),(v[0].x,v[0].y,v[0].color));
    }
    #[test] fn outside_crop_clamps_edges_without_stretching_interior_or_losing_reversal() {
        for (part,scale) in [([-2.,-3.,14.,17.],[1.,1.]),([12.,14.,-14.,-17.],[-1.,1.])] {
            let (v,n)=clamped_quads([0.,0.],part,[100.,100.],scale,0.,[32.,64.,256.,256.],[10.,11.]);
            assert!(n<=54 && n%6==0);
            // Sample triangle centroids: affine UV interpolation must equal the
            // original fragment shader's clamp at that actual screen position.
            for tri in v[..n].chunks_exact(3) {
                let x=tri.iter().map(|v|v.x as f64).sum::<f64>()/3.;let y=tri.iter().map(|v|v.y as f64).sum::<f64>()/3.;
                let u=tri.iter().map(|v|v.u as f64).sum::<f64>()/3.;let vv=tri.iter().map(|v|v.v as f64).sum::<f64>()/3.;
                let expected_u=(32.+(part[0]+(x-99.5)/scale[0]).clamp(0.5,9.5))/256.;
                let expected_v=(64.+(part[1]+(y-99.5)/scale[1]).clamp(0.5,10.5))/256.;
                assert!((u-expected_u).abs()<1e-6 && (vv-expected_v).abs()<1e-6);
            }
        }
    }
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
