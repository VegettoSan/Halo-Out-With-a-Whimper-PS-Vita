//! Preserve the original triangle fan's color planes while splitting UV clamps.
use super::geometry::{Vertex,quad};
#[repr(C)] #[derive(Clone,Copy,Debug)]
pub struct TintVertex {pub x:f32,pub y:f32,pub u:f32,pub v:f32,pub color:[f32;4]}
fn cuts(start:f64,len:f64,size:f64)->Vec<f64> {
    let mut out=vec![0.,1.];if len!=0. {for e in [0.5,size-0.5] {let t=(e-start)/len;if t>0. && t<1. {out.push(t);}}}out.sort_by(f64::total_cmp);out.dedup();out
}
fn clip(p:&[[f64;2]],axis:usize,edge:f64,low:bool)->Vec<[f64;2]> {
    let mut out=Vec::with_capacity(7);if p.is_empty(){return out;}
    let inside=|v:[f64;2]|if low {v[axis]>=edge}else{v[axis]<=edge};let mut a=*p.last().unwrap();
    for &b in p {if inside(a)!=inside(b) {let t=(edge-a[axis])/(b[axis]-a[axis]);out.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]);}if inside(b){out.push(b);}a=b;}out
}
pub fn vertices(origin:[f64;2],part:[f64;4],pos:[f64;2],scale:[f64;2],angle:f64,atlas:[f64;4],size:[f64;2],colors:[i32;4],alpha:f64)->Vec<TintVertex> {
    let base=quad(origin,part,pos,scale,angle,atlas);let xs=cuts(part[0],part[2],size[0]);let ys=cuts(part[1],part[3],size[1]);let mut out=Vec::with_capacity(128);
    let vertex=|t:[f64;2]| {let [x,y]=t;let weights=if x>=y {[1.-x,x-y,y,0.]}else{[1.-y,0.,x,y-x]};
        let color=std::array::from_fn(|c|if c==3 {alpha.clamp(0.,1.) as f32}else{(0..4).map(|i|weights[i]*f64::from((colors[i]>>(c*8))&255)/255.).sum::<f64>() as f32});
        TintVertex{x:base[0].x+(base[1].x-base[0].x)*x as f32+(base[5].x-base[0].x)*y as f32,y:base[0].y+(base[1].y-base[0].y)*x as f32+(base[5].y-base[0].y)*y as f32,
            u:((atlas[0]+(part[0]+part[2]*x).clamp(0.5,size[0]-0.5))/atlas[2]) as f32,v:((atlas[1]+(part[1]+part[3]*y).clamp(0.5,size[1]-0.5))/atlas[3]) as f32,color}};
    for x in xs.windows(2) {for y in ys.windows(2) {for tri in [[[0.,0.],[1.,0.],[1.,1.]],[[0.,0.],[1.,1.],[0.,1.]]] {
        let mut p=tri.to_vec();for (axis,edge,low) in [(0,x[0],true),(0,x[1],false),(1,y[0],true),(1,y[1],false)] {p=clip(&p,axis,edge,low);}
        for i in 1..p.len().saturating_sub(1) {out.extend([vertex(p[0]),vertex(p[i]),vertex(p[i+1])]);}
    }}}assert!(out.len()<=270);out
}
#[cfg(test)] mod tests {
    use super::*;
    #[test] fn arbitrary_corner_colors_and_crop_preserve_both_original_triangle_planes() {
        let v=vertices([0.,0.],[-2.,-3.,14.,17.],[100.,100.],[-1.,1.],0.,[32.,64.,256.,256.],[10.,11.],[255,65280,16711680,16777215],0.25);
        assert!(!v.is_empty() && v.len()%3==0 && v.len()<=270);assert_eq!(std::mem::size_of::<TintVertex>(),32);
        for t in v.chunks_exact(3) {
            let x=t.iter().map(|v|v.x as f64).sum::<f64>()/3.;let y=t.iter().map(|v|v.y as f64).sum::<f64>()/3.;let tx=(99.5-x)/14.;let ty=(y-99.5)/17.;
            let expected=if tx>=ty {[1.-tx,tx-ty,ty]}else{[1.-tx,ty-tx,ty]};
            for c in 0..3 {let actual=t.iter().map(|v|v.color[c] as f64).sum::<f64>()/3.;assert!((actual-expected[c]).abs()<1e-5);}
            assert!(t.iter().all(|v|v.color[3]==0.25));
            let u=t.iter().map(|v|v.u as f64).sum::<f64>()/3.;let vv=t.iter().map(|v|v.v as f64).sum::<f64>()/3.;
            assert!((u-(32.+(-2.+14.*tx).clamp(0.5,9.5))/256.).abs()<1e-5);assert!((vv-(64.+(-3.+17.*ty).clamp(0.5,10.5))/256.).abs()<1e-5);
        }
    }
}
