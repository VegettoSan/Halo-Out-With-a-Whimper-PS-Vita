//! Reject only already-current, separated boxes. Stale boxes and all overlaps
//! fall through to the untouched original sprite/pixel collision algorithm.
use crate::instance::Instance;
#[inline]
pub fn reject(a:&Instance,b:&Instance)->bool {
    !a.bbox_is_stale.get() && !b.bbox_is_stale.get() &&
    (a.bbox_right.get()<b.bbox_left.get() || b.bbox_right.get()<a.bbox_left.get() ||
     a.bbox_bottom.get()<b.bbox_top.get() || b.bbox_bottom.get()<a.bbox_top.get())
}
/// Exact first AABB used by line queries; current boxes only, no new cache.
#[inline(always)]
pub fn reject_line(i:&Instance,x1:crate::math::Real,y1:crate::math::Real,x2:crate::math::Real,y2:crate::math::Real)->bool{
 use crate::math::Real;
 !i.bbox_is_stale.get() && (Real::from(i.bbox_right.get())+Real::from(1.)<=x1.min(x2) || x1.max(x2)<Real::from(i.bbox_left.get()) || Real::from(i.bbox_bottom.get())+Real::from(1.)<=y1.min(y2) || y1.max(y2)<Real::from(i.bbox_top.get()))
}
