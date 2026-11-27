//! Reject only already-current, separated boxes. Stale boxes and all overlaps
//! fall through to the untouched original sprite/pixel collision algorithm.
use crate::instance::Instance;
#[inline]
pub fn reject(a:&Instance,b:&Instance)->bool {
    !a.bbox_is_stale.get() && !b.bbox_is_stale.get() &&
    (a.bbox_right.get()<b.bbox_left.get() || b.bbox_right.get()<a.bbox_left.get() ||
     a.bbox_bottom.get()<b.bbox_top.get() || b.bbox_bottom.get()<a.bbox_top.get())
}
