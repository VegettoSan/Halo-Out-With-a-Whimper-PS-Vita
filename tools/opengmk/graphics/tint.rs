//! Preserve the original triangle fan's color planes while splitting UV clamps.
use super::geometry::quad;
#[repr(C)] #[derive(Clone,Copy,Debug)]
pub struct TintVertex {pub x:f32,pub y:f32,pub u:f32,pub v:f32,pub color:[f32;4]}
fn cuts(start:f64,len:f64,size:f64)->([f64;4],usize) {
    let mut out=[0.,1.,0.,0.];let mut n=2;if len!=0. {for e in [0.5,size-0.5] {let t=(e-start)/len;if t>0. && t<1. {out[n]=t;n+=1;}}}out[..n].sort_by(f64::total_cmp);
    let mut unique=1;for i in 1..n {if out[i]!=out[unique-1] {out[unique]=out[i];unique+=1;}}(out,unique)
}
struct Poly {points:[[f64;2];16],n:usize}
impl Poly {fn empty()->Self {Self{points:[[0.;2];16],n:0}}fn push(&mut self,p:[f64;2]){assert!(self.n<16);self.points[self.n]=p;self.n+=1;}}
fn clip(p:&Poly,axis:usize,edge:f64,low:bool)->Poly {
    let mut out=Poly::empty();if p.n==0{return out;}
    let inside=|v:[f64;2]|if low {v[axis]>=edge}else{v[axis]<=edge};let mut a=p.points[p.n-1];
    for &b in &p.points[..p.n] {if inside(a)!=inside(b) {let t=(edge-a[axis])/(b[axis]-a[axis]);out.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]);}if inside(b){out.push(b);}a=b;}out
}
pub fn vertices(origin:[f64;2],part:[f64;4],pos:[f64;2],scale:[f64;2],angle:f64,atlas:[f64;4],size:[f64;2],colors:[i32;4],alpha:f64)->Vec<TintVertex> {
    let mut out=Vec::with_capacity(270);vertices_into(&mut out,origin,part,pos,scale,angle,atlas,size,colors,alpha);out
}
pub fn vertices_into(out:&mut Vec<TintVertex>,origin:[f64;2],part:[f64;4],pos:[f64;2],scale:[f64;2],angle:f64,atlas:[f64;4],size:[f64;2],colors:[i32;4],alpha:f64) {
    out.clear();let base=quad(origin,part,pos,scale,angle,atlas);let (xs,nx)=cuts(part[0],part[2],size[0]);let (ys,ny)=cuts(part[1],part[3],size[1]);
    let vertex=|t:[f64;2]| {let [x,y]=t;let weights=if x>=y {[1.-x,x-y,y,0.]}else{[1.-y,0.,x,y-x]};
        let color=std::array::from_fn(|c|if c==3 {alpha.clamp(0.,1.) as f32}else{(0..4).map(|i|weights[i]*f64::from((colors[i]>>(c*8))&255)/255.).sum::<f64>() as f32});
        TintVertex{x:base[0].x+(base[1].x-base[0].x)*x as f32+(base[5].x-base[0].x)*y as f32,y:base[0].y+(base[1].y-base[0].y)*x as f32+(base[5].y-base[0].y)*y as f32,
            u:((atlas[0]+(part[0]+part[2]*x).clamp(0.5,size[0]-0.5))/atlas[2]) as f32,v:((atlas[1]+(part[1]+part[3]*y).clamp(0.5,size[1]-0.5))/atlas[3]) as f32,color}};
    for x in xs[..nx].windows(2) {for y in ys[..ny].windows(2) {for tri in [[[0.,0.],[1.,0.],[1.,1.]],[[0.,0.],[1.,1.],[0.,1.]]] {
        let mut p=Poly::empty();for v in tri {p.push(v);}for (axis,edge,low) in [(0,x[0],true),(0,x[1],false),(1,y[0],true),(1,y[1],false)] {p=clip(&p,axis,edge,low);}
        for i in 1..p.n.saturating_sub(1) {out.extend([vertex(p.points[0]),vertex(p.points[i]),vertex(p.points[i+1])]);}
    }}}assert!(out.len()<=270);
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
