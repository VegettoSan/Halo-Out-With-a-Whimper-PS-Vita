//! Controlled WASAPI starvation/recovery test; no game data.
use std::sync::{Arc, atomic::{AtomicUsize, AtomicBool, Ordering}};
use std::time::Duration;
use udon::{session::{Api, Session}, source::{Source, ChannelCount, SampleRate, Sample}};

struct Probe {
    channels: ChannelCount,
    rate: SampleRate,
    calls: Arc<AtomicUsize>,
    samples: Arc<AtomicUsize>,
    stalled: Arc<AtomicBool>,
    phase: f32,
}
impl Source for Probe {
    fn channel_count(&self) -> ChannelCount { self.channels }
    fn sample_rate(&self) -> SampleRate { self.rate }
    fn reset(&mut self) {}
    fn write_samples(&mut self, buffer: &mut [Sample]) -> usize {
        if self.calls.fetch_add(1, Ordering::Relaxed) == 40 {
            self.stalled.store(true, Ordering::Relaxed);
            std::thread::sleep(Duration::from_millis(120));
        }
        for sample in buffer.iter_mut() {
            *sample = self.phase.sin() * 0.02;
            self.phase += 0.03;
        }
        self.samples.fetch_add(buffer.len(), Ordering::Relaxed);
        buffer.len()
    }
}
fn main() {
    let session = Session::new(Api::SoundIo).unwrap();
    let device = session.default_output_device().unwrap();
    let calls = Arc::new(AtomicUsize::new(0));
    let samples = Arc::new(AtomicUsize::new(0));
    let stalled = Arc::new(AtomicBool::new(false));
    let source = Probe { channels: device.channel_count(), rate: device.sample_rate(),
        calls: calls.clone(), samples: samples.clone(), stalled: stalled.clone(), phase: 0.0 };
    std::thread::spawn(move || {
        std::thread::sleep(Duration::from_secs(3));
        let first = samples.load(Ordering::Relaxed);
        eprintln!("RECOVERY first_samples={} stalled={}", first, stalled.load(Ordering::Relaxed));
        std::thread::sleep(Duration::from_secs(3));
        let second = samples.load(Ordering::Relaxed);
        let pass = stalled.load(Ordering::Relaxed) && second > first;
        eprintln!("RECOVERY second_samples={} calls={} result={}", second, calls.load(Ordering::Relaxed),
            if pass { "PASS" } else { "FAIL" });
        std::process::exit(if pass { 0 } else { 1 });
    });
    let stream = session.open_output_stream(device).unwrap();
    stream.play(source).unwrap();
}
