//! Actual original-engine CPU collision fixture, not native events or fabricated frames.
use gm8emulator::{game::{Game,PlayType,GetAsset},instance::Instance,diagnostics,probe_sha256,math::Real};
use std::{hint::black_box,time::Instant};
fn bbox(i:&Instance)->[i32;5] {[i.bbox_left.get(),i.bbox_right.get(),i.bbox_top.get(),i.bbox_bottom.get(),i.bbox_is_stale.get() as i32]}
fn restore(i:&Instance,b:[i32;5]){i.bbox_left.set(b[0]);i.bbox_right.set(b[1]);i.bbox_top.set(b[2]);i.bbox_bottom.set(b[3]);i.bbox_is_stale.set(b[4]!=0);}
fn main(){
 let input=std::path::PathBuf::from(std::env::args_os().nth(1).unwrap()).canonicalize().unwrap();let temp=std::path::PathBuf::from(std::env::args_os().nth(2).unwrap());std::fs::create_dir(&temp).unwrap();let temp=temp.canonicalize().unwrap();diagnostics::open(&temp).unwrap();
 let mut bytes=std::fs::read(&input).unwrap();assert_eq!(probe_sha256::digest(&bytes),"cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f");let assets=gm8exe::reader::from_exe(&mut bytes,None::<fn(&str)>,true,false).unwrap();drop(bytes);
 let mut g=Game::launch(assets,input,vec![],Some(temp.join("profile")),encoding_rs::WINDOWS_1252,true,0,false,PlayType::Normal).unwrap();
 let object=g.assets.objects.iter().position(|x|x.is_some()).unwrap();
 let sprites:Vec<i32>=g.assets.sprites.iter().enumerate().filter_map(|(n,s)|s.as_ref().filter(|s|s.width>0 && s.width<=128 && s.height>0 && s.height<=128 && !s.colliders.is_empty()).map(|_|n as i32)).collect();assert!(sprites.len()>100);
 let mut handles=Vec::new();for n in 0..320 {let inst=Instance::new(100000+n,Real::from((n%20)*100),Real::from((n/20)*100),object as i32,g.assets.objects.get_asset(object as i32).unwrap());inst.sprite_index.set(sprites[n as usize%sprites.len()]);handles.push(g.room.instance_list.insert(inst));}
 let a=handles[0];let b=handles[1];let ia=g.room.instance_list.get(a);let ib=g.room.instance_list.get(b);
 for n in 0..20000usize {
  for (j,i) in [ia,ib].into_iter().enumerate(){i.x.set((((n*17+j*13)%200) as f64-100.).into());i.y.set((((n*31+j*7)%200) as f64-100.).into());i.image_angle.set(([0.,90.,-45.,360.,33.][(n+j)%5]).into());i.image_xscale.set(([1.,-1.,2.,0.5][(n+j)%4]).into());i.image_yscale.set(([1.,-1.,0.75][(n+j)%3]).into());i.sprite_index.set(if n%19==0 {-1}else{sprites[(n*7+j*13)%sprites.len()]});i.mask_index.set(if n%23==0 {sprites[(n+j)%sprites.len()]}else{-1});i.image_index.set(((n%7) as f64-2.).into());i.bbox_is_stale.set(true);if (n+j)%2==0 {let s=g.assets.sprites.get_asset(if i.mask_index.get()<0{i.sprite_index.get()}else{i.mask_index.get()}).map(|s|s.as_ref());i.update_bbox(s);}}
  let before=[bbox(ia),bbox(ib)];let h=if n%29==0 {a}else{b};let expected=g.check_collision_reference(a,h);let after=[bbox(ia),bbox(ib)];restore(ia,before[0]);restore(ib,before[1]);assert_eq!(g.check_collision(a,h),expected,"collision n={n}");assert_eq!([bbox(ia),bbox(ib)],after,"bbox side effects n={n}");
 }
 for (n,&h) in handles.iter().enumerate(){let i=g.room.instance_list.get(h);i.x.set((((n%20)*100) as i32).into());i.y.set((((n/20)*100) as i32).into());i.sprite_index.set(sprites[n%sprites.len()]);i.mask_index.set(-1);i.bbox_is_stale.set(true);let s=g.assets.sprites.get_asset(i.sprite_index.get()).map(|s|s.as_ref());i.update_bbox(s);}
 println!("COLLISION_REGRESSION_PASS actual engine/original masks cases=20000 bool+bbox side effects including fresh/stale,mask overrides,missing sprite,self,rotation,mirrors,scales; fixture only,no events skipped");
 for round in 0..3 {let start=Instant::now();let mut old=0;for _ in 0..10 {for &a in &handles {for &b in &handles {old+=black_box(g.check_collision_reference(black_box(a),black_box(b))) as usize;}}}let before=start.elapsed().as_micros();let start=Instant::now();let mut new=0;for _ in 0..10 {for &a in &handles {for &b in &handles {new+=black_box(g.check_collision(black_box(a),black_box(b))) as usize;}}}let after=start.elapsed().as_micros();assert_eq!(old,new);println!("COLLISION_BENCH round={round} pairs=1024000 before_us={before} after_us={after} hits={old}; PC fixture grid,not native gameplay");}
 diagnostics::check().unwrap();
}
