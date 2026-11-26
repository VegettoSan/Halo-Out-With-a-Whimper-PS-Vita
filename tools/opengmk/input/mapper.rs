//! Pure physical-snapshot mapping. It never polls/fabricates a device.
use crate::input::Input;
pub const SELECT:u32=1;pub const START:u32=8;
pub const UP:u32=16;pub const RIGHT:u32=32;pub const DOWN:u32=64;pub const LEFT:u32=128;
pub const L:u32=256;pub const R:u32=512;pub const TRIANGLE:u32=4096;pub const CIRCLE:u32=8192;pub const CROSS:u32=16384;pub const SQUARE:u32=32768;
#[derive(Clone,Copy)] pub struct Sample {pub buttons:u32,pub axes:[u8;4],pub touch:Option<[f64;2]>}
pub struct Mapper {held:[bool;256],mouse:[bool;3],cursor:[f64;2]}
impl Default for Mapper {fn default()->Self {Self{held:[false;256],mouse:[false;3],cursor:[320.,162.]}}}
impl Mapper {
    pub fn apply(&mut self,input:&mut Input,s:Sample,dt:f64,size:[u32;2])->usize {
        let mut next=[false;256];let b=s.buttons;let [lx,ly,rx,ry]=s.axes;
        let mut key=|vk:usize,on:bool| {next[vk]|=on;};
        // D-pad arrows; left stick also supplies original WASD movement.
        for (vk,on) in [(37,b&LEFT!=0),(38,b&UP!=0),(39,b&RIGHT!=0),(40,b&DOWN!=0),
            (65,lx<80),(68,lx>176),(87,ly<80),(83,ly>176),
            (13,b&START!=0),(27,b&SELECT!=0),(32,b&CIRCLE!=0),
            (82,b&SQUARE!=0),(69,b&TRIANGLE!=0),(16,b&L!=0)] {key(vk,on);}
        let axis=|v:u8| {let n=f64::from(v)-128.;if n.abs()<=24.{0.}else{n.signum()*(n.abs()-24.)/103.}};
        if let Some([px,py])=s.touch {
            // Touch is in physical-display coordinates; undo the actual aspect viewport.
            let scale=(960./size[0] as f64).min(544./size[1] as f64);
            self.cursor=[(px-(960.-size[0] as f64*scale)/2.)/scale,(py-(544.-size[1] as f64*scale)/2.)/scale];
        } else {
            self.cursor[0]+=axis(rx)*500.*dt.clamp(0.,0.1);
            self.cursor[1]+=axis(ry)*500.*dt.clamp(0.,0.1);
        }
        self.cursor[0]=self.cursor[0].clamp(0.,size[0].saturating_sub(1) as f64);
        self.cursor[1]=self.cursor[1].clamp(0.,size[1].saturating_sub(1) as f64);
        input.mouse_step();input.mouse_move_to((self.cursor[0].round() as i32,self.cursor[1].round() as i32));
        let mut changes=0;
        for vk in 0..256 {if self.held[vk]!=next[vk] {changes+=1;if next[vk]{input.button_press(vk as u8,true);}else{input.button_release(vk as u8,true);}}}
        let mouse=[b&CROSS!=0 || s.touch.is_some(),b&R!=0,false];
        for i in 0..3 {if mouse[i]!=self.mouse[i] {changes+=1;if mouse[i]{input.mouse_press(i as i8+1,true);}else{input.mouse_release(i as i8+1,true);}}}
        self.held=next;self.mouse=mouse;changes
    }
}
