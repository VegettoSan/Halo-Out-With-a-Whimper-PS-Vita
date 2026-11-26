use gm8emulator::{input::Input,input_mapper::*};
fn main() {
    let mut map=Mapper::default();let mut i=Input::new();
    let idle=Sample{buttons:0,axes:[128;4],touch:None};
    map.apply(&mut i,idle,1./30.,[640,325]);assert!(!i.keyboard_check_any());
    let press=Sample{buttons:START|CROSS,axes:[0,128,128,128],touch:None};
    map.apply(&mut i,press,1./30.,[640,325]);assert!(i.keyboard_check_pressed(13)&&i.keyboard_check(65)&&i.mouse_check_button_pressed(1));
    i.step();map.apply(&mut i,press,1./30.,[640,325]);assert!(i.keyboard_check(13)&&!i.keyboard_check_pressed(13));assert!(!i.mouse_check_button_pressed(1));
    i.step();map.apply(&mut i,Sample{touch:Some([480.,272.]),..idle},1./30.,[640,325]);
    assert!(i.keyboard_check_released(13)&&i.keyboard_check_released(65));assert!(i.mouse_check_button(1)&&!i.mouse_check_button_released(1));assert_eq!((i.mouse_x(),i.mouse_y()),(320,163));
    i.step();map.apply(&mut i,idle,1./30.,[640,325]);assert!(i.mouse_check_button_released(1));
    i.step();let before=i.mouse_x();map.apply(&mut i,Sample{axes:[128,128,255,128],..idle},1./30.,[640,325]);assert!(i.mouse_x()>before);
    map.apply(&mut i,Sample{touch:Some([2000.,-500.]),..idle},1./30.,[640,325]);assert_eq!((i.mouse_x(),i.mouse_y()),(639,0));
    map.set_fill(true);map.apply(&mut i,Sample{touch:Some([480.,64.]),..idle},1./30.,[640,325]);assert_eq!((i.mouse_x(),i.mouse_y()),(320,38));
    println!("INPUT_CONTRACT_PASS engine pressed/held/released, source union, deadzone, cursor/touch aspect bounds; synthetic CPU snapshots only, no hardware claim");
}
