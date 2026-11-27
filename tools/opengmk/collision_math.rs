//! Exact specialization of the original integer-point transform, no mask cache.
//! Checked subtraction falls back to preserve original overflow behavior.
#[inline]
pub fn is_unit(sx:f64,sy:f64,sin:f64,cos:f64)->bool{sin==0. && cos==1. && sx.abs()==1. && sy.abs()==1.}
#[inline(always)]
pub fn unit_point_known(x:i32,y:i32,ix:i32,iy:i32,ox:i32,oy:i32,sx:f64,sy:f64)->Option<(i32,i32)> {
    let dx=i64::from(x.checked_sub(ix)?);let dy=i64::from(y.checked_sub(iy)?);
    Some(((i64::from(ox)+if sx<0. {-dx}else{dx}) as i32,(i64::from(oy)+if sy<0. {-dy}else{dy}) as i32))
}
#[inline]
pub fn unit_point(x:i32,y:i32,ix:i32,iy:i32,ox:i32,oy:i32,sx:f64,sy:f64,sin:f64,cos:f64)->Option<(i32,i32)> {
    if !is_unit(sx,sy,sin,cos) {return None;}
    // Real::to_i32 casts f64 -> i64 -> i32, wrapping at32 bits, not saturating.
    unit_point_known(x,y,ix,iy,ox,oy,sx,sy)
}
