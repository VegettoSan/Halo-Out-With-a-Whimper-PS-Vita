//! Generated query loads on original engine/masks; not recorded native gameplay.
use gm8emulator::collision_profile as profile;
include!("collision_detail_base.rs");

fn bench<F:Fn(usize)->bool,G:Fn(usize)->bool>(label:&str,n:usize,old:F,new:G){
 for i in 0..n {assert_eq!(old(i),new(i),"{label} query={i}");}
 fn measure<F:Fn(usize)->bool>(n:usize,f:&F)->(u128,usize){let t=Instant::now();let mut a=0usize;for i in 0..n{a=a.wrapping_add((i+1)*black_box(f(black_box(i))) as usize);}(t.elapsed().as_micros(),a)}
 for round in 0..5 {let ((before,a),(after,b))=if round%2==0{(measure(n,&old),measure(n,&new))}else{let b=measure(n,&new);(measure(n,&old),b)};assert_eq!(a,b);println!("DETAIL_BENCH label={label} round={round} calls={n} before_us={before} after_us={after} checksum={a}; generated PC load,not Vita FPS");}
}
fn query(g:&Game,h:usize,n:usize,kind:usize,reference:bool)->bool{
 let i=g.room.instance_list.get(h);let x=i.x.get()+((n%40) as i32-20).into();let y=i.y.get()+((n%30) as i32-15).into();let p=n%2==0;
 match (kind,reference){
 (0,true)=>g.check_collision_point_reference(h,x,y,p),(0,false)=>g.check_collision_point(h,x,y,p),
 (1,true)=>g.check_collision_rectangle_reference(h,x.to_i32()-8,y.to_i32()-8,x.to_i32()+8,y.to_i32()+8,p),(1,false)=>g.check_collision_rectangle(h,x.to_i32()-8,y.to_i32()-8,x.to_i32()+8,y.to_i32()+8,p),
 (2,true)=>g.check_collision_ellipse_reference(h,x-8.into(),y-8.into(),x+8.into(),y+8.into(),p),(2,false)=>g.check_collision_ellipse(h,x-8.into(),y-8.into(),x+8.into(),y+8.into(),p),
 (3,true)=>g.check_collision_line_reference(h,x-8.into(),y-8.into(),x+8.into(),y+8.into(),p),(3,false)=>g.check_collision_line(h,x-8.into(),y-8.into(),x+8.into(),y+8.into(),p),_=>unreachable!()}
}
fn detail(g:&Game,handles:&[usize],sprites:&[i32]){
 profile::calibrate();profile::enabled(false);
 for kind in 0..4{for n in 0..2000{let h=handles[n%320];let i=g.room.instance_list.get(h);i.sprite_index.set(if n%19==0{-1}else{sprites[n%sprites.len()]});i.mask_index.set(if n%23==0{sprites[(n+3)%sprites.len()]}else{-1});i.image_angle.set(if n%3==0{33.into()}else{0.into()});i.image_xscale.set(if n%5==0{(-1).into()}else{1.into()});i.image_yscale.set(1.into());i.bbox_is_stale.set(n%2==0);let before=bbox(i);let expected=query(g,h,n,kind,true);let after=bbox(i);restore(i,before);assert_eq!(query(g,h,n,kind,false),expected,"kind={kind} n={n}");assert_eq!(bbox(i),after,"bbox kind={kind} n={n}");}}
 println!("QUERY_DIFFERENTIAL_PASS cases=8000 bool+bbox side effects,precise/nonprecise,stale/fresh,mask/frame/transform changes");
 let mut checks=0;
 for n in 0..200000usize {
  let v=[i32::MIN,i32::MAX,-100000,100000,0,1,-1,78,21];let x=v[n%v.len()];let y=v[(n/7)%v.len()];let ix=v[(n/11)%v.len()];let iy=v[(n/13)%v.len()];let ox=v[(n/17)%v.len()];let oy=v[(n/19)%v.len()];let sx=if n%2==0{1.}else{-1.};let sy=if n%3==0{-1.}else{1.};
  if let Some((a,b))=gm8emulator::collision_math::unit_point(x,y,ix,iy,ox,oy,sx,sy,0.,1.) {let dx=x.checked_sub(ix).unwrap();let dy=y.checked_sub(iy).unwrap();let mut fx=dx as f64;let mut fy=dy as f64;gm8emulator::util::rotate_around_center(&mut fx,&mut fy,0.,1.);let expected=((Real::from(ox)+Real::from(fx)/Real::from(sx)).floor().to_i32(),(Real::from(oy)+Real::from(fy)/Real::from(sy)).floor().to_i32());assert_eq!((a,b),expected);checks+=1;}
 }
 let c=&g.assets.sprites[sprites[0] as usize].as_ref().unwrap().colliders[0];
 for n in 0..20000 {let x=(n%150) as i32-50;let y=((n*31)%150) as i32-50;let sx=[1.,-1.,0.5,2.,0.][n%5];let sy=[1.,-1.,0.75][n%3];let angle=[0f64,0.,0.,33.,90.][n%5].to_radians();let a=if gm8emulator::collision_math::is_unit(sx,sy,angle.sin(),angle.cos()){c.check_collision_point_unit(x,y,2,-7,5,9,sx.into(),sy.into(),angle.sin(),angle.cos())}else{c.check_collision_point_precise(x,y,2,-7,5,9,sx.into(),sy.into(),angle.sin(),angle.cos())};assert_eq!(a,c.check_collision_point_precise_reference(x,y,2,-7,5,9,sx.into(),sy.into(),angle.sin(),angle.cos()));}
 println!("UNIT_TRANSFORM_PASS checked_coordinates={checks} mask_cases=20000 includes i32 wrap,overflow fallback,mirrors,scales,rotation and zero scale");
 bench("unit_pixels",1_000_000,|n|c.check_collision_point_precise_reference((n%64) as i32,(n/64%64) as i32,0,0,0,0,1.into(),1.into(),0.,1.),|n|c.check_collision_point_unit((n%64) as i32,(n/64%64) as i32,0,0,0,0,1.into(),1.into(),0.,1.));
 for (label,gap,angle) in [("sparse",100,0.),("dense",3,0.),("rotated",3,33.)] {
  for (n,&h) in handles.iter().enumerate(){let i=g.room.instance_list.get(h);i.x.set(((n%20*gap) as i32).into());i.y.set(((n/20*gap) as i32).into());i.sprite_index.set(sprites[n%sprites.len()]);i.mask_index.set(-1);i.image_angle.set(angle.into());i.image_xscale.set(1.into());i.image_yscale.set(1.into());i.solid.set(n%9==0);i.bbox_is_stale.set(true);i.update_bbox(g.assets.sprites[i.sprite_index.get() as usize].as_deref());}
  let n=3200;profile::reset();profile::enabled(true);
  for j in 0..n {let h=handles[j%handles.len()];let target=handles[(j*17+71)%handles.len()];let i=g.room.instance_list.get(h);let x=i.x.get()+Real::from((j%40) as i32-20);let y=i.y.get()+Real::from((j%30) as i32-15);black_box(g.check_collision(h,target));black_box(g.check_collision_point(h,x,y,true));black_box(g.check_collision_line(h,x-8.into(),y-8.into(),x+8.into(),y+8.into(),true));black_box(g.check_collision_rectangle(h,x.to_i32()-8,y.to_i32()-8,x.to_i32()+8,y.to_i32()+8,true));black_box(g.check_collision_ellipse(h,x-8.into(),y-8.into(),x+8.into(),y+8.into(),true));}
  profile::report(label);profile::enabled(false);
  bench(&format!("{label}_pair_320"),102400,|j|g.check_collision_reference(handles[j/320],handles[j%320]),|j|g.check_collision(handles[j/320],handles[j%320]));
  bench(&format!("{label}_point"),n*10,|j|{let h=handles[j%320];let i=g.room.instance_list.get(h);g.check_collision_point_reference(h,i.x.get()+((j%40) as i32-20).into(),i.y.get(),true)},|j|{let h=handles[j%320];let i=g.room.instance_list.get(h);g.check_collision_point(h,i.x.get()+((j%40) as i32-20).into(),i.y.get(),true)});
  bench(&format!("{label}_rectangle"),n*10,|j|{let h=handles[j%320];let i=g.room.instance_list.get(h);let x=i.x.get().to_i32();let y=i.y.get().to_i32();g.check_collision_rectangle_reference(h,x-8,y-8,x+8,y+8,true)},|j|{let h=handles[j%320];let i=g.room.instance_list.get(h);let x=i.x.get().to_i32();let y=i.y.get().to_i32();g.check_collision_rectangle(h,x-8,y-8,x+8,y+8,true)});
  bench(&format!("{label}_ellipse"),n*10,|j|{let h=handles[j%320];let i=g.room.instance_list.get(h);g.check_collision_ellipse_reference(h,i.x.get()-8.into(),i.y.get()-8.into(),i.x.get()+8.into(),i.y.get()+8.into(),true)},|j|{let h=handles[j%320];let i=g.room.instance_list.get(h);g.check_collision_ellipse(h,i.x.get()-8.into(),i.y.get()-8.into(),i.x.get()+8.into(),i.y.get()+8.into(),true)});
  bench(&format!("{label}_line"),n*10,|j|{let h=handles[j%320];let i=g.room.instance_list.get(h);g.check_collision_line_reference(h,i.x.get()-8.into(),i.y.get()-8.into(),i.x.get()+8.into(),i.y.get()+8.into(),true)},|j|{let h=handles[j%320];let i=g.room.instance_list.get(h);g.check_collision_line(h,i.x.get()-8.into(),i.y.get()-8.into(),i.x.get()+8.into(),i.y.get()+8.into(),true)});
  bench(&format!("{label}_solid"),320,|j|g.check_collision_solid_reference(handles[j]).is_some(),|j|g.check_collision_solid(handles[j]).is_some());
  bench(&format!("{label}_any"),320,|j|g.check_collision_any_reference(handles[j]).is_some(),|j|g.check_collision_any(handles[j]).is_some());
 }
 println!("COLLISION_DETAIL_PASS 320objects,queries and transitive original masks; no Game::frame/input/GML events synthesized");
}
