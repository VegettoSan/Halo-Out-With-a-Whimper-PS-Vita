//! Real OpenGMK reader/parser and independent engine modules; no game replacement.
//! Prepared beside the upstream crates by prepare_native_probe.py.
#![allow(dead_code)]
#[path = "../gm8emulator/src/math.rs"]
mod math;
#[path = "../gm8emulator/src/gml/rand.rs"]
mod random;
#[path = "../gm8emulator/src/render/atlas.rs"]
mod atlas;

use std::{alloc::{GlobalAlloc, Layout, System}, sync::atomic::{AtomicUsize, Ordering}};

// Requested allocation bytes only: excludes allocator overhead, stack and GPU.
struct Meter;
static LIVE: AtomicUsize = AtomicUsize::new(0);
static PEAK: AtomicUsize = AtomicUsize::new(0);
fn add(n: usize) {
    let live = LIVE.fetch_add(n, Ordering::Relaxed) + n;
    PEAK.fetch_max(live, Ordering::Relaxed);
}
unsafe impl GlobalAlloc for Meter {
    unsafe fn alloc(&self, l: Layout) -> *mut u8 {
        let p = System.alloc(l);
        if !p.is_null() { add(l.size()); }
        p
    }
    unsafe fn alloc_zeroed(&self, l: Layout) -> *mut u8 {
        let p = System.alloc_zeroed(l);
        if !p.is_null() { add(l.size()); }
        p
    }
    unsafe fn dealloc(&self, p: *mut u8, l: Layout) {
        System.dealloc(p, l);
        LIVE.fetch_sub(l.size(), Ordering::Relaxed);
    }
    unsafe fn realloc(&self, p: *mut u8, l: Layout, n: usize) -> *mut u8 {
        let q = System.realloc(p, l, n);
        if !q.is_null() {
            LIVE.fetch_sub(l.size(), Ordering::Relaxed);
            add(n);
        }
        q
    }
}
#[global_allocator]
static ALLOCATOR: Meter = Meter;

#[derive(Default)]
struct Syntax { units: usize, failures: usize, source_bytes: usize, statements: usize }
impl Syntax {
    fn check(&mut self, code: &[u8]) {
        if code.is_empty() { return; }
        self.units += 1;
        self.source_bytes += code.len();
        match gml_parser::ast::AST::new(code) {
            Ok(ast) => self.statements += ast.len(),
            Err(_) => self.failures += 1, // Never dump private code or parser messages.
        }
    }
}
fn count<T>(v: &gm8exe::AssetList<T>) -> usize { v.iter().flatten().count() }

fn run() -> Result<(), Box<dyn std::error::Error>> {
    #[cfg(not(target_os = "vita"))]
    let path = std::env::args_os().nth(1).ok_or("supply a private copied EXE path")?;
    #[cfg(target_os = "vita")]
    let path = std::ffi::OsString::from("ux0:data/howaw/HOWaW_FirefightDemov1.exe");
    let mut exe = std::fs::read(path)?;
    if exe.len() != 18_142_424 { return Err("unexpected input size; verify baseline SHA-256 before running".into()); }
    // Strict format checks; serial path avoids requiring a Rayon worker pool.
    let assets = gm8exe::reader::from_exe(&mut exe, None::<fn(&str)>, true, false)?;
    println!("strict_load=PASS version={:?}", assets.version);
    println!("sprites={} sounds={} backgrounds={} scripts={} objects={} rooms={} fonts={}",
        count(&assets.sprites), count(&assets.sounds), count(&assets.backgrounds),
        count(&assets.scripts), count(&assets.objects), count(&assets.rooms), count(&assets.fonts));
    println!("loader_requested_peak_bytes={} loader_requested_live_bytes={}",
        PEAK.load(Ordering::Relaxed), LIVE.load(Ordering::Relaxed));
    drop(exe);
    let sprite_bytes: usize = assets.sprites.iter().flatten().flat_map(|s| &s.frames).map(|f| f.data.len()).sum();
    let mask_bytes: usize = assets.sprites.iter().flatten().flat_map(|s| &s.colliders).map(|c| c.data.len()).sum();
    let background_bytes: usize = assets.backgrounds.iter().flatten().filter_map(|b| b.data.as_ref()).map(|d| d.len()).sum();
    let sound_bytes: usize = assets.sounds.iter().flatten().filter_map(|s| s.data.as_ref()).map(|d| d.len()).sum();
    let font_alpha_bytes: usize = assets.fonts.iter().flatten().map(|f| f.pixel_map.len()).sum();
    println!("sprite_rgba_bytes={sprite_bytes} collision_bool_bytes={mask_bytes} background_bgra_bytes={background_bytes} encoded_sound_bytes={sound_bytes} font_alpha_bytes={font_alpha_bytes}");
    let mut syntax = Syntax::default();
    for s in assets.scripts.iter().flatten() { syntax.check(&s.source.0); }
    let script_units = syntax.units;
    for o in assets.objects.iter().flatten() {
        for events in &o.events { for (_, actions) in events { for a in actions {
            if a.action_kind == 7 { syntax.check(&a.param_strings[0].0); }
            else if a.action_kind == 0 && a.execution_type == 2 { syntax.check(&a.fn_code.0); }
        } } }
    }
    for r in assets.rooms.iter().flatten() {
        syntax.check(&r.creation_code.0);
        for i in &r.instances { syntax.check(&i.creation_code.0); }
    }
    for code in &assets.library_init_strings { syntax.check(&code.0); }
    println!("syntax_script_units={script_units} syntax_total_units={} syntax_failures={} source_bytes={} top_level_statements={}",
        syntax.units, syntax.failures, syntax.source_bytes, syntax.statements);
    // Pack original sprite/background pixels with the unchanged engine packer.
    // Move buffers, rather than adding a second decoded copy to the estimate.
    let mut builder = atlas::AtlasBuilder::new(2048);
    let mut rejected = 0;
    for s in assets.sprites.into_iter().flatten() {
        for f in s.frames {
            if builder.texture(f.width as i32, f.height as i32, s.origin_x, s.origin_y, f.data).is_none() { rejected += 1; }
        }
    }
    for b in assets.backgrounds.into_iter().flatten() {
        if let Some(data) = b.data {
            if builder.texture(b.width as i32, b.height as i32, 0, 0, data).is_none() { rejected += 1; }
        }
    }
    let (pages, textures) = builder.into_inner();
    let atlas_bytes: usize = pages.iter().map(|p| { let (w,h)=p.size(); w as usize*h as usize*4 }).sum();
    println!("atlas_limit=2048 atlas_pages={} atlas_rgba_capacity_bytes={atlas_bytes} atlas_rejected={rejected} texture_entries={}", pages.len(), textures.len());
    println!("abi_pointer_bytes={} real_bytes={} random_bytes={} atlas_rect_bytes={}",
        std::mem::size_of::<usize>(), std::mem::size_of::<math::Real>(),
        std::mem::size_of::<random::Random>(), std::mem::size_of::<atlas::AtlasRect>());
    if syntax.failures != 0 || rejected != 0 { return Err("syntax/atlas validation failed".into()); }
    println!("HEADLESS_DATA_PASS execution_of_gml=NOT_ATTEMPTED");
    Ok(())
}
fn main() {
    if let Err(e) = run() { eprintln!("HEADLESS_DATA_FAIL: {e}"); std::process::exit(1); }
}
