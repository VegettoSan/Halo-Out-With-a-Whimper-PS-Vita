//! Windows modal backend for GM8 show_message_ext. No game data or GML included.
//! The synchronous OS dialog pumps UI messages without advancing the game loop.
#![cfg(windows)]

use std::{ffi::c_void, io, ptr};

type Hwnd = *mut c_void;

#[link(name = "user32")]
extern "system" {
    fn DialogBoxIndirectParamW(
        instance: *mut c_void,
        template: *const u32,
        owner: Hwnd,
        callback: unsafe extern "system" fn(Hwnd, u32, usize, isize) -> isize,
        parameter: isize,
    ) -> isize;
    fn EndDialog(dialog: Hwnd, result: isize) -> i32;
}

unsafe extern "system" fn dialog_proc(dialog: Hwnd, message: u32, wparam: usize, _: isize) -> isize {
    match message {
        0x0110 => 1, // WM_INITDIALOG: let dialog manager set default focus.
        0x0111 => { // WM_COMMAND. Private IDs avoid IDOK/IDCANCEL collisions.
            let id = (wparam & 0xffff) as isize;
            let result = match id {
                101..=103 => id - 100,
                2 => 0, // IDCANCEL: Escape, not the second custom button.
                _ => return 0,
            };
            EndDialog(dialog, result);
            1
        }
        0x0010 => { // WM_CLOSE / titlebar X.
            EndDialog(dialog, 0);
            1
        }
        _ => 0,
    }
}

fn dword(words: &mut Vec<u16>, value: u32) {
    words.extend([value as u16, (value >> 16) as u16]);
}

fn text(words: &mut Vec<u16>, value: &str) {
    words.extend(value.encode_utf16().take_while(|c| *c != 0));
    words.push(0);
}

fn item(words: &mut Vec<u16>, style: u32, rect: [u16; 4], id: u16, class: u16, label: &str) {
    if words.len() % 2 != 0 { words.push(0); }
    dword(words, style);
    dword(words, 0);
    words.extend(rect);
    words.extend([id, 0xffff, class]);
    text(words, label);
    words.push(0); // No control creation data.
}

/// Empty labels hide that slot without renumbering the remaining buttons.
/// Errors creating a dialog are errors, never synthetic user selections.
pub fn show(owner: isize, message: &str, buttons: [&str; 3]) -> io::Result<i32> {
    let visible: Vec<_> = buttons.iter().enumerate().filter(|(_, label)| !label.is_empty()).collect();
    let button_width = buttons.iter().map(|s| s.chars().count() as u16 * 4 + 16)
        .max().unwrap_or(60).clamp(60, 180);
    let width = (visible.len() as u16 * (button_width + 6) + 18).max(300);
    let message = message.replace('#', "\r\n");
    let columns = ((width - 24) / 4).max(1) as usize;
    let lines = message.lines().map(|line| (line.chars().count().max(1) + columns - 1) / columns)
        .sum::<usize>().max(1).min(45) as u16;
    let text_height = lines * 10 + 8;
    let height = text_height + 46;
    let mut words = Vec::new();
    // DLGTEMPLATE: modal frame, centered, system font, caption and close box.
    dword(&mut words, 0x80c8_08c0);
    dword(&mut words, 0);
    words.extend([visible.len() as u16 + 1, 0, 0, width, height, 0, 0]);
    text(&mut words, "OpenGMK");
    words.push(9);
    text(&mut words, "Segoe UI");
    item(&mut words, 0x5000_0080, [12, 10, width - 24, text_height], 0xffff, 0x82, &message);
    let row_width = visible.len() as u16 * (button_width + 6);
    let x = (width - row_width) / 2;
    for (position, (slot, label)) in visible.iter().enumerate() {
        let default = if position == 0 { 1 } else { 0 };
        item(&mut words, 0x5001_0000 | default,
             [x + position as u16 * (button_width + 6), text_height + 20, button_width, 16],
             101 + *slot as u16, 0x80, label);
    }
    if words.len() % 2 != 0 { words.push(0); }
    // Vec<u32> guarantees the DWORD alignment required by DialogBoxIndirectParamW.
    let aligned: Vec<u32> = words.chunks_exact(2).map(|p| p[0] as u32 | ((p[1] as u32) << 16)).collect();
    let result = unsafe {
        DialogBoxIndirectParamW(ptr::null_mut(), aligned.as_ptr(), owner as Hwnd, dialog_proc, 0)
    };
    match result {
        0..=3 => Ok(result as i32),
        _ => Err(io::Error::last_os_error()),
    }
}
